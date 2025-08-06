# Campaign Service Guide - Vocelio AI Call Center

## 🎯 Overview

The Campaign Service manages marketing and sales campaigns, including campaign creation, optimization, lead management, A/B testing, automated scheduling, and AI-powered performance optimization. It orchestrates the entire campaign lifecycle from planning to execution and analysis.

## 🏗️ Architecture

```
Campaign Service Architecture
├── 🎯 Campaign Controller (API endpoints)
├── 📊 Campaign Manager (Lifecycle management)
├── 🤖 AI Optimizer (Performance optimization)
├── 👥 Lead Manager (Prospect handling)
├── 📅 Scheduler (Smart scheduling)
├── 🧪 A/B Tester (Campaign testing)
├── 📈 Performance Tracker (Real-time monitoring)
├── 🎮 Campaign Automation (Rule-based actions)
└── 📝 Compliance Monitor (Regulatory compliance)
```

## ⚙️ Configuration

### Environment Variables

```env
# Campaign Service Configuration
CAMPAIGN_SERVICE_PORT=3003
CAMPAIGN_SERVICE_HOST=0.0.0.0

# AI Optimization Configuration
AI_OPTIMIZATION_ENABLED=true
OPTIMIZATION_MODEL=gpt-4
OPTIMIZATION_FREQUENCY=hourly
MIN_CALLS_FOR_OPTIMIZATION=50

# Lead Management Configuration
LEAD_IMPORT_BATCH_SIZE=1000
LEAD_VALIDATION_ENABLED=true
DUPLICATE_DETECTION=true
PHONE_VALIDATION_PROVIDER=twilio_lookup

# Scheduling Configuration
AUTO_SCHEDULING=true
TIMEZONE_DETECTION=true
OPTIMAL_CALL_TIMES=true
RESPECT_BUSINESS_HOURS=true
WEEKEND_CALLING=false

# A/B Testing Configuration
AB_TESTING_ENABLED=true
MIN_SAMPLE_SIZE=100
CONFIDENCE_LEVEL=95
TEST_DURATION_DAYS=7

# Compliance Configuration
DNC_CHECK_BEFORE_CALL=true
CONSENT_TRACKING=true
CALL_FREQUENCY_LIMITS=true
COMPLIANCE_REPORTING=true

# Performance Configuration
MAX_CONCURRENT_CAMPAIGNS=50
MAX_LEADS_PER_CAMPAIGN=100000
CAMPAIGN_BATCH_SIZE=100
WORKER_THREADS=4

# Automation Rules
AUTO_PAUSE_LOW_PERFORMANCE=true
AUTO_SCALE_HIGH_PERFORMANCE=true
SMART_RETRY_LOGIC=true
INTELLIGENT_ROUTING=true
```

### Campaign Configuration

```javascript
// config/campaign.js
module.exports = {
  // Campaign types
  types: {
    outbound_sales: "Outbound sales campaigns",
    lead_nurturing: "Lead nurturing sequences", 
    appointment_setting: "Appointment scheduling",
    customer_service: "Customer service follow-up",
    survey: "Customer surveys",
    event_promotion: "Event promotion calls"
  },
  
  // Default settings
  defaults: {
    max_attempts: 3,
    retry_delay: 24, // hours
    call_timeout: 30, // seconds
    max_duration: 1800, // 30 minutes
    recording: true,
    transcription: true
  },
  
  // Optimization settings
  optimization: {
    enabled: true,
    frequency: 'hourly',
    metrics: ['success_rate', 'conversion_rate', 'cost_per_lead'],
    min_calls: 50,
    confidence_threshold: 0.95
  },
  
  // Compliance settings
  compliance: {
    dnc_check: true,
    consent_required: true,
    max_calls_per_day: 3,
    respect_timezone: true,
    business_hours_only: true
  }
};
```

## 🚀 API Endpoints

### Campaign Management

