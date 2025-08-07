"""
White Label Service - Vocelio AI Call Center
White-label branding, customization, and multi-tenant management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import base64
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# White Label Models
class BrandingTheme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    CORPORATE = "corporate"
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    COLORFUL = "colorful"

class TenantType(str, Enum):
    STARTUP = "startup"
    SMB = "smb"
    ENTERPRISE = "enterprise"
    AGENCY = "agency"
    RESELLER = "reseller"

class CustomizationLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    FULL = "full"

class BrandAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_type: str  # "logo", "favicon", "background", "banner"
    file_name: str
    file_url: str
    file_size: int
    mime_type: str
    
    # Metadata
    width: Optional[int] = None
    height: Optional[int] = None
    alt_text: Optional[str] = None
    
    # Status
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ColorScheme(BaseModel):
    primary: str = "#3B82F6"  # Blue
    secondary: str = "#10B981"  # Green
    accent: str = "#F59E0B"  # Yellow
    background: str = "#FFFFFF"  # White
    surface: str = "#F9FAFB"  # Light gray
    text_primary: str = "#111827"  # Dark gray
    text_secondary: str = "#6B7280"  # Medium gray
    border: str = "#E5E7EB"  # Light border
    error: str = "#EF4444"  # Red
    warning: str = "#F59E0B"  # Orange
    success: str = "#10B981"  # Green
    info: str = "#3B82F6"  # Blue

class TypographySettings(BaseModel):
    font_family_primary: str = "Inter, system-ui, sans-serif"
    font_family_secondary: str = "Inter, system-ui, sans-serif"
    font_size_base: str = "16px"
    font_weight_normal: int = 400
    font_weight_medium: int = 500
    font_weight_bold: int = 700
    line_height_base: float = 1.5
    letter_spacing: str = "0px"

class UISettings(BaseModel):
    border_radius: str = "8px"
    shadow_sm: str = "0 1px 2px 0 rgb(0 0 0 / 0.05)"
    shadow_md: str = "0 4px 6px -1px rgb(0 0 0 / 0.1)"
    shadow_lg: str = "0 10px 15px -3px rgb(0 0 0 / 0.1)"
    transition_duration: str = "150ms"
    animation_curve: str = "cubic-bezier(0.4, 0, 0.2, 1)"

class BrandingConfiguration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    
    # Basic branding
    brand_name: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    
    # Theme and styling
    theme: BrandingTheme = BrandingTheme.LIGHT
    color_scheme: ColorScheme = Field(default_factory=ColorScheme)
    typography: TypographySettings = Field(default_factory=TypographySettings)
    ui_settings: UISettings = Field(default_factory=UISettings)
    
    # Assets
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    background_url: Optional[str] = None
    
    # Contact information
    website_url: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    
    # Social media
    social_links: Dict[str, str] = {}  # platform -> url
    
    # Customization
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    
    # Status
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TenantConfiguration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    
    # Tenant details
    name: str
    display_name: str
    subdomain: str
    custom_domain: Optional[str] = None
    
    # Tenant type and settings
    tenant_type: TenantType
    customization_level: CustomizationLevel
    
    # Features enabled
    features_enabled: List[str] = []
    
    # Limits and quotas
    user_limit: Optional[int] = None
    agent_limit: Optional[int] = None
    call_limit: Optional[int] = None
    storage_limit_gb: Optional[int] = None
    
    # Billing
    plan_tier: str = "basic"
    billing_email: Optional[str] = None
    
    # Status
    active: bool = True
    suspended: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Sample data
SAMPLE_TENANTS = [
    TenantConfiguration(
        tenant_id="tenant_001",
        name="TechCorp Solutions",
        display_name="TechCorp AI Assistant",
        subdomain="techcorp",
        custom_domain="ai.techcorp.com",
        tenant_type=TenantType.ENTERPRISE,
        customization_level=CustomizationLevel.FULL,
        features_enabled=["custom_branding", "white_label", "api_access", "advanced_analytics"],
        user_limit=500,
        agent_limit=50,
        call_limit=100000,
        storage_limit_gb=1000,
        plan_tier="enterprise",
        billing_email="billing@techcorp.com"
    ),
    TenantConfiguration(
        tenant_id="tenant_002",
        name="StartupHub Inc",
        display_name="StartupHub Voice AI",
        subdomain="startuphub",
        tenant_type=TenantType.STARTUP,
        customization_level=CustomizationLevel.INTERMEDIATE,
        features_enabled=["basic_branding", "custom_colors"],
        user_limit=50,
        agent_limit=10,
        call_limit=10000,
        storage_limit_gb=100,
        plan_tier="pro",
        billing_email="founders@startuphub.com"
    ),
    TenantConfiguration(
        tenant_id="tenant_003",
        name="Marketing Agency Pro",
        display_name="AgencyPro Call Center",
        subdomain="agencypro",
        tenant_type=TenantType.AGENCY,
        customization_level=CustomizationLevel.ADVANCED,
        features_enabled=["reseller_portal", "client_management", "custom_branding"],
        user_limit=200,
        agent_limit=25,
        call_limit=50000,
        storage_limit_gb=500,
        plan_tier="agency",
        billing_email="admin@agencypro.com"
    )
]

SAMPLE_BRANDING = [
    BrandingConfiguration(
        tenant_id="tenant_001",
        brand_name="TechCorp AI",
        tagline="Intelligent Conversations, Exceptional Results",
        description="Enterprise-grade AI call center solution",
        theme=BrandingTheme.CORPORATE,
        color_scheme=ColorScheme(
            primary="#1E40AF",
            secondary="#059669",
            accent="#DC2626"
        ),
        website_url="https://techcorp.com",
        support_email="support@techcorp.com",
        support_phone="+1-800-TECHCORP",
        social_links={
            "linkedin": "https://linkedin.com/company/techcorp",
            "twitter": "https://twitter.com/techcorp"
        }
    ),
    BrandingConfiguration(
        tenant_id="tenant_002",
        brand_name="StartupHub Voice",
        tagline="Scale your voice operations",
        description="Modern voice AI for growing businesses",
        theme=BrandingTheme.MODERN,
        color_scheme=ColorScheme(
            primary="#8B5CF6",
            secondary="#06B6D4",
            accent="#F59E0B"
        ),
        website_url="https://startuphub.com",
        support_email="help@startuphub.com",
        social_links={
            "twitter": "https://twitter.com/startuphub",
            "discord": "https://discord.gg/startuphub"
        }
    ),
    BrandingConfiguration(
        tenant_id="tenant_003",
        brand_name="AgencyPro",
        tagline="White-label voice solutions for your clients",
        description="Complete call center platform for agencies",
        theme=BrandingTheme.MINIMAL,
        color_scheme=ColorScheme(
            primary="#0F172A",
            secondary="#64748B",
            accent="#0EA5E9"
        ),
        website_url="https://agencypro.com",
        support_email="support@agencypro.com",
        social_links={
            "linkedin": "https://linkedin.com/company/agencypro"
        }
    )
]

# Global storage
tenants: List[TenantConfiguration] = []
branding_configs: List[BrandingConfiguration] = []
brand_assets: List[BrandAsset] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global tenants, branding_configs
    
    tenants.extend(SAMPLE_TENANTS)
    branding_configs.extend(SAMPLE_BRANDING)
    
    logger.info("Sample white-label data initialized successfully")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="White Label Service", 
    description="White-label branding, customization, and multi-tenant management for Vocelio AI Call Center",
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

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "white-label",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Tenant Management Endpoints
@app.get("/tenants", response_model=List[TenantConfiguration])
async def get_tenants(
    tenant_type: Optional[TenantType] = None,
    active_only: bool = True
):
    """Get all tenants with optional filtering"""
    filtered_tenants = tenants
    
    if tenant_type:
        filtered_tenants = [t for t in filtered_tenants if t.tenant_type == tenant_type]
    
    if active_only:
        filtered_tenants = [t for t in filtered_tenants if t.active and not t.suspended]
    
    return filtered_tenants

@app.get("/tenants/{tenant_id}", response_model=TenantConfiguration)
async def get_tenant(tenant_id: str):
    """Get specific tenant configuration"""
    tenant = next((t for t in tenants if t.tenant_id == tenant_id), None)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.post("/tenants", response_model=TenantConfiguration)
async def create_tenant(tenant_data: TenantConfiguration):
    """Create a new tenant"""
    tenants.append(tenant_data)
    logger.info(f"Created new tenant: {tenant_data.name}")
    return tenant_data

@app.put("/tenants/{tenant_id}", response_model=TenantConfiguration)
async def update_tenant(tenant_id: str, updates: Dict[str, Any]):
    """Update tenant configuration"""
    tenant = next((t for t in tenants if t.tenant_id == tenant_id), None)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    for field, value in updates.items():
        if hasattr(tenant, field):
            setattr(tenant, field, value)
    
    tenant.updated_at = datetime.now()
    logger.info(f"Updated tenant: {tenant.name}")
    return tenant

# Branding Configuration Endpoints
@app.get("/branding", response_model=List[BrandingConfiguration])
async def get_branding_configs(tenant_id: Optional[str] = None):
    """Get branding configurations"""
    filtered_configs = branding_configs
    
    if tenant_id:
        filtered_configs = [c for c in filtered_configs if c.tenant_id == tenant_id]
    
    return filtered_configs

@app.get("/branding/{tenant_id}", response_model=BrandingConfiguration)
async def get_tenant_branding(tenant_id: str):
    """Get branding configuration for specific tenant"""
    config = next((c for c in branding_configs if c.tenant_id == tenant_id), None)
    if not config:
        raise HTTPException(status_code=404, detail="Branding configuration not found")
    return config

@app.post("/branding", response_model=BrandingConfiguration)
async def create_branding_config(config_data: BrandingConfiguration):
    """Create branding configuration"""
    branding_configs.append(config_data)
    logger.info(f"Created branding config for tenant: {config_data.tenant_id}")
    return config_data

@app.put("/branding/{tenant_id}", response_model=BrandingConfiguration)
async def update_branding_config(tenant_id: str, updates: Dict[str, Any]):
    """Update branding configuration"""
    config = next((c for c in branding_configs if c.tenant_id == tenant_id), None)
    if not config:
        raise HTTPException(status_code=404, detail="Branding configuration not found")
    
    for field, value in updates.items():
        if hasattr(config, field):
            setattr(config, field, value)
    
    config.updated_at = datetime.now()
    logger.info(f"Updated branding config for tenant: {tenant_id}")
    return config

# Theme and Styling Endpoints
@app.get("/themes")
async def get_available_themes():
    """Get available branding themes"""
    return {
        "themes": [
            {
                "name": theme.value,
                "display_name": theme.value.replace("_", " ").title(),
                "description": f"{theme.value.title()} theme with preset styling"
            }
            for theme in BrandingTheme
        ]
    }

@app.get("/themes/{theme_name}/preview")
async def get_theme_preview(theme_name: str):
    """Get theme preview with sample styling"""
    try:
        theme = BrandingTheme(theme_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    # Sample theme configurations
    theme_configs = {
        BrandingTheme.LIGHT: {
            "colors": ColorScheme(),
            "description": "Clean and bright interface"
        },
        BrandingTheme.DARK: {
            "colors": ColorScheme(
                primary="#60A5FA",
                background="#111827",
                surface="#1F2937",
                text_primary="#F9FAFB",
                text_secondary="#D1D5DB"
            ),
            "description": "Dark theme for reduced eye strain"
        },
        BrandingTheme.CORPORATE: {
            "colors": ColorScheme(
                primary="#1E40AF",
                secondary="#059669",
                accent="#DC2626"
            ),
            "description": "Professional corporate styling"
        }
    }
    
    return {
        "theme": theme.value,
        "config": theme_configs.get(theme, theme_configs[BrandingTheme.LIGHT])
    }

# Asset Management Endpoints
@app.get("/assets", response_model=List[BrandAsset])
async def get_brand_assets(
    tenant_id: Optional[str] = None,
    asset_type: Optional[str] = None
):
    """Get brand assets"""
    filtered_assets = brand_assets
    
    if tenant_id:
        filtered_assets = [a for a in filtered_assets if a.tenant_id == tenant_id]
        
    if asset_type:
        filtered_assets = [a for a in filtered_assets if a.asset_type == asset_type]
    
    return filtered_assets

@app.post("/assets", response_model=BrandAsset)
async def upload_brand_asset(asset_data: BrandAsset):
    """Upload a brand asset"""
    brand_assets.append(asset_data)
    logger.info(f"Uploaded {asset_data.asset_type} asset for tenant: {asset_data.tenant_id}")
    return asset_data

# Custom CSS/JS Endpoints
@app.get("/custom-styles/{tenant_id}")
async def get_custom_styles(tenant_id: str):
    """Get custom CSS for tenant"""
    config = next((c for c in branding_configs if c.tenant_id == tenant_id), None)
    if not config:
        raise HTTPException(status_code=404, detail="Branding configuration not found")
    
    return {
        "custom_css": config.custom_css,
        "custom_js": config.custom_js
    }

@app.put("/custom-styles/{tenant_id}")
async def update_custom_styles(tenant_id: str, styles: Dict[str, str]):
    """Update custom CSS/JS for tenant"""
    config = next((c for c in branding_configs if c.tenant_id == tenant_id), None)
    if not config:
        raise HTTPException(status_code=404, detail="Branding configuration not found")
    
    if "custom_css" in styles:
        config.custom_css = styles["custom_css"]
    
    if "custom_js" in styles:
        config.custom_js = styles["custom_js"]
    
    config.updated_at = datetime.now()
    logger.info(f"Updated custom styles for tenant: {tenant_id}")
    
    return {"message": "Custom styles updated successfully"}

# White Label Analytics
@app.get("/analytics/overview")
async def get_white_label_analytics():
    """Get white-label service analytics"""
    total_tenants = len(tenants)
    active_tenants = len([t for t in tenants if t.active and not t.suspended])
    
    # Tenant type distribution
    type_stats = {}
    for tenant_type in TenantType:
        type_stats[tenant_type.value] = len([t for t in tenants if t.tenant_type == tenant_type])
    
    # Customization level distribution
    customization_stats = {}
    for level in CustomizationLevel:
        customization_stats[level.value] = len([t for t in tenants if t.customization_level == level])
    
    return {
        "overview": {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "suspended_tenants": len([t for t in tenants if t.suspended]),
            "total_brand_configs": len(branding_configs),
            "total_assets": len(brand_assets)
        },
        "tenant_type_distribution": type_stats,
        "customization_level_distribution": customization_stats,
        "popular_themes": [
            {"theme": "corporate", "usage": 8},
            {"theme": "modern", "usage": 6},
            {"theme": "light", "usage": 4},
            {"theme": "minimal", "usage": 3}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8022)
