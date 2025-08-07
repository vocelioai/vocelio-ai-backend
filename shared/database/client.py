"""
Supabase Database Client
Centralized database connection and utilities for all microservices
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
import asyncio
import logging
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Centralized database client for all Vocelio microservices"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.supabase_url, self.supabase_key]):
            raise ValueError("Missing required Supabase environment variables")
            
        # Client for regular operations
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Admin client for service-to-service operations
        if self.service_role_key:
            self.admin_client: Client = create_client(self.supabase_url, self.service_role_key)
        else:
            self.admin_client = self.client
            
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            result = self.client.table("users").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    # User Management
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new user"""
        try:
            user_data["created_at"] = datetime.now(timezone.utc).isoformat()
            user_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("users").insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user"""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("users").update(updates).eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    # Organization Management
    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID"""
        try:
            result = self.client.table("organizations").select("*").eq("id", org_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting organization {org_id}: {e}")
            return None
    
    async def create_organization(self, org_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new organization"""
        try:
            org_data["created_at"] = datetime.now(timezone.utc).isoformat()
            org_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("organizations").insert(org_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating organization: {e}")
            return None
    
    # Agent Management
    async def get_agents(self, user_id: str, org_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a user/organization"""
        try:
            result = self.client.table("agents").select("*").eq("user_id", user_id).eq("organization_id", org_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting agents: {e}")
            return []
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new AI agent"""
        try:
            agent_data["created_at"] = datetime.now(timezone.utc).isoformat()
            agent_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("agents").insert(agent_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return None
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update agent"""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("agents").update(updates).eq("id", agent_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            return None
    
    # Campaign Management
    async def get_campaigns(self, user_id: str, org_id: str) -> List[Dict[str, Any]]:
        """Get all campaigns for a user/organization"""
        try:
            result = self.client.table("campaigns").select("*").eq("user_id", user_id).eq("organization_id", org_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            return []
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new campaign"""
        try:
            campaign_data["created_at"] = datetime.now(timezone.utc).isoformat()
            campaign_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("campaigns").insert(campaign_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return None
    
    # Call Management
    async def create_call_record(self, call_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create call record"""
        try:
            call_data["created_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("calls").insert(call_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating call record: {e}")
            return None
    
    async def update_call_record(self, call_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update call record"""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("calls").update(updates).eq("id", call_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating call {call_id}: {e}")
            return None
    
    # Voice Management
    async def get_voices(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get available voices with optional filters"""
        try:
            query = self.client.table("voices").select("*")
            
            if filters:
                for key, value in filters.items():
                    if value and value != "all":
                        query = query.eq(key, value)
            
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    # Analytics and Metrics
    async def log_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Log analytics metric"""
        try:
            metric_data["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            self.client.table("analytics_metrics").insert(metric_data).execute()
            return True
        except Exception as e:
            logger.error(f"Error logging metric: {e}")
            return False
    
    async def get_metrics(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get analytics metrics with filters"""
        try:
            query = self.client.table("analytics_metrics").select("*")
            
            if filters.get("user_id"):
                query = query.eq("user_id", filters["user_id"])
            if filters.get("metric_type"):
                query = query.eq("metric_type", filters["metric_type"])
            if filters.get("start_date"):
                query = query.gte("timestamp", filters["start_date"])
            if filters.get("end_date"):
                query = query.lte("timestamp", filters["end_date"])
            
            result = query.order("timestamp", desc=True).limit(1000).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []
    
    # Billing and Usage
    async def log_usage(self, usage_data: Dict[str, Any]) -> bool:
        """Log usage for billing"""
        try:
            usage_data["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            self.client.table("usage_logs").insert(usage_data).execute()
            return True
        except Exception as e:
            logger.error(f"Error logging usage: {e}")
            return False
    
    async def get_usage_summary(self, user_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get usage summary for billing"""
        try:
            result = self.client.table("usage_logs").select("*").eq("user_id", user_id).gte("timestamp", start_date).lte("timestamp", end_date).execute()
            
            usage_data = result.data or []
            
            # Calculate totals
            total_calls = len([u for u in usage_data if u.get("usage_type") == "call"])
            total_minutes = sum([u.get("duration", 0) for u in usage_data if u.get("usage_type") == "call"])
            total_cost = sum([u.get("cost", 0) for u in usage_data])
            
            return {
                "total_calls": total_calls,
                "total_minutes": total_minutes,
                "total_cost": total_cost,
                "usage_details": usage_data
            }
        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            return {}
    
    # Generic table operations
    async def get_records(self, table: str, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Generic method to get records from any table"""
        try:
            query = self.client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting records from {table}: {e}")
            return []
    
    async def create_record(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generic method to create record in any table"""
        try:
            if "created_at" not in data:
                data["created_at"] = datetime.now(timezone.utc).isoformat()
            if "updated_at" not in data:
                data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating record in {table}: {e}")
            return None
    
    async def update_record(self, table: str, record_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generic method to update record in any table"""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table(table).update(updates).eq("id", record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating record in {table}: {e}")
            return None

# Global database client instance - initialized conditionally
try:
    db_client = DatabaseClient()
except ValueError:
    # Running without Supabase configuration
    db_client = None
