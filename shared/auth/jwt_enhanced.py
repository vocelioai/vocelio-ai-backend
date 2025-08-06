"""
Enhanced JWT Authentication System
Comprehensive token validation, refresh, and security features
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import redis
import logging
from .rbac import UserContext, Role, rbac_manager

logger = logging.getLogger(__name__)

class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    organization_id: str
    roles: List[str]
    email: str
    is_verified: bool = True
    is_active: bool = True
    token_type: str = "access"
    issued_at: datetime
    expires_at: datetime

class TokenPair(BaseModel):
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class JWTManager:
    """Enhanced JWT token management with security features"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        redis_client: Optional[redis.Redis] = None
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.redis_client = redis_client
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.token_blacklist_prefix = "blacklist:"
        self.failed_attempts_prefix = "failed:"
        self.refresh_token_prefix = "refresh:"
    
    def create_access_token(
        self,
        user_id: str,
        organization_id: str,
        roles: List[str],
        email: str,
        is_verified: bool = True,
        is_active: bool = True,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        issued_at = datetime.utcnow()
        
        payload = {
            "user_id": user_id,
            "organization_id": organization_id,
            "roles": roles,
            "email": email,
            "is_verified": is_verified,
            "is_active": is_active,
            "token_type": "access",
            "iat": issued_at.timestamp(),
            "exp": expire.timestamp(),
            "jti": secrets.token_urlsafe(16),  # Unique token ID
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        issued_at = datetime.utcnow()
        
        payload = {
            "user_id": user_id,
            "token_type": "refresh",
            "iat": issued_at.timestamp(),
            "exp": expire.timestamp(),
            "jti": secrets.token_urlsafe(32),  # Longer ID for refresh tokens
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token in Redis if available
        if self.redis_client:
            self.redis_client.setex(
                f"{self.refresh_token_prefix}{user_id}",
                timedelta(days=self.refresh_token_expire_days),
                token
            )
        
        return token
    
    def create_token_pair(
        self,
        user_id: str,
        organization_id: str,
        roles: List[str],
        email: str,
        is_verified: bool = True,
        is_active: bool = True
    ) -> TokenPair:
        """Create access and refresh token pair"""
        access_token = self.create_access_token(
            user_id, organization_id, roles, email, is_verified, is_active
        )
        refresh_token = self.create_refresh_token(user_id)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60
        )
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token"""
        try:
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate token type
            if payload.get("token_type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected: {token_type}"
                )
            
            # Check expiration
            if datetime.utcnow().timestamp() > payload.get("exp", 0):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return TokenData(
                user_id=payload["user_id"],
                organization_id=payload.get("organization_id", ""),
                roles=payload.get("roles", []),
                email=payload.get("email", ""),
                is_verified=payload.get("is_verified", True),
                is_active=payload.get("is_active", True),
                token_type=payload["token_type"],
                issued_at=datetime.fromtimestamp(payload["iat"]),
                expires_at=datetime.fromtimestamp(payload["exp"])
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            logger.warning(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token"""
        # Verify refresh token
        token_data = self.verify_token(refresh_token, "refresh")
        
        # Check if refresh token is still valid in Redis
        if self.redis_client:
            stored_token = self.redis_client.get(f"{self.refresh_token_prefix}{token_data.user_id}")
            if not stored_token or stored_token.decode() != refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
        
        # Here you would typically fetch user data from database
        # For now, we'll use the token data
        return self.create_token_pair(
            user_id=token_data.user_id,
            organization_id=token_data.organization_id,
            roles=token_data.roles,
            email=token_data.email,
            is_verified=token_data.is_verified,
            is_active=token_data.is_active
        )
    
    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist"""
        if not self.redis_client:
            logger.warning("Redis not available for token blacklisting")
            return
        
        try:
            # Decode token to get expiration
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp", 0)
            
            # Calculate TTL (time until token expires)
            ttl = max(0, int(exp - datetime.utcnow().timestamp()))
            
            # Add to blacklist with TTL
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.redis_client.setex(f"{self.blacklist_prefix}{token_hash}", ttl, "1")
            
        except jwt.JWTError:
            # If token is invalid, no need to blacklist
            pass
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        if not self.redis_client:
            return False
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return bool(self.redis_client.get(f"{self.blacklist_prefix}{token_hash}"))
    
    def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revoke all tokens for a user"""
        if not self.redis_client:
            logger.warning("Redis not available for token revocation")
            return
        
        # Remove refresh token
        self.redis_client.delete(f"{self.refresh_token_prefix}{user_id}")
        
        # Add user to global revocation list (all tokens issued before this time are invalid)
        self.redis_client.setex(
            f"revoked_user:{user_id}",
            timedelta(days=self.refresh_token_expire_days),
            datetime.utcnow().timestamp()
        )
    
    def track_failed_login(self, identifier: str) -> None:
        """Track failed login attempt"""
        if not self.redis_client:
            return
        
        key = f"{self.failed_attempts_prefix}{identifier}"
        current_attempts = self.redis_client.get(key)
        
        if current_attempts:
            attempts = int(current_attempts) + 1
        else:
            attempts = 1
        
        self.redis_client.setex(key, self.lockout_duration, attempts)
    
    def is_account_locked(self, identifier: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if not self.redis_client:
            return False
        
        key = f"{self.failed_attempts_prefix}{identifier}"
        attempts = self.redis_client.get(key)
        
        return attempts and int(attempts) >= self.max_failed_attempts
    
    def clear_failed_attempts(self, identifier: str) -> None:
        """Clear failed login attempts"""
        if self.redis_client:
            self.redis_client.delete(f"{self.failed_attempts_prefix}{identifier}")

# Security bearer for FastAPI
security = HTTPBearer()

# Global JWT manager (initialize with your settings)
jwt_manager = JWTManager(
    secret_key="your-secret-key-here",  # Use environment variable
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserContext:
    """Dependency to get current authenticated user"""
    try:
        token_data = jwt_manager.verify_token(credentials.credentials)
        
        # Convert to UserContext
        roles = [Role(role) for role in token_data.roles if role in Role.__members__.values()]
        
        user_context = UserContext(
            user_id=token_data.user_id,
            organization_id=token_data.organization_id,
            roles=roles,
            permissions=set(),  # Will be populated by RBAC manager
            is_active=token_data.is_active,
            is_verified=token_data.is_verified
        )
        
        # Get permissions from RBAC manager
        user_context.permissions = rbac_manager.get_user_permissions(user_context)
        
        return user_context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_active_user(
    current_user: UserContext = Depends(get_current_user)
) -> UserContext:
    """Dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_verified_user(
    current_user: UserContext = Depends(get_current_user)
) -> UserContext:
    """Dependency to get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user