#### Create Campaign
```http
POST /api/campaigns
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Q1 Product Launch Campaign",
  "description": "Promote new AI features to existing customers",
  "campaign_type": "outbound_sales",
  "status": "draft",
  "settings": {
    "max_calls_per_day": 500,
    "max_attempts_per_prospect": 3,
    "retry_delay_hours": 24,
    "call_timeout_seconds": 30,
    "max_call_duration": 1800,
    "recording_enabled": true,
    "transcription_enabled": true,
    "analysis_enabled": true
  },
  "schedule": {
    "start_date": "2024-01-20T09:00:00Z",
    "end_date": "2024-02-20T17:00:00Z",
    "business_hours": {
      "monday": {"start": "09:00", "end": "17:00"},
      "tuesday": {"start": "09:00", "end": "17:00"},
      "wednesday": {"start": "09:00", "end": "17:00"},
      "thursday": {"start": "09:00", "end": "17:00"},
      "friday": {"start": "09:00", "end": "17:00"},
      "saturday": null,
      "sunday": null
    },
    "timezone": "America/New_York",
    "respect_prospect_timezone": true
  },
  "targeting": {
    "demographics": {
      "age_range": [25, 65],
      "industries": ["technology", "finance", "healthcare"],
      "company_size": ["small", "medium", "enterprise"]
    },
    "behavioral": {
      "previous_engagement": "high",
      "product_interest": "ai_automation",
      "buying_stage": ["consideration", "decision"]
    }
  },
  "script": {
    "script_id": "script_12345",
    "personalization_enabled": true,
    "dynamic_content": true,
    "objection_handling": true
  },
  "voice_settings": {
    "voice_id": "voice_67890",
    "voice_provider": "elevenlabs",
    "speaking_rate": 1.0,
    "pitch": 0.0,
    "stability": 0.5
  },
  "compliance": {
    "dnc_check": true,
    "consent_required": true,
    "recording_notice": true,
    "opt_out_keywords": ["stop", "remove", "unsubscribe"]
  },
  "optimization": {
    "ai_optimization": true,
    "ab_testing": true,
    "real_time_adjustments": true,
    "performance_tracking": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "name": "Q1 Product Launch Campaign",
    "status": "draft",
    "created_at": "2024-01-15T14:00:00Z",
    "estimated_leads": 0,
    "estimated_duration": null,
    "estimated_cost": 0.00,
    "optimization_suggestions": [],
    "next_steps": [
      "Upload leads list",
      "Review and approve script",
      "Set agent assignments",
      "Schedule campaign launch"
    ]
  }
}
```

#### Get Campaign Details
```http
GET /api/campaigns/{campaign_id}
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "name": "Q1 Product Launch Campaign",
    "description": "Promote new AI features to existing customers",
    "campaign_type": "outbound_sales",
    "status": "active",
    "created_at": "2024-01-15T14:00:00Z",
    "started_at": "2024-01-20T09:00:00Z",
    "progress": {
      "total_prospects": 5000,
      "contacted_prospects": 1250,
      "completed_calls": 1100,
      "successful_calls": 935,
      "conversion_count": 187,
      "progress_percentage": 25.0
    },
    "performance": {
      "success_rate": 85.0,
      "conversion_rate": 17.0,
      "average_call_duration": 185.5,
      "cost_per_call": 0.65,
      "cost_per_conversion": 3.82,
      "revenue_generated": 18750.00,
      "roi": 4.85
    },
    "current_metrics": {
      "calls_today": 125,
      "success_rate_today": 87.2,
      "active_calls": 8,
      "queue_size": 15,
      "estimated_completion": "2024-02-18T15:30:00Z"
    },
    "optimization": {
      "last_optimized": "2024-01-21T10:00:00Z",
      "optimization_score": 4.2,
      "suggestions_applied": 3,
      "improvement": "+12% conversion rate"
    },
    "compliance_status": {
      "dnc_violations": 0,
      "consent_rate": 95.5,
      "opt_out_rate": 2.1,
      "compliance_score": 98.5
    }
  }
}
```

#### Update Campaign
```http
PUT /api/campaigns/{campaign_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "paused",
  "settings": {
    "max_calls_per_day": 750
  },
  "optimization": {
    "ai_optimization": true
  }
}
```

#### List Campaigns
```http
GET /api/campaigns
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `status` - Filter by status (draft, active, paused, completed, cancelled)
- `campaign_type` - Filter by campaign type
- `date_from` - Created after date
- `date_to` - Created before date
- `search` - Search in name/description
- `sort` - Sort by (created_at, performance, name)
- `page` - Page number
- `limit` - Results per page

### Lead Management

#### Upload Leads
```http
POST /api/campaigns/{campaign_id}/leads
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `file` - CSV file with leads data
- `mapping` - JSON mapping of CSV columns to fields
- `validation` - Enable phone/email validation
- `duplicate_handling` - skip, update, or create_new

