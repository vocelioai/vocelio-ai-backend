"""
Role-Based Access Control (RBAC) Manager
Comprehensive permission and role management system
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass
from functools import wraps
from fastapi import HTTPException, status, Depends
import logging

logger = logging.getLogger(__name__)

class Role(str, Enum):
    """System roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    AGENT = "agent"
    VIEWER = "viewer"
    API_USER = "api_user"
    GUEST = "guest"

class Permission(str, Enum):
    """Granular permissions for system resources"""
    # Universal permissions
    ALL = "*"
    READ_ALL = "read:*"
    WRITE_ALL = "write:*"
    
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_INVITE = "user:invite"
    
    # Agent management
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_TRAIN = "agent:train"
    AGENT_ASSIGN = "agent:assign"
    
    # Campaign management
    CAMPAIGN_CREATE = "campaign:create"
    CAMPAIGN_READ = "campaign:read"
    CAMPAIGN_UPDATE = "campaign:update"
    CAMPAIGN_DELETE = "campaign:delete"
    CAMPAIGN_START = "campaign:start"
    CAMPAIGN_STOP = "campaign:stop"
    
    # Call management
    CALL_READ = "call:read"
    CALL_UPDATE = "call:update"
    CALL_TRANSFER = "call:transfer"
    CALL_RECORD = "call:record"
    CALL_MONITOR = "call:monitor"
    
    # Voice management
    VOICE_CREATE = "voice:create"
    VOICE_READ = "voice:read"
    VOICE_UPDATE = "voice:update"
    VOICE_DELETE = "voice:delete"
    VOICE_CLONE = "voice:clone"
    
    # Analytics and reporting
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    REPORTS_CREATE = "reports:create"
    REPORTS_READ = "reports:read"
    
    # Billing and finance
    BILLING_READ = "billing:read"
    BILLING_UPDATE = "billing:update"
    BILLING_ADMIN = "billing:admin"
    
    # System administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_BACKUP = "system:backup"
    
    # Integration management
    INTEGRATION_CREATE = "integration:create"
    INTEGRATION_READ = "integration:read"
    INTEGRATION_UPDATE = "integration:update"
    INTEGRATION_DELETE = "integration:delete"

