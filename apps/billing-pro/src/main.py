"""
Billing Pro Service - Vocelio AI Call Center
Comprehensive billing, subscription management, and payment processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, date
from decimal import Decimal
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import hmac
import stripe

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Billing Models
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"

class BillingPeriod(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    WEEKLY = "weekly"
    DAILY = "daily"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"

class UsageMetricType(str, Enum):
    CALLS_MADE = "calls_made"
    MINUTES_USED = "minutes_used"
    SMS_SENT = "sms_sent"
    AI_TOKENS = "ai_tokens"
    STORAGE_GB = "storage_gb"
    API_REQUESTS = "api_requests"
    AGENTS_ACTIVE = "agents_active"
    PHONE_NUMBERS = "phone_numbers"

class PricingModel(str, Enum):
    FLAT_RATE = "flat_rate"
    PER_USAGE = "per_usage"
    TIERED = "tiered"
    VOLUME = "volume"
    FREEMIUM = "freemium"

# Core Models
class UsageMetric(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: UsageMetricType
    value: Decimal
    unit: str  # e.g., "calls", "minutes", "GB", "tokens"
    recorded_at: datetime = Field(default_factory=datetime.now)
    customer_id: str
    subscription_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class PricingTier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    min_usage: Decimal
    max_usage: Optional[Decimal] = None
    price_per_unit: Decimal
    flat_fee: Optional[Decimal] = None

class BillingPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    pricing_model: PricingModel
    base_price: Decimal
    billing_period: BillingPeriod
    
    # Usage-based pricing
    usage_limits: Dict[UsageMetricType, Decimal] = {}
    overage_rates: Dict[UsageMetricType, Decimal] = {}
    
    # Tiered pricing
    pricing_tiers: List[PricingTier] = []
    
    # Features and limits
    features: List[str] = []
    limits: Dict[str, Any] = {}
    
    # Status
    is_active: bool = True
    trial_period_days: Optional[int] = None
    setup_fee: Optional[Decimal] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Basic info
    email: str
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Billing details
    billing_address: Dict[str, str] = {}
    tax_id: Optional[str] = None
    currency: str = "USD"
    
    # Payment methods
    default_payment_method_id: Optional[str] = None
    payment_methods: List[str] = []
    
    # Stripe integration
    stripe_customer_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    plan_id: str
    
    # Subscription details
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    
    # Pricing
    monthly_amount: Decimal
    annual_amount: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    
    # Usage tracking
    usage_this_period: Dict[UsageMetricType, Decimal] = {}
    overage_charges: Decimal = Decimal('0.00')
    
    # Payment
    next_billing_date: datetime
    auto_renew: bool = True
    
    # Stripe integration
    stripe_subscription_id: Optional[str] = None
    stripe_price_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    subscription_id: Optional[str] = None
    
    # Invoice details
    invoice_number: str
    status: PaymentStatus
    due_date: datetime
    paid_date: Optional[datetime] = None
    
    # Amounts
    subtotal: Decimal
    tax_amount: Decimal = Decimal('0.00')
    discount_amount: Decimal = Decimal('0.00')
    total_amount: Decimal
    amount_paid: Decimal = Decimal('0.00')
    amount_due: Decimal
    
    # Line items
    line_items: List[Dict[str, Any]] = []
    
    # Payment tracking
    payment_attempts: int = 0
    last_payment_attempt: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    
    # Stripe integration
    stripe_invoice_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    
    # Metadata
    notes: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PaymentMethod(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    
    # Payment method details
    type: str  # "card", "bank_account", "paypal", etc.
    provider: str = "stripe"
    
    # Card details (if applicable)
    last_four: Optional[str] = None
    brand: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    
    # Status
    is_default: bool = False
    is_verified: bool = False
    
    # Stripe integration
    stripe_payment_method_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Request/Response Models
class CreateCustomerRequest(BaseModel):
    email: str
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    billing_address: Dict[str, str] = {}
    currency: str = "USD"
    metadata: Dict[str, Any] = {}

class CreateSubscriptionRequest(BaseModel):
    customer_id: str
    plan_id: str
    trial_days: Optional[int] = None
    discount_percent: Optional[Decimal] = None
    payment_method_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class UsageReportRequest(BaseModel):
    customer_id: str
    metric_type: UsageMetricType
    value: Decimal
    recorded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class BillingDashboard(BaseModel):
    total_revenue: Decimal
    monthly_recurring_revenue: Decimal
    annual_recurring_revenue: Decimal
    active_subscriptions: int
    churned_subscriptions: int
    average_revenue_per_user: Decimal
    total_customers: int
    overdue_invoices: int
    failed_payments: int

# Global storage (in production, use a database)
customers_db: Dict[str, Customer] = {}
subscriptions_db: Dict[str, Subscription] = {}
invoices_db: Dict[str, Invoice] = {}
billing_plans_db: Dict[str, BillingPlan] = {}
usage_metrics_db: List[UsageMetric] = []
payment_methods_db: Dict[str, PaymentMethod] = {}

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Billing Pro Service...")
    await initialize_default_plans()
    logger.info("Billing Pro Service ready")
    yield
    # Shutdown
    logger.info("Shutting down Billing Pro Service...")

# Initialize FastAPI app
app = FastAPI(
    title="Billing Pro Service",
    description="Comprehensive billing, subscription management, and payment processing for Vocelio AI Call Center",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions
async def initialize_default_plans():
    """Initialize default billing plans"""
    
    # Starter Plan
    starter_plan = BillingPlan(
        name="Starter",
        description="Perfect for small businesses getting started with AI calling",
        pricing_model=PricingModel.FLAT_RATE,
        base_price=Decimal('99.00'),
        billing_period=BillingPeriod.MONTHLY,
        usage_limits={
            UsageMetricType.CALLS_MADE: Decimal('1000'),
            UsageMetricType.MINUTES_USED: Decimal('500'),
            UsageMetricType.AGENTS_ACTIVE: Decimal('3'),
            UsageMetricType.PHONE_NUMBERS: Decimal('1')
        },
        overage_rates={
            UsageMetricType.CALLS_MADE: Decimal('0.15'),
            UsageMetricType.MINUTES_USED: Decimal('0.20')
        },
        features=[
            "Basic AI calling",
            "Call recording",
            "Basic analytics",
            "Email support"
        ],
        trial_period_days=14
    )
    
    # Professional Plan
    professional_plan = BillingPlan(
        name="Professional",
        description="Advanced features for growing businesses",
        pricing_model=PricingModel.FLAT_RATE,
        base_price=Decimal('299.00'),
        billing_period=BillingPeriod.MONTHLY,
        usage_limits={
            UsageMetricType.CALLS_MADE: Decimal('5000'),
            UsageMetricType.MINUTES_USED: Decimal('2500'),
            UsageMetricType.AGENTS_ACTIVE: Decimal('10'),
            UsageMetricType.PHONE_NUMBERS: Decimal('5')
        },
        overage_rates={
            UsageMetricType.CALLS_MADE: Decimal('0.12'),
            UsageMetricType.MINUTES_USED: Decimal('0.18')
        },
        features=[
            "Advanced AI calling",
            "Call recording & transcription",
            "Advanced analytics",
            "CRM integrations",
            "Priority support",
            "Custom voice models"
        ],
        trial_period_days=14
    )
    
    # Enterprise Plan
    enterprise_plan = BillingPlan(
        name="Enterprise",
        description="Unlimited scaling for large organizations",
        pricing_model=PricingModel.FLAT_RATE,
        base_price=Decimal('999.00'),
        billing_period=BillingPeriod.MONTHLY,
        usage_limits={},  # Unlimited
        features=[
            "Unlimited AI calling",
            "Advanced voice lab",
            "Custom integrations",
            "Dedicated support",
            "White-label options",
            "SLA guarantees",
            "Advanced compliance"
        ],
        trial_period_days=30
    )
    
    billing_plans_db[starter_plan.id] = starter_plan
    billing_plans_db[professional_plan.id] = professional_plan
    billing_plans_db[enterprise_plan.id] = enterprise_plan
    
    logger.info("Initialized 3 default billing plans")

def calculate_usage_charges(subscription: Subscription, plan: BillingPlan) -> Decimal:
    """Calculate overage charges for a subscription"""
    total_overage = Decimal('0.00')
    
    for metric_type, usage_amount in subscription.usage_this_period.items():
        limit = plan.usage_limits.get(metric_type, Decimal('0'))
        if limit > 0 and usage_amount > limit:
            overage = usage_amount - limit
            rate = plan.overage_rates.get(metric_type, Decimal('0'))
            total_overage += overage * rate
    
    return total_overage

def generate_invoice_number() -> str:
    """Generate a unique invoice number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"INV-{timestamp}-{random_suffix}"

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "billing-pro",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Customer management endpoints
@app.post("/customers")
async def create_customer(request: CreateCustomerRequest):
    """Create a new customer"""
    try:
        customer = Customer(
            email=request.email,
            company_name=request.company_name,
            first_name=request.first_name,
            last_name=request.last_name,
            billing_address=request.billing_address,
            currency=request.currency,
            metadata=request.metadata
        )
        
        customers_db[customer.id] = customer
        
        logger.info(f"Created customer: {customer.id}")
        return customer
        
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers")
async def list_customers(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all customers with pagination"""
    customers = list(customers_db.values())
    total = len(customers)
    paginated = customers[offset:offset + limit]
    
    return {
        "customers": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer by ID"""
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customers_db[customer_id]

@app.put("/customers/{customer_id}")
async def update_customer(customer_id: str, request: CreateCustomerRequest):
    """Update customer information"""
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer = customers_db[customer_id]
    customer.email = request.email
    customer.company_name = request.company_name
    customer.first_name = request.first_name
    customer.last_name = request.last_name
    customer.billing_address = request.billing_address
    customer.currency = request.currency
    customer.metadata = request.metadata
    customer.updated_at = datetime.now()
    
    return customer

# Billing plans endpoints
@app.get("/plans")
async def list_billing_plans():
    """List all available billing plans"""
    return {
        "plans": list(billing_plans_db.values()),
        "total": len(billing_plans_db)
    }

@app.get("/plans/{plan_id}")
async def get_billing_plan(plan_id: str):
    """Get billing plan by ID"""
    if plan_id not in billing_plans_db:
        raise HTTPException(status_code=404, detail="Billing plan not found")
    
    return billing_plans_db[plan_id]

# Subscription management endpoints
@app.post("/subscriptions")
async def create_subscription(request: CreateSubscriptionRequest):
    """Create a new subscription"""
    try:
        # Validate customer exists
        if request.customer_id not in customers_db:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Validate plan exists
        if request.plan_id not in billing_plans_db:
            raise HTTPException(status_code=404, detail="Billing plan not found")
        
        plan = billing_plans_db[request.plan_id]
        
        # Calculate subscription dates
        start_date = datetime.now()
        trial_end = None
        if request.trial_days or plan.trial_period_days:
            trial_days = request.trial_days or plan.trial_period_days
            trial_end = start_date + timedelta(days=trial_days)
        
        # Calculate period end based on billing period
        if plan.billing_period == BillingPeriod.MONTHLY:
            period_end = start_date + timedelta(days=30)
        elif plan.billing_period == BillingPeriod.QUARTERLY:
            period_end = start_date + timedelta(days=90)
        elif plan.billing_period == BillingPeriod.ANNUALLY:
            period_end = start_date + timedelta(days=365)
        else:
            period_end = start_date + timedelta(days=30)
        
        subscription = Subscription(
            customer_id=request.customer_id,
            plan_id=request.plan_id,
            status=SubscriptionStatus.TRIALING if trial_end else SubscriptionStatus.ACTIVE,
            current_period_start=start_date,
            current_period_end=period_end,
            trial_end=trial_end,
            monthly_amount=plan.base_price,
            next_billing_date=trial_end or period_end,
            discount_percent=request.discount_percent,
            metadata=request.metadata
        )
        
        subscriptions_db[subscription.id] = subscription
        
        logger.info(f"Created subscription: {subscription.id}")
        return subscription
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscriptions")
async def list_subscriptions(
    customer_id: Optional[str] = None,
    status: Optional[SubscriptionStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List subscriptions with optional filtering"""
    subscriptions = list(subscriptions_db.values())
    
    # Apply filters
    if customer_id:
        subscriptions = [s for s in subscriptions if s.customer_id == customer_id]
    if status:
        subscriptions = [s for s in subscriptions if s.status == status]
    
    total = len(subscriptions)
    paginated = subscriptions[offset:offset + limit]
    
    return {
        "subscriptions": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/subscriptions/{subscription_id}")
async def get_subscription(subscription_id: str):
    """Get subscription by ID"""
    if subscription_id not in subscriptions_db:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return subscriptions_db[subscription_id]

@app.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str, at_period_end: bool = True):
    """Cancel a subscription"""
    if subscription_id not in subscriptions_db:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription = subscriptions_db[subscription_id]
    
    if at_period_end:
        subscription.auto_renew = False
        subscription.status = SubscriptionStatus.CANCELED
    else:
        subscription.status = SubscriptionStatus.CANCELED
        subscription.current_period_end = datetime.now()
    
    subscription.updated_at = datetime.now()
    
    logger.info(f"Canceled subscription: {subscription_id}")
    return subscription

# Usage tracking endpoints
@app.post("/usage")
async def report_usage(request: UsageReportRequest):
    """Report usage metrics for billing"""
    try:
        # Validate customer exists
        if request.customer_id not in customers_db:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Find active subscription for customer
        customer_subscriptions = [
            s for s in subscriptions_db.values() 
            if s.customer_id == request.customer_id and s.status == SubscriptionStatus.ACTIVE
        ]
        
        subscription_id = customer_subscriptions[0].id if customer_subscriptions else None
        
        usage_metric = UsageMetric(
            metric_type=request.metric_type,
            value=request.value,
            customer_id=request.customer_id,
            subscription_id=subscription_id,
            recorded_at=request.recorded_at or datetime.now(),
            metadata=request.metadata
        )
        
        usage_metrics_db.append(usage_metric)
        
        # Update subscription usage if applicable
        if subscription_id and subscription_id in subscriptions_db:
            subscription = subscriptions_db[subscription_id]
            current_usage = subscription.usage_this_period.get(request.metric_type, Decimal('0'))
            subscription.usage_this_period[request.metric_type] = current_usage + request.value
            subscription.updated_at = datetime.now()
        
        logger.info(f"Recorded usage: {request.metric_type} = {request.value} for customer {request.customer_id}")
        return usage_metric
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usage/{customer_id}")
async def get_customer_usage(
    customer_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get usage metrics for a customer"""
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Filter usage metrics
    customer_usage = [
        metric for metric in usage_metrics_db 
        if metric.customer_id == customer_id
    ]
    
    # Apply date filters
    if start_date:
        customer_usage = [
            metric for metric in customer_usage 
            if metric.recorded_at.date() >= start_date
        ]
    
    if end_date:
        customer_usage = [
            metric for metric in customer_usage 
            if metric.recorded_at.date() <= end_date
        ]
    
    # Aggregate by metric type
    usage_summary = {}
    for metric in customer_usage:
        metric_type = metric.metric_type
        if metric_type not in usage_summary:
            usage_summary[metric_type] = {
                "total": Decimal('0'),
                "count": 0,
                "unit": metric.unit
            }
        usage_summary[metric_type]["total"] += metric.value
        usage_summary[metric_type]["count"] += 1
    
    return {
        "customer_id": customer_id,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "usage_summary": usage_summary,
        "detailed_metrics": customer_usage
    }

# Invoice management endpoints
@app.get("/invoices")
async def list_invoices(
    customer_id: Optional[str] = None,
    status: Optional[PaymentStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List invoices with optional filtering"""
    invoices = list(invoices_db.values())
    
    # Apply filters
    if customer_id:
        invoices = [i for i in invoices if i.customer_id == customer_id]
    if status:
        invoices = [i for i in invoices if i.status == status]
    
    # Sort by creation date (newest first)
    invoices.sort(key=lambda x: x.created_at, reverse=True)
    
    total = len(invoices)
    paginated = invoices[offset:offset + limit]
    
    return {
        "invoices": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get invoice by ID"""
    if invoice_id not in invoices_db:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoices_db[invoice_id]

@app.post("/invoices/{invoice_id}/pay")
async def pay_invoice(invoice_id: str, payment_method_id: Optional[str] = None):
    """Process payment for an invoice"""
    if invoice_id not in invoices_db:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice = invoices_db[invoice_id]
    
    if invoice.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Invoice already paid")
    
    # Simulate payment processing
    try:
        # In a real implementation, you would integrate with Stripe or another payment processor
        invoice.status = PaymentStatus.PAID
        invoice.paid_date = datetime.now()
        invoice.amount_paid = invoice.total_amount
        invoice.amount_due = Decimal('0.00')
        invoice.payment_method_id = payment_method_id
        invoice.updated_at = datetime.now()
        
        logger.info(f"Processed payment for invoice: {invoice_id}")
        return invoice
        
    except Exception as e:
        invoice.payment_attempts += 1
        invoice.last_payment_attempt = datetime.now()
        invoice.status = PaymentStatus.FAILED
        invoice.updated_at = datetime.now()
        
        logger.error(f"Payment failed for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

# Dashboard and analytics endpoints
@app.get("/dashboard")
async def get_billing_dashboard():
    """Get comprehensive billing dashboard metrics"""
    try:
        # Calculate metrics
        active_subscriptions = [
            s for s in subscriptions_db.values() 
            if s.status == SubscriptionStatus.ACTIVE
        ]
        
        churned_subscriptions = [
            s for s in subscriptions_db.values() 
            if s.status == SubscriptionStatus.CANCELED
        ]
        
        paid_invoices = [
            i for i in invoices_db.values() 
            if i.status == PaymentStatus.PAID
        ]
        
        overdue_invoices = [
            i for i in invoices_db.values() 
            if i.status == PaymentStatus.PENDING and i.due_date < datetime.now()
        ]
        
        failed_payments = [
            i for i in invoices_db.values() 
            if i.status == PaymentStatus.FAILED
        ]
        
        # Calculate revenue metrics
        total_revenue = sum(i.amount_paid for i in paid_invoices)
        monthly_revenue = sum(s.monthly_amount for s in active_subscriptions)
        annual_revenue = monthly_revenue * 12
        
        total_customers = len(customers_db)
        avg_revenue_per_user = total_revenue / max(total_customers, 1)
        
        dashboard = BillingDashboard(
            total_revenue=total_revenue,
            monthly_recurring_revenue=monthly_revenue,
            annual_recurring_revenue=annual_revenue,
            active_subscriptions=len(active_subscriptions),
            churned_subscriptions=len(churned_subscriptions),
            average_revenue_per_user=avg_revenue_per_user,
            total_customers=total_customers,
            overdue_invoices=len(overdue_invoices),
            failed_payments=len(failed_payments)
        )
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/revenue")
async def get_revenue_analytics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    group_by: str = Query("month", regex="^(day|week|month|quarter)$")
):
    """Get revenue analytics with time-based grouping"""
    try:
        # Filter invoices by date range
        filtered_invoices = list(invoices_db.values())
        
        if start_date:
            filtered_invoices = [
                i for i in filtered_invoices 
                if i.created_at.date() >= start_date
            ]
        
        if end_date:
            filtered_invoices = [
                i for i in filtered_invoices 
                if i.created_at.date() <= end_date
            ]
        
        # Group by specified period
        revenue_data = {}
        for invoice in filtered_invoices:
            if invoice.status == PaymentStatus.PAID:
                if group_by == "day":
                    key = invoice.created_at.strftime("%Y-%m-%d")
                elif group_by == "week":
                    key = invoice.created_at.strftime("%Y-W%U")
                elif group_by == "month":
                    key = invoice.created_at.strftime("%Y-%m")
                else:  # quarter
                    quarter = (invoice.created_at.month - 1) // 3 + 1
                    key = f"{invoice.created_at.year}-Q{quarter}"
                
                if key not in revenue_data:
                    revenue_data[key] = {
                        "period": key,
                        "revenue": Decimal('0.00'),
                        "invoice_count": 0
                    }
                
                revenue_data[key]["revenue"] += invoice.amount_paid
                revenue_data[key]["invoice_count"] += 1
        
        # Sort by period
        sorted_data = sorted(revenue_data.values(), key=lambda x: x["period"])
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "group_by": group_by
            },
            "revenue_data": sorted_data,
            "total_revenue": sum(d["revenue"] for d in sorted_data),
            "total_invoices": sum(d["invoice_count"] for d in sorted_data)
        }
        
    except Exception as e:
        logger.error(f"Error generating revenue analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhook endpoint for payment processor
@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: dict,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    try:
        # In a real implementation, verify the webhook signature
        event_type = request.get("type")
        data = request.get("data", {}).get("object", {})
        
        logger.info(f"Received Stripe webhook: {event_type}")
        
        if event_type == "invoice.payment_succeeded":
            # Handle successful payment
            stripe_invoice_id = data.get("id")
            amount_paid = Decimal(str(data.get("amount_paid", 0))) / 100  # Convert from cents
            
            # Find corresponding invoice
            for invoice in invoices_db.values():
                if invoice.stripe_invoice_id == stripe_invoice_id:
                    invoice.status = PaymentStatus.PAID
                    invoice.paid_date = datetime.now()
                    invoice.amount_paid = amount_paid
                    invoice.amount_due = Decimal('0.00')
                    invoice.updated_at = datetime.now()
                    break
        
        elif event_type == "invoice.payment_failed":
            # Handle failed payment
            stripe_invoice_id = data.get("id")
            
            # Find corresponding invoice
            for invoice in invoices_db.values():
                if invoice.stripe_invoice_id == stripe_invoice_id:
                    invoice.status = PaymentStatus.FAILED
                    invoice.payment_attempts += 1
                    invoice.last_payment_attempt = datetime.now()
                    invoice.updated_at = datetime.now()
                    break
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
