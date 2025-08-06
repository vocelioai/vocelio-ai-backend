"""
Event-Driven Architecture Implementation
Message bus, event sourcing, and CQRS patterns for microservices
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable, Type, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import logging
from contextlib import asynccontextmanager
import weakref

logger = logging.getLogger(__name__)

class EventPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Event:
    """Base event class"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    event_version: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        data = data.copy()
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

# Domain Events
@dataclass
class CallEvent(Event):
    """Call-related events"""
    event_type: str = "call"

@dataclass
class CallStartedEvent(CallEvent):
    """Call started event"""
    event_type: str = "call.started"

@dataclass
class CallEndedEvent(CallEvent):
    """Call ended event"""
    event_type: str = "call.ended"

@dataclass
class AgentEvent(Event):
    """Agent-related events"""
    event_type: str = "agent"

@dataclass
class AgentCreatedEvent(AgentEvent):
    """Agent created event"""
    event_type: str = "agent.created"

@dataclass
class AgentUpdatedEvent(AgentEvent):
    """Agent updated event"""
    event_type: str = "agent.updated"

@dataclass
class CampaignEvent(Event):
    """Campaign-related events"""
    event_type: str = "campaign"

@dataclass
class CampaignStartedEvent(CampaignEvent):
    """Campaign started event"""
    event_type: str = "campaign.started"

@dataclass
class CampaignStoppedEvent(CampaignEvent):
    """Campaign stopped event"""
    event_type: str = "campaign.stopped"

class EventHandler(ABC):
    """Abstract event handler"""
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle an event"""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Check if handler can handle event type"""
        pass

class EventStore:
    """Event store for event sourcing"""
    
    def __init__(self):
        self._events: Dict[str, List[Event]] = {}
        self._snapshots: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def append_events(self, aggregate_id: str, events: List[Event], expected_version: int = -1) -> None:
        """Append events to aggregate stream"""
        async with self._lock:
            if aggregate_id not in self._events:
                self._events[aggregate_id] = []
            
            current_version = len(self._events[aggregate_id])
            
            # Check optimistic concurrency
            if expected_version != -1 and current_version != expected_version:
                raise Exception(f"Concurrency conflict. Expected version {expected_version}, got {current_version}")
            
            # Append events
            for i, event in enumerate(events):
                event.event_version = current_version + i + 1
                self._events[aggregate_id].append(event)
            
            logger.info(f"Appended {len(events)} events to aggregate {aggregate_id}")
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get events for aggregate from specific version"""
        async with self._lock:
            if aggregate_id not in self._events:
                return []
            
            events = self._events[aggregate_id]
            return [e for e in events if e.event_version > from_version]
    
    async def get_all_events(self, event_types: Optional[List[str]] = None) -> List[Event]:
        """Get all events, optionally filtered by type"""
        async with self._lock:
            all_events = []
            for events in self._events.values():
                all_events.extend(events)
            
            if event_types:
                all_events = [e for e in all_events if e.event_type in event_types]
            
            return sorted(all_events, key=lambda x: x.timestamp)
    
    async def save_snapshot(self, aggregate_id: str, version: int, snapshot: Dict[str, Any]) -> None:
        """Save aggregate snapshot"""
        async with self._lock:
            self._snapshots[aggregate_id] = {
                'version': version,
                'data': snapshot,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Get latest snapshot for aggregate"""
        async with self._lock:
            return self._snapshots.get(aggregate_id)

class EventBus:
    """In-memory event bus with pub/sub pattern"""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._dead_letter_queue: List[Event] = []
        self._processing_queue = asyncio.Queue()
        self._workers: List[asyncio.Task] = []
        self._is_running = False
        self._lock = asyncio.Lock()
    
    async def start(self, num_workers: int = 5):
        """Start event bus with worker tasks"""
        self._is_running = True
        
        # Start worker tasks
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        
        logger.info(f"Event bus started with {num_workers} workers")
    
    async def stop(self):
        """Stop event bus"""
        self._is_running = False
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        
        self._workers.clear()
        logger.info("Event bus stopped")
    
    async def _worker(self, worker_id: str):
        """Event processing worker"""
        logger.info(f"Event worker {worker_id} started")
        
        while self._is_running:
            try:
                # Get event from queue (with timeout to allow graceful shutdown)
                event = await asyncio.wait_for(self._processing_queue.get(), timeout=1.0)
                
                await self._process_event(event)
                self._processing_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker {worker_id}: {str(e)}")
        
        logger.info(f"Event worker {worker_id} stopped")
    
    async def _process_event(self, event: Event):
        """Process single event"""
        handlers = self._handlers.get(event.event_type, [])
        
        if not handlers:
            logger.warning(f"No handlers for event type: {event.event_type}")
            return
        
        # Process with all handlers
        for handler in handlers:
            try:
                if handler.can_handle(event.event_type):
                    await handler.handle(event)
            except Exception as e:
                logger.error(f"Handler error for event {event.event_id}: {str(e)}")
                # Add to dead letter queue
                self._dead_letter_queue.append(event)
    
    async def publish(self, event: Event) -> None:
        """Publish event to bus"""
        if not self._is_running:
            raise Exception("Event bus is not running")
        
        # Add metadata
        event.metadata.update({
            'published_at': datetime.utcnow().isoformat(),
            'publisher': 'event_bus'
        })
        
        # Queue for processing
        await self._processing_queue.put(event)
        
        logger.debug(f"Published event: {event.event_type} ({event.event_id})")
    
    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe handler to event type"""
        async with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            
            self._handlers[event_type].append(handler)
        
        logger.info(f"Subscribed handler to event type: {event_type}")
    
    async def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe handler from event type"""
        async with self._lock:
            if event_type in self._handlers:
                try:
                    self._handlers[event_type].remove(handler)
                    if not self._handlers[event_type]:
                        del self._handlers[event_type]
                except ValueError:
                    pass
        
        logger.info(f"Unsubscribed handler from event type: {event_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            'is_running': self._is_running,
            'num_workers': len(self._workers),
            'queue_size': self._processing_queue.qsize(),
            'dead_letter_count': len(self._dead_letter_queue),
            'handler_types': list(self._handlers.keys()),
            'total_handlers': sum(len(handlers) for handlers in self._handlers.values())
        }

