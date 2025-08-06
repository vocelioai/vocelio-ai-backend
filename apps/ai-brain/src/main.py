"""
AI Brain Service - Vocelio Backend
Natural Language Processing, AI reasoning, and intelligent conversation management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
import os
from contextlib import asynccontextmanager
import random
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

class IntentType(str, Enum):
    GREETING = "greeting"
    INQUIRY = "inquiry"
    COMPLAINT = "complaint"
    BOOKING = "booking"
    SUPPORT = "support"
    SALES = "sales"
    OBJECTION = "objection"
    CLOSING = "closing"
    ESCALATION = "escalation"
    UNKNOWN = "unknown"

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class EmotionType(str, Enum):
    JOY = "joy"
    ANGER = "anger"
    FEAR = "fear"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"

class LanguageCode(str, Enum):
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    ZH = "zh"
    JA = "ja"
    KO = "ko"
    AR = "ar"

class AIModelType(str, Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-3"
    LLAMA = "llama-2"
    GEMINI = "gemini-pro"
    CUSTOM = "custom"

class ConversationState(str, Enum):
    STARTING = "starting"
    ACTIVE = "active"
    WAITING = "waiting"
    TRANSFERRING = "transferring"
    ENDING = "ending"
    COMPLETED = "completed"
    FAILED = "failed"

# Pydantic Models
class TextAnalysisRequest(BaseModel):
    text: str
    language: Optional[LanguageCode] = LanguageCode.EN
    include_sentiment: bool = True
    include_intent: bool = True
    include_entities: bool = True
    include_emotions: bool = False
    
    @validator('text')
    def validate_text(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Text cannot be empty')
        if len(v) > 10000:
            raise ValueError('Text cannot exceed 10,000 characters')
        return v.strip()

class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int
    confidence: float

class Intent(BaseModel):
    name: IntentType
    confidence: float
    parameters: Dict[str, Any] = {}

class Sentiment(BaseModel):
    label: SentimentType
    score: float
    confidence: float

class Emotion(BaseModel):
    emotion: EmotionType
    intensity: float

class TextAnalysisResponse(BaseModel):
    text: str
    language: LanguageCode
    language_confidence: float
    sentiment: Optional[Sentiment] = None
    intent: Optional[Intent] = None
    entities: List[Entity] = []
    emotions: List[Emotion] = []
    keywords: List[str] = []
    summary: Optional[str] = None

class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    agent_id: str
    context: Optional[Dict[str, Any]] = None
    model: AIModelType = AIModelType.GPT35
    temperature: float = 0.7
    max_tokens: int = 150
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0.0 or v > 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v

class ConversationResponse(BaseModel):
    conversation_id: str
    message: str
    response: str
    intent: Intent
    sentiment: Sentiment
    suggested_actions: List[str] = []
    confidence: float
    processing_time: float
    model_used: AIModelType
    context_updated: Dict[str, Any] = {}

class ConversationContext(BaseModel):
    conversation_id: str
    agent_id: str
    state: ConversationState
    messages: List[Dict[str, Any]] = []
    customer_info: Dict[str, Any] = {}
    session_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class KnowledgeBase(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = []
    confidence_threshold: float = 0.8
    created_at: datetime
    updated_at: datetime

class SmartReply(BaseModel):
    text: str
    intent: IntentType
    confidence: float
    tone: str = "professional"

class ConversationInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    recommendations: List[str]
    confidence: float
    data: Dict[str, Any]

# Global state (In production, use proper database and AI APIs)
conversations_db = {}
knowledge_base_db = {}
ai_models_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 AI Brain Service starting up...")
    
    # Initialize sample data
    await initialize_sample_data()
    
    yield
    
    logger.info("💤 AI Brain Service shutting down...")

app = FastAPI(
    title="AI Brain Service",
    description="Natural Language Processing, AI reasoning, and intelligent conversation management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token"""
    # In production, implement proper JWT validation
    if credentials.credentials == "demo-token":
        return {"id": "user123", "email": "demo@vocelio.com"}
    return {"id": "user123", "email": "demo@vocelio.com"}  # Demo mode