**CSV Format Example:**
```csv
first_name,last_name,phone,email,company,title,industry
John,Doe,+1234567890,john@example.com,Tech Corp,CEO,technology
Jane,Smith,+1987654321,jane@company.com,Finance Inc,CFO,finance
```

**Response:**
```json
{
  "success": true,
  "data": {
    "import_id": "import_12345",
    "status": "processing",
    "total_rows": 5000,
    "processed_rows": 0,
    "valid_leads": 0,
    "invalid_leads": 0,
    "duplicates": 0,
    "estimated_completion": "2024-01-15T14:15:00Z",
    "validation_summary": {
      "phone_validation": "enabled",
      "email_validation": "enabled",
      "duplicate_detection": "enabled"
    }
  }
}
```

#### Get Lead Import Status
```http
GET /api/campaigns/{campaign_id}/leads/import/{import_id}
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "import_id": "import_12345",
    "status": "completed",
    "total_rows": 5000,
    "processed_rows": 5000,
    "valid_leads": 4750,
    "invalid_leads": 125,
    "duplicates": 125,
    "completion_time": "2024-01-15T14:12:30Z",
    "validation_results": {
      "phone_validation": {
        "valid": 4800,
        "invalid": 200,
        "issues": ["invalid_format", "disconnected_number"]
      },
      "email_validation": {
        "valid": 4900,
        "invalid": 100,
        "issues": ["invalid_format", "domain_not_found"]
      }
    },
    "error_report_url": "https://api.vocelio.com/reports/import_errors_12345.csv"
  }
}
```