@dataclass
class UserContext:
    """User context with roles and permissions"""
    user_id: str
    organization_id: str
    roles: List[Role]
    permissions: Set[Permission]
    is_active: bool = True
    is_verified: bool = True

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        self._role_permissions = self._initialize_role_permissions()
        self._cached_permissions: Dict[str, Set[Permission]] = {}
    
    def _initialize_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """Initialize role-permission mappings"""
        return {
            Role.SUPER_ADMIN: {Permission.ALL},
            
            Role.ADMIN: {
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE,
                Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_DELETE,
                Permission.CAMPAIGN_CREATE, Permission.CAMPAIGN_READ, Permission.CAMPAIGN_UPDATE, Permission.CAMPAIGN_DELETE,
                Permission.VOICE_CREATE, Permission.VOICE_READ, Permission.VOICE_UPDATE, Permission.VOICE_DELETE,
                Permission.ANALYTICS_READ, Permission.ANALYTICS_EXPORT,
                Permission.REPORTS_CREATE, Permission.REPORTS_READ,
                Permission.BILLING_READ, Permission.BILLING_UPDATE,
                Permission.SYSTEM_CONFIG, Permission.SYSTEM_MONITOR,
                Permission.INTEGRATION_CREATE, Permission.INTEGRATION_READ, Permission.INTEGRATION_UPDATE,
            },
            
            Role.MANAGER: {
                Permission.USER_READ, Permission.USER_INVITE,
                Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_ASSIGN,
                Permission.CAMPAIGN_CREATE, Permission.CAMPAIGN_READ, Permission.CAMPAIGN_UPDATE,
                Permission.CAMPAIGN_START, Permission.CAMPAIGN_STOP,
                Permission.CALL_READ, Permission.CALL_MONITOR,
                Permission.VOICE_READ, Permission.VOICE_UPDATE,
                Permission.ANALYTICS_READ, Permission.REPORTS_READ,
                Permission.INTEGRATION_READ,
            },
            
            Role.SUPERVISOR: {
                Permission.AGENT_READ, Permission.AGENT_UPDATE,
                Permission.CAMPAIGN_READ, Permission.CAMPAIGN_UPDATE,
                Permission.CALL_READ, Permission.CALL_MONITOR, Permission.CALL_TRANSFER,
                Permission.VOICE_READ,
                Permission.ANALYTICS_READ,
            },
            
            Role.AGENT: {
                Permission.CALL_READ, Permission.CALL_UPDATE, Permission.CALL_TRANSFER,
                Permission.VOICE_READ,
                Permission.ANALYTICS_READ,
            },
            
            Role.VIEWER: {
                Permission.ANALYTICS_READ, Permission.REPORTS_READ,
                Permission.CALL_READ, Permission.CAMPAIGN_READ,
            },
            
            Role.API_USER: {
                Permission.AGENT_READ, Permission.CAMPAIGN_READ,
                Permission.CALL_READ, Permission.ANALYTICS_READ,
            },
            
            Role.GUEST: set()
        }
    
    def get_user_permissions(self, user_context: UserContext) -> Set[Permission]:
        """Get all permissions for a user based on their roles"""
        cache_key = f"{user_context.user_id}:{','.join(user_context.roles)}"
        
        if cache_key in self._cached_permissions:
            return self._cached_permissions[cache_key]
        
        permissions = set()
        for role in user_context.roles:
            role_perms = self._role_permissions.get(role, set())
            permissions.update(role_perms)
        
        # Handle wildcard permissions
        if Permission.ALL in permissions:
            permissions = set(Permission)
        
        self._cached_permissions[cache_key] = permissions
        return permissions
    
    def has_permission(self, user_context: UserContext, required_permission: Permission) -> bool:
        """Check if user has specific permission"""
        if not user_context.is_active or not user_context.is_verified:
            return False
        
        user_permissions = self.get_user_permissions(user_context)
        
        # Check for exact permission
        if required_permission in user_permissions:
            return True
        
        # Check for wildcard permissions
        if Permission.ALL in user_permissions:
            return True
        
        # Check for read-all permission on read operations
        if required_permission.value.endswith(":read") and Permission.READ_ALL in user_permissions:
            return True
        
        # Check for write-all permission on write operations
        write_ops = [":create", ":update", ":delete", ":start", ":stop", ":train", ":assign"]
        if any(required_permission.value.endswith(op) for op in write_ops):
            if Permission.WRITE_ALL in user_permissions:
                return True
        
        return False
    
    def has_any_permission(self, user_context: UserContext, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        return any(self.has_permission(user_context, perm) for perm in permissions)
    
    def has_all_permissions(self, user_context: UserContext, permissions: List[Permission]) -> bool:
        """Check if user has all specified permissions"""
        return all(self.has_permission(user_context, perm) for perm in permissions)
    
    def add_role_permission(self, role: Role, permission: Permission):
        """Add permission to role"""
        if role not in self._role_permissions:
            self._role_permissions[role] = set()
        self._role_permissions[role].add(permission)
        self._clear_cache()
    
    def remove_role_permission(self, role: Role, permission: Permission):
        """Remove permission from role"""
        if role in self._role_permissions:
            self._role_permissions[role].discard(permission)
        self._clear_cache()
    
    def _clear_cache(self):
        """Clear permission cache"""
        self._cached_permissions.clear()

# Global RBAC manager instance
rbac_manager = RBACManager()

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user context from request
            user_context = kwargs.get('current_user')
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not rbac_manager.has_permission(user_context, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[Permission]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_context = kwargs.get('current_user')
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not rbac_manager.has_any_permission(user_context, permissions):
                perm_names = [p.value for p in permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of these permissions required: {', '.join(perm_names)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: Role):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_context = kwargs.get('current_user')
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if role not in user_context.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Utility functions for common permission checks
async def get_current_user_context(request) -> UserContext:
    """Extract user context from request"""
    # This would integrate with your JWT token validation
    # For now, return a mock context
    return UserContext(
        user_id="user_123",
        organization_id="org_123",
        roles=[Role.MANAGER],
        permissions=rbac_manager.get_user_permissions(UserContext(
            user_id="user_123",
            organization_id="org_123",
            roles=[Role.MANAGER],
            permissions=set()
        ))
    )

def check_organization_access(user_context: UserContext, resource_org_id: str) -> bool:
    """Check if user has access to organization resources"""
    # Super admin can access all organizations
    if Role.SUPER_ADMIN in user_context.roles:
        return True
    
    # Users can only access their own organization's resources
    return user_context.organization_id == resource_org_id