async def initialize_sample_data():
    """Initialize sample AI data"""
    
    # Sample knowledge base entries
    knowledge_entries = [
        {
            "title": "Product Pricing Information",
            "content": "Our starter plan costs $29/month, professional plan $99/month, and enterprise plan $299/month. All plans include unlimited calls and basic analytics.",
            "category": "pricing",
            "tags": ["pricing", "plans", "cost", "billing"]
        },
        {
            "title": "Technical Support Process",
            "content": "For technical issues, we provide 24/7 support via phone, email, and chat. Critical issues are resolved within 2 hours, standard issues within 24 hours.",
            "category": "support",
            "tags": ["support", "technical", "help", "assistance"]
        },
        {
            "title": "Call Center Features",
            "content": "Our AI call center includes voice cloning, real-time sentiment analysis, automatic call routing, conversation insights, and integration with CRM systems.",
            "category": "features",
            "tags": ["features", "capabilities", "ai", "voice"]
        },
        {
            "title": "Data Security and Compliance",
            "content": "We are SOC 2 compliant and follow GDPR guidelines. All data is encrypted in transit and at rest. We provide data export and deletion upon request.",
            "category": "security",
            "tags": ["security", "compliance", "privacy", "gdpr"]
        },
        {
            "title": "Integration Capabilities",
            "content": "Vocelio integrates with Salesforce, HubSpot, Pipedrive, Zapier, and custom APIs. We provide webhooks and REST APIs for seamless integration.",
            "category": "integrations",
            "tags": ["integrations", "api", "crm", "webhooks"]
        }
    ]
    
    for i, entry in enumerate(knowledge_entries):
        kb_id = str(uuid.uuid4())
        
        knowledge_base_db[kb_id] = {
            "id": kb_id,
            "title": entry["title"],
            "content": entry["content"],
            "category": entry["category"],
            "tags": entry["tags"],
            "confidence_threshold": 0.8,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            "updated_at": datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        }
    
    # Sample conversations
    for i in range(10):
        conversation_id = str(uuid.uuid4())
        created_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        
        conversation = {
            "conversation_id": conversation_id,
            "agent_id": f"agent_{random.randint(1, 5)}",
            "state": random.choice(list(ConversationState)),
            "messages": [
                {
                    "role": "user",
                    "content": f"Hello, I have a question about {random.choice(['pricing', 'features', 'support', 'integration'])}",
                    "timestamp": created_time.isoformat()
                },
                {
                    "role": "assistant",
                    "content": "I'd be happy to help you with that. Let me get you the information you need.",
                    "timestamp": (created_time + timedelta(seconds=30)).isoformat()
                }
            ],
            "customer_info": {
                "name": f"Customer {i+1}",
                "email": f"customer{i+1}@example.com",
                "phone": f"+1555{random.randint(1000000, 9999999)}"
            },
            "session_data": {
                "intent_history": [random.choice(list(IntentType)) for _ in range(3)],
                "sentiment_trend": [random.choice(list(SentimentType)) for _ in range(3)]
            },
            "created_at": created_time,
            "updated_at": created_time + timedelta(minutes=random.randint(5, 30))
        }
        
        conversations_db[conversation_id] = conversation

