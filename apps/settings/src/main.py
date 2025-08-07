"""
Settings Service - Vocelio AI Call Center
Organization and user settings management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings Models
class SettingType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    LIST = "list"

class SettingCategory(str, Enum):
    GENERAL = "general"
    SECURITY = "security"
    NOTIFICATIONS = "notifications"
    BILLING = "billing"
    INTEGRATIONS = "integrations"
    APPEARANCE = "appearance"
    VOICE = "voice"
    ANALYTICS = "analytics"
    COMPLIANCE = "compliance"
    ADVANCED = "advanced"

class OrganizationSetting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    
    # Setting details
    key: str
    value: Union[str, int, float, bool, dict, list]
    setting_type: SettingType
    category: SettingCategory
    
    # Metadata
    display_name: str
    description: Optional[str] = None
    default_value: Union[str, int, float, bool, dict, list]
    
    # Constraints
    required: bool = False
    read_only: bool = False
    encrypted: bool = False
    
    # Validation
    validation_rules: Optional[Dict[str, Any]] = None
    allowed_values: Optional[List[Any]] = None
    
    # Status
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UserSetting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    organization_id: str
    
    # Setting details
    key: str
    value: Union[str, int, float, bool, dict, list]
    setting_type: SettingType
    category: SettingCategory
    
    # Metadata
    display_name: str
    description: Optional[str] = None
    default_value: Union[str, int, float, bool, dict, list]
    
    # Status
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Sample data
SAMPLE_ORG_SETTINGS = [
    OrganizationSetting(
        organization_id="org_001",
        key="company_name",
        value="TechCorp Solutions",
        setting_type=SettingType.STRING,
        category=SettingCategory.GENERAL,
        display_name="Company Name",
        description="The official name of your organization",
        default_value="My Company",
        required=True
    ),
    OrganizationSetting(
        organization_id="org_001",
        key="timezone",
        value="America/New_York",
        setting_type=SettingType.STRING,
        category=SettingCategory.GENERAL,
        display_name="Timezone",
        description="Primary timezone for your organization",
        default_value="UTC"
    ),
    OrganizationSetting(
        organization_id="org_001",
        key="max_concurrent_calls",
        value=50,
        setting_type=SettingType.INTEGER,
        category=SettingCategory.VOICE,
        display_name="Max Concurrent Calls",
        description="Maximum number of simultaneous calls allowed",
        default_value=10
    ),
    OrganizationSetting(
        organization_id="org_001",
        key="enable_call_recording",
        value=True,
        setting_type=SettingType.BOOLEAN,
        category=SettingCategory.COMPLIANCE,
        display_name="Enable Call Recording",
        description="Record all incoming and outgoing calls",
        default_value=False
    ),
    OrganizationSetting(
        organization_id="org_001",
        key="notification_settings",
        value={
            "email_alerts": True,
            "sms_alerts": False,
            "webhook_alerts": True
        },
        setting_type=SettingType.JSON,
        category=SettingCategory.NOTIFICATIONS,
        display_name="Notification Settings",
        description="Configure how you receive alerts and notifications",
        default_value={"email_alerts": True, "sms_alerts": False}
    )
]

SAMPLE_USER_SETTINGS = [
    UserSetting(
        user_id="user_001",
        organization_id="org_001",
        key="theme",
        value="dark",
        setting_type=SettingType.STRING,
        category=SettingCategory.APPEARANCE,
        display_name="Theme",
        description="Visual theme preference",
        default_value="light"
    ),
    UserSetting(
        user_id="user_001",
        organization_id="org_001",
        key="notification_email",
        value=True,
        setting_type=SettingType.BOOLEAN,
        category=SettingCategory.NOTIFICATIONS,
        display_name="Email Notifications",
        description="Receive notifications via email",
        default_value=True
    ),
    UserSetting(
        user_id="user_001",
        organization_id="org_001",
        key="dashboard_layout",
        value=["calls", "analytics", "agents", "leads"],
        setting_type=SettingType.LIST,
        category=SettingCategory.APPEARANCE,
        display_name="Dashboard Layout",
        description="Customize dashboard widget order",
        default_value=["calls", "agents", "analytics"]
    )
]

# Global storage
organization_settings: List[OrganizationSetting] = []
user_settings: List[UserSetting] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global organization_settings, user_settings
    
    organization_settings.extend(SAMPLE_ORG_SETTINGS)
    user_settings.extend(SAMPLE_USER_SETTINGS)
    
    logger.info("Sample settings data initialized successfully")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Settings Service", 
    description="Organization and user settings management for Vocelio AI Call Center",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "settings",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Organization Settings Endpoints
@app.get("/organizations/{organization_id}/settings", response_model=List[OrganizationSetting])
async def get_organization_settings(
    organization_id: str,
    category: Optional[SettingCategory] = None
):
    """Get organization settings"""
    filtered_settings = [s for s in organization_settings if s.organization_id == organization_id]
    
    if category:
        filtered_settings = [s for s in filtered_settings if s.category == category]
    
    return filtered_settings

@app.get("/organizations/{organization_id}/settings/{key}", response_model=OrganizationSetting)
async def get_organization_setting(organization_id: str, key: str):
    """Get specific organization setting"""
    setting = next((s for s in organization_settings 
                   if s.organization_id == organization_id and s.key == key), None)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@app.post("/organizations/{organization_id}/settings", response_model=OrganizationSetting)
async def create_organization_setting(organization_id: str, setting_data: OrganizationSetting):
    """Create organization setting"""
    setting_data.organization_id = organization_id
    organization_settings.append(setting_data)
    logger.info(f"Created organization setting: {setting_data.key}")
    return setting_data

@app.put("/organizations/{organization_id}/settings/{key}")
async def update_organization_setting(organization_id: str, key: str, value: Dict[str, Any]):
    """Update organization setting"""
    setting = next((s for s in organization_settings 
                   if s.organization_id == organization_id and s.key == key), None)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    if setting.read_only:
        raise HTTPException(status_code=400, detail="Setting is read-only")
    
    setting.value = value.get("value", setting.value)
    setting.updated_at = datetime.now()
    
    logger.info(f"Updated organization setting: {key}")
    return {"message": "Setting updated successfully"}

# User Settings Endpoints
@app.get("/users/{user_id}/settings", response_model=List[UserSetting])
async def get_user_settings(
    user_id: str,
    category: Optional[SettingCategory] = None
):
    """Get user settings"""
    filtered_settings = [s for s in user_settings if s.user_id == user_id]
    
    if category:
        filtered_settings = [s for s in filtered_settings if s.category == category]
    
    return filtered_settings

@app.get("/users/{user_id}/settings/{key}", response_model=UserSetting)
async def get_user_setting(user_id: str, key: str):
    """Get specific user setting"""
    setting = next((s for s in user_settings 
                   if s.user_id == user_id and s.key == key), None)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@app.post("/users/{user_id}/settings", response_model=UserSetting)
async def create_user_setting(user_id: str, setting_data: UserSetting):
    """Create user setting"""
    setting_data.user_id = user_id
    user_settings.append(setting_data)
    logger.info(f"Created user setting: {setting_data.key}")
    return setting_data

@app.put("/users/{user_id}/settings/{key}")
async def update_user_setting(user_id: str, key: str, value: Dict[str, Any]):
    """Update user setting"""
    setting = next((s for s in user_settings 
                   if s.user_id == user_id and s.key == key), None)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.value = value.get("value", setting.value)
    setting.updated_at = datetime.now()
    
    logger.info(f"Updated user setting: {key}")
    return {"message": "Setting updated successfully"}

# Settings Categories
@app.get("/categories")
async def get_setting_categories():
    """Get available setting categories"""
    return {
        "categories": [
            {
                "name": category.value,
                "display_name": category.value.replace("_", " ").title(),
                "description": f"Settings related to {category.value}"
            }
            for category in SettingCategory
        ]
    }

# Bulk Operations
@app.post("/organizations/{organization_id}/settings/bulk")
async def bulk_update_organization_settings(organization_id: str, updates: Dict[str, Any]):
    """Bulk update organization settings"""
    updated_count = 0
    
    for key, value in updates.items():
        setting = next((s for s in organization_settings 
                       if s.organization_id == organization_id and s.key == key), None)
        if setting and not setting.read_only:
            setting.value = value
            setting.updated_at = datetime.now()
            updated_count += 1
    
    logger.info(f"Bulk updated {updated_count} organization settings")
    return {"message": f"Updated {updated_count} settings successfully"}

@app.post("/users/{user_id}/settings/bulk")
async def bulk_update_user_settings(user_id: str, updates: Dict[str, Any]):
    """Bulk update user settings"""
    updated_count = 0
    
    for key, value in updates.items():
        setting = next((s for s in user_settings 
                       if s.user_id == user_id and s.key == key), None)
        if setting:
            setting.value = value
            setting.updated_at = datetime.now()
            updated_count += 1
    
    logger.info(f"Bulk updated {updated_count} user settings")
    return {"message": f"Updated {updated_count} settings successfully"}

# Settings Analytics
@app.get("/analytics/overview")
async def get_settings_analytics():
    """Get settings analytics overview"""
    return {
        "overview": {
            "total_organization_settings": len(organization_settings),
            "total_user_settings": len(user_settings),
            "categories_in_use": len(set(s.category for s in organization_settings + user_settings))
        },
        "organization_settings_by_category": {
            category.value: len([s for s in organization_settings if s.category == category])
            for category in SettingCategory
        },
        "user_settings_by_category": {
            category.value: len([s for s in user_settings if s.category == category])
            for category in SettingCategory
        },
        "most_common_settings": [
            {"key": "theme", "usage_count": 15},
            {"key": "timezone", "usage_count": 12},
            {"key": "notification_email", "usage_count": 10},
            {"key": "company_name", "usage_count": 8}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8017)