class Aggregate(ABC):
    """Base aggregate for event sourcing"""
    
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._uncommitted_events: List[Event] = []
    
    @abstractmethod
    def apply_event(self, event: Event) -> None:
        """Apply event to aggregate state"""
        pass
    
    def raise_event(self, event: Event) -> None:
        """Raise new event"""
        event.aggregate_id = self.aggregate_id
        event.aggregate_type = self.__class__.__name__
        self._uncommitted_events.append(event)
    
    def get_uncommitted_events(self) -> List[Event]:
        """Get uncommitted events"""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self) -> None:
        """Mark events as committed"""
        self._uncommitted_events.clear()
    
    def load_from_history(self, events: List[Event]) -> None:
        """Load aggregate from event history"""
        for event in events:
            self.apply_event(event)
            self.version = event.event_version

class Repository(ABC):
    """Base repository for aggregates"""
    
    def __init__(self, event_store: EventStore, event_bus: EventBus):
        self.event_store = event_store
        self.event_bus = event_bus
    
    @abstractmethod
    def create_aggregate(self, aggregate_id: str) -> Aggregate:
        """Create new aggregate instance"""
        pass
    
    async def get(self, aggregate_id: str) -> Optional[Aggregate]:
        """Get aggregate by ID"""
        # Try to get snapshot first
        snapshot = await self.event_store.get_snapshot(aggregate_id)
        
        if snapshot:
            # Load from snapshot
            aggregate = self.create_aggregate(aggregate_id)
            aggregate.version = snapshot['version']
            # Apply snapshot data to aggregate (implementation specific)
            
            # Get events after snapshot
            events = await self.event_store.get_events(aggregate_id, snapshot['version'])
        else:
            # Load from beginning
            aggregate = self.create_aggregate(aggregate_id)
            events = await self.event_store.get_events(aggregate_id)
        
        if not events and not snapshot:
            return None
        
        # Apply events
        aggregate.load_from_history(events)
        
        return aggregate
    
    async def save(self, aggregate: Aggregate) -> None:
        """Save aggregate"""
        uncommitted_events = aggregate.get_uncommitted_events()
        
        if not uncommitted_events:
            return
        
        # Save to event store
        await self.event_store.append_events(
            aggregate.aggregate_id,
            uncommitted_events,
            aggregate.version
        )
        
        # Publish events
        for event in uncommitted_events:
            await self.event_bus.publish(event)
        
        # Mark as committed
        aggregate.mark_events_as_committed()
        aggregate.version += len(uncommitted_events)

# CQRS Implementation
class Query(ABC):
    """Base query class for CQRS"""
    pass

class QueryHandler(ABC):
    """Base query handler for CQRS"""
    
    @abstractmethod
    async def handle(self, query: Query) -> Any:
        """Handle query"""
        pass

class Command(ABC):
    """Base command class for CQRS"""
    pass

class CommandHandler(ABC):
    """Base command handler for CQRS"""
    
    @abstractmethod
    async def handle(self, command: Command) -> Any:
        """Handle command"""
        pass

class CQRS:
    """Command Query Responsibility Segregation"""
    
    def __init__(self):
        self._command_handlers: Dict[Type[Command], CommandHandler] = {}
        self._query_handlers: Dict[Type[Query], QueryHandler] = {}
    
    def register_command_handler(self, command_type: Type[Command], handler: CommandHandler):
        """Register command handler"""
        self._command_handlers[command_type] = handler
    
    def register_query_handler(self, query_type: Type[Query], handler: QueryHandler):
        """Register query handler"""
        self._query_handlers[query_type] = handler
    
    async def execute_command(self, command: Command) -> Any:
        """Execute command"""
        command_type = type(command)
        handler = self._command_handlers.get(command_type)
        
        if not handler:
            raise Exception(f"No handler registered for command: {command_type.__name__}")
        
        return await handler.handle(command)
    
    async def execute_query(self, query: Query) -> Any:
        """Execute query"""
        query_type = type(query)
        handler = self._query_handlers.get(query_type)
        
        if not handler:
            raise Exception(f"No handler registered for query: {query_type.__name__}")
        
        return await handler.handle(query)

# Global instances
event_store = EventStore()
event_bus = EventBus()
cqrs = CQRS()

# Utility functions
async def publish_event(event: Event) -> None:
    """Publish event to global event bus"""
    await event_bus.publish(event)

@asynccontextmanager
async def event_bus_context():
    """Context manager for event bus lifecycle"""
    await event_bus.start()
    try:
        yield event_bus
    finally:
        await event_bus.stop()

# Decorators
def event_handler(event_type: str):
    """Decorator to mark function as event handler"""
    def decorator(func):
        class FunctionHandler(EventHandler):
            async def handle(self, event: Event) -> None:
                await func(event)
            
            def can_handle(self, event_type_check: str) -> bool:
                return event_type_check == event_type
        
        # Auto-register handler
        handler = FunctionHandler()
        asyncio.create_task(event_bus.subscribe(event_type, handler))
        
        return func
    return decorator