def analyze_text(text: str, language: LanguageCode = LanguageCode.EN) -> TextAnalysisResponse:
    """Simulate text analysis using AI/NLP"""
    
    # Simulate language detection
    language_confidence = random.uniform(0.85, 0.99)
    
    # Simulate sentiment analysis
    sentiment_scores = {
        SentimentType.POSITIVE: random.uniform(0.0, 1.0),
        SentimentType.NEGATIVE: random.uniform(0.0, 1.0),
        SentimentType.NEUTRAL: random.uniform(0.0, 1.0)
    }
    
    dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
    sentiment = Sentiment(
        label=dominant_sentiment,
        score=sentiment_scores[dominant_sentiment],
        confidence=random.uniform(0.7, 0.95)
    )
    
    # Simulate intent detection
    intent_mapping = {
        "hello": IntentType.GREETING,
        "price": IntentType.INQUIRY,
        "cost": IntentType.INQUIRY,
        "problem": IntentType.COMPLAINT,
        "issue": IntentType.COMPLAINT,
        "book": IntentType.BOOKING,
        "schedule": IntentType.BOOKING,
        "help": IntentType.SUPPORT,
        "buy": IntentType.SALES,
        "purchase": IntentType.SALES,
        "cancel": IntentType.OBJECTION,
        "end": IntentType.CLOSING
    }
    
    detected_intent = IntentType.UNKNOWN
    intent_confidence = 0.5
    
    text_lower = text.lower()
    for keyword, intent_type in intent_mapping.items():
        if keyword in text_lower:
            detected_intent = intent_type
            intent_confidence = random.uniform(0.8, 0.95)
            break
    
    intent = Intent(
        name=detected_intent,
        confidence=intent_confidence,
        parameters={}
    )
    
    # Simulate entity extraction
    entities = []
    
    # Look for phone numbers
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phone_matches = re.finditer(phone_pattern, text)
    for match in phone_matches:
        entities.append(Entity(
            text=match.group(),
            label="PHONE",
            start=match.start(),
            end=match.end(),
            confidence=random.uniform(0.9, 0.99)
        ))
    
    # Look for email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.finditer(email_pattern, text)
    for match in email_matches:
        entities.append(Entity(
            text=match.group(),
            label="EMAIL",
            start=match.start(),
            end=match.end(),
            confidence=random.uniform(0.9, 0.99)
        ))
    
    # Simulate emotions
    emotions = [
        Emotion(emotion=EmotionType.NEUTRAL, intensity=random.uniform(0.3, 0.7)),
        Emotion(emotion=random.choice(list(EmotionType)), intensity=random.uniform(0.1, 0.4))
    ]
    
    # Extract keywords
    keywords = []
    words = text.lower().split()
    important_words = [word for word in words if len(word) > 3 and word.isalpha()]
    keywords = random.sample(important_words, min(5, len(important_words)))
    
    return TextAnalysisResponse(
        text=text,
        language=language,
        language_confidence=language_confidence,
        sentiment=sentiment,
        intent=intent,
        entities=entities,
        emotions=emotions,
        keywords=keywords,
        summary=f"Analyzed text with {detected_intent} intent and {dominant_sentiment} sentiment"
    )

def generate_ai_response(message: str, context: ConversationContext, model: AIModelType) -> str:
    """Generate AI response based on message and context"""
    
    # Simulate different AI model responses
    if model == AIModelType.GPT4:
        responses = [
            "I understand your concern. Let me provide you with detailed information about that.",
            "That's a great question! Based on our latest features, I can help you with that.",
            "I appreciate your patience. Here's what I can tell you about this topic.",
            "Thank you for reaching out. I'll be happy to assist you with this matter."
        ]
    elif model == AIModelType.CLAUDE:
        responses = [
            "I'd be delighted to help you with that. Let me explain this clearly.",
            "That's an excellent point. Here's how we can address your needs.",
            "I understand what you're looking for. Let me provide you with the right information.",
            "Thank you for your question. I'll give you a comprehensive answer."
        ]
    else:  # Default responses
        responses = [
            "I can help you with that. Let me get you the information you need.",
            "Thank you for your question. Here's what I can tell you.",
            "I understand. Let me assist you with this matter.",
            "Great question! I'll be happy to help you with that."
        ]
    
    base_response = random.choice(responses)
    
    # Add context-aware elements
    if context.customer_info.get("name"):
        base_response = base_response.replace("you", f"you, {context.customer_info['name']}")
    
    # Simulate knowledge base lookup
    relevant_kb = search_knowledge_base(message)
    if relevant_kb:
        base_response += f" {relevant_kb['content'][:200]}..."
    
    return base_response

def search_knowledge_base(query: str) -> Optional[Dict[str, Any]]:
    """Search knowledge base for relevant information"""
    
    query_lower = query.lower()
    
    for kb_entry in knowledge_base_db.values():
        # Simple keyword matching
        for tag in kb_entry["tags"]:
            if tag.lower() in query_lower:
                return kb_entry
        
        # Content matching
        if any(word in kb_entry["content"].lower() for word in query_lower.split()):
            return kb_entry
    
    return None