#### List Campaign Leads
```http
GET /api/campaigns/{campaign_id}/leads
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `status` - Filter by status (pending, contacted, completed, do_not_call)
- `disposition` - Filter by call disposition
- `page` - Page number
- `limit` - Results per page

### Campaign Performance & Analytics

#### Get Campaign Analytics
```http
GET /api/campaigns/{campaign_id}/analytics
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `date_from` - Start date for analytics
- `date_to` - End date for analytics  
- `granularity` - hour, day, week
- `metrics` - Specific metrics to include

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "date_range": {
      "start_date": "2024-01-20T00:00:00Z",
      "end_date": "2024-01-22T23:59:59Z"
    },
    "summary": {
      "total_calls": 1250,
      "successful_calls": 1063,
      "success_rate": 85.04,
      "conversion_count": 213,
      "conversion_rate": 17.04,
      "average_duration": 185.5,
      "total_cost": 812.50,
      "revenue_generated": 21300.00,
      "roi": 2.62
    },
    "time_series": [
      {
        "timestamp": "2024-01-20T09:00:00Z",
        "calls": 45,
        "success_rate": 86.7,
        "conversion_rate": 18.2,
        "cost": 29.25,
        "revenue": 910.00
      }
    ],
    "performance_by_hour": [
      {
        "hour": 9,
        "calls": 145,
        "success_rate": 89.7,
        "conversion_rate": 19.3,
        "avg_duration": 195.2
      }
    ],
    "disposition_breakdown": [
      {
        "disposition": "interested",
        "count": 213,
        "percentage": 17.04,
        "conversion_rate": 100.0
      },
      {
        "disposition": "not_interested",
        "count": 487,
        "percentage": 38.96,
        "conversion_rate": 0.0
      },
      {
        "disposition": "callback_requested",
        "count": 125,
        "percentage": 10.0,
        "conversion_rate": 65.0
      }
    ],
    "agent_performance": [
      {
        "agent_id": "agent_123",
        "agent_name": "John Agent",
        "calls": 156,
        "success_rate": 91.7,
        "conversion_rate": 22.4,
        "avg_duration": 205.3
      }
    ]
  }
}
```

#### Get Real-time Campaign Metrics
```http
GET /api/campaigns/{campaign_id}/metrics/realtime
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "status": "active",
    "timestamp": "2024-01-22T15:30:00Z",
    "current_activity": {
      "active_calls": 8,
      "queue_size": 12,
      "agents_online": 15,
      "calls_today": 187,
      "success_rate_today": 88.2
    },
    "progress": {
      "total_prospects": 5000,
      "contacted": 1425,
      "remaining": 3575,
      "completion_percentage": 28.5,
      "estimated_completion": "2024-02-18T16:45:00Z"
    },
    "performance_trends": {
      "success_rate_trend": "+2.3%",
      "conversion_rate_trend": "+5.7%",
      "cost_trend": "-8.1%",
      "velocity_trend": "+12.4%"
    },
    "alerts": [
      {
        "type": "performance",
        "level": "info",
        "message": "Success rate increased by 5% in the last hour"
      }
    ]
  }
}
```

### Campaign Optimization

#### Get Optimization Suggestions
```http
GET /api/campaigns/{campaign_id}/optimization
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "optimization_score": 4.2,
    "last_analyzed": "2024-01-22T14:00:00Z",
    "current_performance": {
      "success_rate": 85.04,
      "conversion_rate": 17.04,
      "cost_per_conversion": 3.81
    },
    "suggestions": [
      {
        "type": "timing_optimization",
        "priority": "high",
        "title": "Optimize Call Timing",
        "description": "Calls made between 2-4 PM show 23% higher success rates",
        "expected_improvement": "15-20% increase in success rate",
        "implementation": {
          "difficulty": "easy",
          "estimated_time": "immediate",
          "action": "Adjust campaign schedule to focus on peak hours"
        },
        "data_confidence": 0.94
      },
      {
        "type": "script_optimization",
        "priority": "medium", 
        "title": "Improve Opening Line",
        "description": "Analysis shows prospects respond better to benefit-focused openings",
        "expected_improvement": "8-12% increase in conversion rate",
        "implementation": {
          "difficulty": "medium",
          "estimated_time": "2 hours",
          "action": "Update script with benefit-focused opening"
        },
        "data_confidence": 0.87
      },
      {
        "type": "voice_optimization",
        "priority": "low",
        "title": "Voice Selection",
        "description": "Professional female voice shows 3% better performance for this audience",
        "expected_improvement": "3-5% increase in engagement",
        "implementation": {
          "difficulty": "easy",
          "estimated_time": "immediate",
          "action": "Switch to recommended voice profile"
        },
        "data_confidence": 0.78
      }
    ],
    "ab_tests": [
      {
        "test_id": "ab_test_123",
        "name": "Opening Line A/B Test",
        "status": "running",
        "progress": 67,
        "current_leader": "variant_b",
        "confidence": 0.92,
        "improvement": "+11.5% conversion rate"
      }
    ]
  }
}
```

#### Apply Optimization
```http
POST /api/campaigns/{campaign_id}/optimization/apply
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "optimizations": [
    {
      "type": "timing_optimization",
      "settings": {
        "peak_hours": ["14:00-16:00", "19:00-21:00"],
        "redistribute_calls": true
      }
    },
    {
      "type": "script_optimization", 
      "settings": {
        "script_version": "v2_benefit_focused",
        "apply_immediately": true
      }
    }
  ],
  "apply_immediately": true,
  "track_performance": true
}
```

### A/B Testing

#### Create A/B Test
```http
POST /api/campaigns/{campaign_id}/ab-tests
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Script Opening Line Test",
  "description": "Test different opening lines for better engagement",
  "test_type": "script",
  "variants": [
    {
      "name": "Control",
      "description": "Current opening line",
      "traffic_percentage": 50,
      "settings": {
        "script_version": "v1_current"
      }
    },
    {
      "name": "Benefit Focused",
      "description": "Lead with key benefit",
      "traffic_percentage": 50,
      "settings": {
        "script_version": "v2_benefit_focused"
      }
    }
  ],
  "success_metric": "conversion_rate",
  "minimum_sample_size": 200,
  "confidence_level": 95,
  "duration_days": 7,
  "auto_winner_selection": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "test_id": "ab_test_123",
    "name": "Script Opening Line Test",
    "status": "active",
    "started_at": "2024-01-22T15:00:00Z",
    "estimated_completion": "2024-01-29T15:00:00Z",
    "variants": [
      {
        "variant_id": "variant_a",
        "name": "Control",
        "traffic_percentage": 50,
        "calls_assigned": 0,
        "current_metrics": null
      },
      {
        "variant_id": "variant_b", 
        "name": "Benefit Focused",
        "traffic_percentage": 50,
        "calls_assigned": 0,
        "current_metrics": null
      }
    ],
    "required_sample_size": 200,
    "current_confidence": 0,
    "winner": null
  }
}
```

#### Get A/B Test Results
```http
GET /api/campaigns/{campaign_id}/ab-tests/{test_id}
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "test_id": "ab_test_123",
    "name": "Script Opening Line Test",
    "status": "completed",
    "started_at": "2024-01-22T15:00:00Z",
    "completed_at": "2024-01-29T15:00:00Z",
    "success_metric": "conversion_rate",
    "confidence_level": 97.5,
    "statistical_significance": true,
    "winner": {
      "variant_id": "variant_b",
      "variant_name": "Benefit Focused",
      "improvement": "+11.5%",
      "confidence": 0.975
    },
    "results": [
      {
        "variant_id": "variant_a",
        "variant_name": "Control",
        "calls": 245,
        "conversions": 35,
        "conversion_rate": 14.29,
        "success_rate": 84.9,
        "avg_duration": 182.3
      },
      {
        "variant_id": "variant_b",
        "variant_name": "Benefit Focused", 
        "calls": 238,
        "conversions": 47,
        "conversion_rate": 19.75,
        "success_rate": 86.1,
        "avg_duration": 195.7
      }
    ],
    "recommendation": {
      "action": "deploy_winner",
      "variant": "variant_b",
      "expected_impact": "+11.5% conversion rate improvement",
      "confidence": "high"
    }
  }
}
```

### Campaign Automation

#### Create Automation Rule
```http
POST /api/campaigns/{campaign_id}/automation
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Auto-pause low performance",
  "description": "Automatically pause campaign if success rate drops below 70%",
  "trigger": {
    "type": "performance_threshold",
    "metric": "success_rate",
    "operator": "less_than",
    "value": 70,
    "time_window": "1_hour",
    "min_calls": 50
  },
  "actions": [
    {
      "type": "pause_campaign",
      "settings": {
        "send_notification": true,
        "notification_channels": ["email", "slack"]
      }
    },
    {
      "type": "send_alert",
      "settings": {
        "message": "Campaign paused due to low success rate",
        "severity": "high"
      }
    }
  ],
  "enabled": true
}
```

#### List Automation Rules
```http
GET /api/campaigns/{campaign_id}/automation
Authorization: Bearer {jwt_token}
```

## 🤖 AI-Powered Features

### Performance Prediction

```http
GET /api/campaigns/{campaign_id}/predictions
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "predictions": {
      "completion_date": {
        "predicted_date": "2024-02-18T16:30:00Z",
        "confidence": 0.87,
        "factors": ["current_velocity", "agent_availability", "lead_quality"]
      },
      "final_performance": {
        "predicted_conversion_rate": 18.5,
        "predicted_success_rate": 86.2,
        "predicted_total_conversions": 925,
        "confidence": 0.82
      },
      "cost_projection": {
        "predicted_total_cost": 3250.00,
        "predicted_cost_per_conversion": 3.51,
        "confidence": 0.91
      },
      "revenue_projection": {
        "predicted_revenue": 92500.00,
        "predicted_roi": 28.46,
        "confidence": 0.78
      }
    },
    "recommendations": [
      "Increase agent allocation to complete 2 days earlier",
      "Optimize call timing to improve conversion rate by 3%",
      "Consider budget reallocation for maximum ROI"
    ]
  }
}
```

### Smart Lead Scoring

```http
POST /api/campaigns/{campaign_id}/leads/score
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "leads": [
    {
      "lead_id": "lead_123",
      "phone": "+1234567890",
      "company": "Tech Corp",
      "industry": "technology",
      "company_size": "enterprise",
      "title": "CEO",
      "previous_engagement": "high"
    }
  ],
  "scoring_model": "conversion_prediction"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scored_leads": [
      {
        "lead_id": "lead_123",
        "lead_score": 85,
        "conversion_probability": 0.73,
        "priority": "high",
        "recommended_timing": "2024-01-23T14:30:00Z",
        "recommended_agent": "agent_456",
        "scoring_factors": [
          {"factor": "company_size", "weight": 0.25, "score": 95},
          {"factor": "title_seniority", "weight": 0.20, "score": 90},
          {"factor": "industry_match", "weight": 0.15, "score": 85},
          {"factor": "engagement_history", "weight": 0.40, "score": 75}
        ]
      }
    ]
  }
}
```

## 📅 Smart Scheduling

### Optimal Time Prediction

```http
GET /api/campaigns/{campaign_id}/optimal-timing
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "optimal_schedule": {
      "best_days": ["tuesday", "wednesday", "thursday"],
      "best_hours": [
        {"start": "10:00", "end": "12:00", "success_rate": 89.2},
        {"start": "14:00", "end": "16:00", "success_rate": 91.5},
        {"start": "19:00", "end": "21:00", "success_rate": 87.8}
      ],
      "avoid_times": [
        {"start": "12:00", "end": "13:00", "reason": "lunch_break"},
        {"start": "17:00", "end": "18:00", "reason": "commute_time"}
      ]
    },
    "timezone_analysis": [
      {
        "timezone": "America/New_York",
        "leads_count": 2500,
        "best_local_times": ["10:00", "14:00", "19:00"],
        "success_rate": 87.3
      },
      {
        "timezone": "America/Los_Angeles", 
        "leads_count": 1800,
        "best_local_times": ["11:00", "15:00", "20:00"],
        "success_rate": 85.1
      }
    ],
    "recommendations": {
      "schedule_adjustment": "Focus 60% of calls between 2-4 PM EST",
      "timezone_strategy": "Stagger calls to respect local business hours",
      "weekly_distribution": "Avoid Mondays and Fridays for initial outreach"
    }
  }
}
```

## 🔒 Compliance Features

### Compliance Dashboard

```http
GET /api/campaigns/{campaign_id}/compliance
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "compliance_score": 98.5,
    "violations": {
      "total": 2,
      "critical": 0,
      "warnings": 2
    },
    "dnc_compliance": {
      "checks_performed": 5000,
      "violations_found": 0,
      "suppressed_calls": 125,
      "compliance_rate": 100.0
    },
    "consent_tracking": {
      "consent_requests": 1250,
      "consent_granted": 1194,
      "consent_rate": 95.5,
      "opt_outs": 26
    },
    "call_frequency": {
      "max_calls_per_prospect": 3,
      "average_calls_per_prospect": 1.8,
      "violations": 0
    },
    "time_restrictions": {
      "business_hours_compliance": 99.8,
      "timezone_compliance": 100.0,
      "weekend_violations": 0
    },
    "recording_compliance": {
      "notice_provided": 100.0,
      "consent_recorded": 95.5,
      "violations": 0
    }
  }
}
```

## 🧪 Testing

### Campaign Simulation

```http
POST /api/campaigns/simulate
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "campaign_config": {
    "lead_count": 1000,
    "agents": 5,
    "calls_per_day": 200,
    "success_rate": 85,
    "conversion_rate": 15
  },
  "simulation_days": 30,
  "scenarios": ["optimistic", "realistic", "pessimistic"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "simulation_results": [
      {
        "scenario": "realistic",
        "total_calls": 6000,
        "successful_calls": 5100,
        "conversions": 765,
        "total_cost": 3900.00,
        "revenue": 76500.00,
        "roi": 19.62,
        "completion_time": 30
      }
    ],
    "recommendations": [
      "Consider adding 2 more agents to complete campaign faster",
      "Budget allocation appears optimal for expected ROI"
    ]
  }
}
```

## 📈 Best Practices

### Campaign Setup
1. **Clear Objectives**: Define specific, measurable goals
2. **Target Audience**: Segment leads for better targeting
3. **Script Quality**: Invest in well-crafted, tested scripts
4. **Compliance First**: Ensure all compliance measures are in place

### Performance Optimization
1. **Data-Driven Decisions**: Use analytics for optimization
2. **Continuous Testing**: Run regular A/B tests
3. **Monitor Real-time**: Track performance throughout the day
4. **Agent Training**: Invest in agent performance improvement

### Lead Management
1. **Quality over Quantity**: Focus on lead quality
2. **Regular Updates**: Keep lead data fresh and accurate
3. **Segmentation**: Use intelligent lead segmentation
4. **Scoring**: Implement AI-powered lead scoring

---

**🎯 Your Campaign Service is ready to manage intelligent, high-converting marketing campaigns with AI-powered optimization!**