def generate_suggested_actions(intent: Intent, sentiment: Sentiment) -> List[str]:
    """Generate suggested actions based on intent and sentiment"""
    
    actions = []
    
    if intent.name == IntentType.COMPLAINT and sentiment.label == SentimentType.NEGATIVE:
        actions = [
            "Escalate to supervisor",
            "Offer compensation",
            "Schedule follow-up call",
            "Document issue in CRM"
        ]
    elif intent.name == IntentType.SALES and sentiment.label == SentimentType.POSITIVE:
        actions = [
            "Send pricing information",
            "Schedule demo",
            "Transfer to sales specialist",
            "Add to high-priority leads"
        ]
    elif intent.name == IntentType.SUPPORT:
        actions = [
            "Create support ticket",
            "Send documentation",
            "Schedule technical call",
            "Check system status"
        ]
    else:
        actions = [
            "Continue conversation",
            "Ask clarifying questions",
            "Provide more information",
            "Check customer satisfaction"
        ]
    
    return actions[:3]  # Return top 3 actions

def generate_conversation_insights(conversation: ConversationContext) -> List[ConversationInsight]:
    """Generate AI-powered conversation insights"""
    
    insights = []
    
    # Analyze message count
    if len(conversation.messages) > 10:
        insights.append(ConversationInsight(
            insight_type="conversation_length",
            title="Long Conversation Detected",
            description="This conversation has been going on for a while and may need supervisor attention.",
            recommendations=["Consider escalation", "Summarize key points", "Offer follow-up call"],
            confidence=0.85,
            data={"message_count": len(conversation.messages)}
        ))
    
    # Analyze sentiment trend
    sentiment_history = conversation.session_data.get("sentiment_trend", [])
    if len(sentiment_history) >= 3 and sentiment_history[-2:] == [SentimentType.NEGATIVE, SentimentType.NEGATIVE]:
        insights.append(ConversationInsight(
            insight_type="sentiment_decline",
            title="Customer Sentiment Declining",
            description="Customer sentiment has been negative in recent messages.",
            recommendations=["Use empathetic language", "Offer immediate solution", "Consider human takeover"],
            confidence=0.90,
            data={"sentiment_trend": sentiment_history}
        ))
    
    # Analyze intent patterns
    intent_history = conversation.session_data.get("intent_history", [])
    if IntentType.OBJECTION in intent_history:
        insights.append(ConversationInsight(
            insight_type="objection_handling",
            title="Sales Objection Detected",
            description="Customer has raised objections that need to be addressed.",
            recommendations=["Address concerns directly", "Provide testimonials", "Offer trial period"],
            confidence=0.80,
            data={"objection_count": intent_history.count(IntentType.OBJECTION)}
        ))
    
    return insights

# Routes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-brain",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text_endpoint(
    request: TextAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze text for sentiment, intent, entities, and emotions"""
    
    start_time = datetime.utcnow()
    
    analysis = analyze_text(request.text, request.language)
    
    # Only include requested analysis components
    if not request.include_sentiment:
        analysis.sentiment = None
    if not request.include_intent:
        analysis.intent = None
    if not request.include_entities:
        analysis.entities = []
    if not request.include_emotions:
        analysis.emotions = []
    
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Text analysis completed in {processing_time:.3f}s")
    
    return analysis

@app.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(
    request: ConversationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Handle conversation message and generate AI response"""
    
    start_time = datetime.utcnow()
    
    # Get or create conversation
    if request.conversation_id and request.conversation_id in conversations_db:
        conversation = conversations_db[request.conversation_id]
        conversation_id = request.conversation_id
    else:
        conversation_id = str(uuid.uuid4())
        conversation = {
            "conversation_id": conversation_id,
            "agent_id": request.agent_id,
            "state": ConversationState.ACTIVE,
            "messages": [],
            "customer_info": request.context.get("customer_info", {}) if request.context else {},
            "session_data": {"intent_history": [], "sentiment_trend": []},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        conversations_db[conversation_id] = conversation
    
    # Analyze the incoming message
    analysis = analyze_text(request.message)
    
    # Update conversation context
    conversation["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat(),
        "analysis": analysis.dict()
    })
    
    conversation["session_data"]["intent_history"].append(analysis.intent.name)
    conversation["session_data"]["sentiment_trend"].append(analysis.sentiment.label)
    conversation["updated_at"] = datetime.utcnow()
    
    # Generate AI response
    context_obj = ConversationContext(**conversation)
    ai_response = generate_ai_response(request.message, context_obj, request.model)
    
    # Add AI response to conversation
    conversation["messages"].append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.utcnow().isoformat(),
        "model": request.model
    })
    
    # Generate suggested actions
    suggested_actions = generate_suggested_actions(analysis.intent, analysis.sentiment)
    
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Process insights in background
    background_tasks.add_task(analyze_conversation_insights, conversation_id)
    
    response = ConversationResponse(
        conversation_id=conversation_id,
        message=request.message,
        response=ai_response,
        intent=analysis.intent,
        sentiment=analysis.sentiment,
        suggested_actions=suggested_actions,
        confidence=min(analysis.intent.confidence, analysis.sentiment.confidence),
        processing_time=processing_time,
        model_used=request.model,
        context_updated={"last_intent": analysis.intent.name, "last_sentiment": analysis.sentiment.label}
    )
    
    return response

@app.get("/conversations/{conversation_id}", response_model=ConversationContext)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get conversation by ID"""
    
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationContext(**conversations_db[conversation_id])

@app.get("/conversations", response_model=List[ConversationContext])
async def get_conversations(
    agent_id: Optional[str] = None,
    state: Optional[ConversationState] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get conversations with optional filtering"""
    
    conversations = list(conversations_db.values())
    
    # Apply filters
    if agent_id:
        conversations = [c for c in conversations if c["agent_id"] == agent_id]
    if state:
        conversations = [c for c in conversations if c["state"] == state]
    
    # Sort by updated_at desc
    conversations.sort(key=lambda x: x["updated_at"], reverse=True)
    
    # Apply pagination
    conversations = conversations[offset:offset + limit]
    
    return [ConversationContext(**conv) for conv in conversations]

@app.get("/conversations/{conversation_id}/insights", response_model=List[ConversationInsight])
async def get_conversation_insights(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get AI-generated insights for a conversation"""
    
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = ConversationContext(**conversations_db[conversation_id])
    insights = generate_conversation_insights(conversation)
    
    return insights

@app.get("/knowledge-base", response_model=List[KnowledgeBase])
async def get_knowledge_base(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge base entries"""
    
    entries = list(knowledge_base_db.values())
    
    # Apply filters
    if category:
        entries = [e for e in entries if e["category"] == category]
    if search:
        search_lower = search.lower()
        entries = [
            e for e in entries 
            if search_lower in e["title"].lower() or 
               search_lower in e["content"].lower() or
               any(search_lower in tag.lower() for tag in e["tags"])
        ]
    
    # Sort by updated_at desc
    entries.sort(key=lambda x: x["updated_at"], reverse=True)
    
    # Apply pagination
    entries = entries[offset:offset + limit]
    
    return [KnowledgeBase(**entry) for entry in entries]

@app.post("/knowledge-base", response_model=KnowledgeBase)
async def create_knowledge_entry(
    entry_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create new knowledge base entry"""
    
    entry_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    entry = {
        "id": entry_id,
        "title": entry_data["title"],
        "content": entry_data["content"],
        "category": entry_data.get("category", "general"),
        "tags": entry_data.get("tags", []),
        "confidence_threshold": entry_data.get("confidence_threshold", 0.8),
        "created_at": now,
        "updated_at": now
    }
    
    knowledge_base_db[entry_id] = entry
    
    return KnowledgeBase(**entry)

@app.get("/smart-replies")
async def get_smart_replies(
    intent: Optional[IntentType] = None,
    sentiment: Optional[SentimentType] = None,
    limit: int = Query(default=5, le=10),
    current_user: dict = Depends(get_current_user)
):
    """Get smart reply suggestions"""
    
    # Generate smart replies based on intent and sentiment
    replies = []
    
    if intent == IntentType.GREETING:
        replies = [
            SmartReply(text="Hello! How can I assist you today?", intent=intent, confidence=0.95),
            SmartReply(text="Good day! What can I help you with?", intent=intent, confidence=0.90),
            SmartReply(text="Hi there! I'm here to help.", intent=intent, confidence=0.85)
        ]
    elif intent == IntentType.COMPLAINT:
        if sentiment == SentimentType.NEGATIVE:
            replies = [
                SmartReply(text="I understand your frustration. Let me help resolve this immediately.", intent=intent, confidence=0.95, tone="empathetic"),
                SmartReply(text="I apologize for the inconvenience. I'll make sure we fix this for you.", intent=intent, confidence=0.90, tone="apologetic"),
                SmartReply(text="I hear your concern and I want to make this right. Can you tell me more?", intent=intent, confidence=0.85, tone="caring")
            ]
        else:
            replies = [
                SmartReply(text="Thank you for bringing this to my attention. How can I help?", intent=intent, confidence=0.90),
                SmartReply(text="I appreciate your feedback. Let's work together to resolve this.", intent=intent, confidence=0.85)
            ]
    elif intent == IntentType.SALES:
        replies = [
            SmartReply(text="I'd be happy to show you how our solution can benefit your business.", intent=intent, confidence=0.95, tone="enthusiastic"),
            SmartReply(text="Great! Let me share some information about our offerings.", intent=intent, confidence=0.90, tone="professional"),
            SmartReply(text="Perfect timing! Our current promotion might be exactly what you're looking for.", intent=intent, confidence=0.85, tone="promotional")
        ]
    else:
        replies = [
            SmartReply(text="I understand. How can I best assist you with this?", intent=IntentType.UNKNOWN, confidence=0.70),
            SmartReply(text="Thank you for your message. Can you provide more details?", intent=IntentType.UNKNOWN, confidence=0.65),
            SmartReply(text="I'm here to help. What specific information do you need?", intent=IntentType.UNKNOWN, confidence=0.60)
        ]
    
    return replies[:limit]

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(
    date_range: int = Query(default=30, description="Days of data to include"),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard analytics for AI Brain Service"""
    
    total_conversations = len(conversations_db)
    active_conversations = len([c for c in conversations_db.values() if c["state"] == ConversationState.ACTIVE])
    
    # Analyze intent distribution
    intent_distribution = {}
    sentiment_distribution = {}
    
    for conversation in conversations_db.values():
        intent_history = conversation["session_data"].get("intent_history", [])
        sentiment_history = conversation["session_data"].get("sentiment_trend", [])
        
        for intent in intent_history:
            intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
        
        for sentiment in sentiment_history:
            sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1
    
    return {
        "overview": {
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "completed_conversations": len([c for c in conversations_db.values() if c["state"] == ConversationState.COMPLETED]),
            "knowledge_base_entries": len(knowledge_base_db),
            "average_response_time": round(random.uniform(0.5, 2.5), 2),
            "ai_confidence_average": round(random.uniform(0.85, 0.95), 3)
        },
        "intelligence": {
            "intent_accuracy": round(random.uniform(0.88, 0.96), 3),
            "sentiment_accuracy": round(random.uniform(0.90, 0.98), 3),
            "entity_extraction_accuracy": round(random.uniform(0.85, 0.94), 3),
            "conversation_completion_rate": round(random.uniform(0.82, 0.92), 3)
        },
        "usage": {
            "daily_conversations": [random.randint(50, 200) for _ in range(7)],
            "intent_distribution": intent_distribution,
            "sentiment_distribution": sentiment_distribution,
            "top_knowledge_categories": {
                "pricing": random.randint(50, 150),
                "support": random.randint(40, 120),
                "features": random.randint(30, 100),
                "integrations": random.randint(20, 80)
            }
        },
        "performance": {
            "average_conversation_length": round(random.uniform(8.5, 15.2), 1),
            "successful_resolutions": round(random.uniform(0.75, 0.88), 3),
            "escalation_rate": round(random.uniform(0.05, 0.15), 3),
            "customer_satisfaction": round(random.uniform(4.2, 4.8), 2)
        },
        "insights": [
            {
                "type": "optimization",
                "message": "Complaint handling improved by 15% this week",
                "impact": "positive"
            },
            {
                "type": "alert",
                "message": "3 conversations require immediate attention",
                "impact": "high"
            },
            {
                "type": "trend",
                "message": "Sales intent increased by 22% compared to last month",
                "impact": "positive"
            }
        ]
    }

# Background Tasks

async def analyze_conversation_insights(conversation_id: str):
    """Analyze conversation for insights in background"""
    
    await asyncio.sleep(2)  # Simulate processing time
    
    if conversation_id in conversations_db:
        conversation = ConversationContext(**conversations_db[conversation_id])
        insights = generate_conversation_insights(conversation)
        
        # Store insights (in production, save to database)
        conversations_db[conversation_id]["insights"] = [insight.dict() for insight in insights]
        
        logger.info(f"Generated {len(insights)} insights for conversation {conversation_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )
