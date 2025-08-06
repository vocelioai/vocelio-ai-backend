# API Reference - Vocelio AI Call Center

## 🌐 Overview

This document provides comprehensive API reference for all Vocelio AI Call Center services. All APIs follow RESTful conventions and use JSON for request/response payloads.

## 🔐 Authentication

### JWT Token Authentication

All API endpoints require authentication using JWT tokens in the Authorization header:

```http
Authorization: Bearer {your_jwt_token}
```

### Obtaining Authentication Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_here",
    "expires_in": 86400,
    "user": {
      "id": "user_12345",
      "email": "user@example.com",
      "organization_id": "org_67890"
    }
  }
}
```

## 🏗️ Base URLs

### Production
```
https://api.vocelio.ai
```

### Staging
```
https://api-staging.vocelio.ai
```

### Development
```
http://localhost:3000
```

## 📝 Request/Response Format

### Standard Request Headers
```http
Content-Type: application/json
Authorization: Bearer {jwt_token}
X-API-Version: v1
```

### Standard Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "timestamp": "2024-01-15T14:00:00Z",
    "request_id": "req_12345",
    "version": "v1"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // Additional error details
    }
  },
  "meta": {
    "timestamp": "2024-01-15T14:00:00Z",
    "request_id": "req_12345"
  }
}
```

## 🔍 Pagination

For list endpoints, use pagination parameters:

```http
GET /api/resource?page=1&limit=20&sort=created_at&order=desc
```

**Pagination Response:**
```json
{
  "success": true,
  "data": [
    // Array of resources
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 500,
    "pages": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🎤 Voice Service API

### Base Path: `/api/voice`

#### List Voices
```http
GET /api/voice/voices
```

**Query Parameters:**
- `provider` (string): Filter by provider
- `language` (string): Filter by language code
- `gender` (string): male, female, neutral
- `category` (string): professional, conversational, narrative

**Response:**
```json
{
  "success": true,
  "data": {
    "voices": [
      {
        "id": "voice_12345",
        "name": "Professional Sarah",
        "provider": "elevenlabs",
        "language": "en-US",
        "gender": "female",
        "category": "professional",
        "sample_url": "https://samples.vocelio.ai/voice_12345.mp3",
        "settings": {
          "stability": 0.5,
          "similarity_boost": 0.75
        }
      }
    ]
  }
}
```

#### Generate Speech
```http
POST /api/voice/generate
Content-Type: application/json

{
  "text": "Hello, this is a test message",
  "voice_id": "voice_12345",
  "settings": {
    "stability": 0.6,
    "similarity_boost": 0.8
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "audio_url": "https://audio.vocelio.ai/generated_12345.mp3",
    "duration": 3.2,
    "characters_used": 28,
    "cost": 0.0012
  }
}
```

#### Clone Voice
```http
POST /api/voice/clone
Content-Type: multipart/form-data

Form Data:
- audio_file: [audio file]
- voice_name: "My Custom Voice"
- description: "Professional male voice"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "voice_id": "cloned_voice_12345",
    "status": "training",
    "estimated_completion": "2024-01-15T15:00:00Z"
  }
}
```

## 📞 Call Service API

### Base Path: `/api/calls`

#### Initiate Call
```http
POST /api/calls
Content-Type: application/json

{
  "campaign_id": "campaign_12345",
  "phone_number": "+1234567890",
  "agent_id": "agent_67890",
  "settings": {
    "recording": true,
    "transcription": true,
    "max_duration": 1800
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "call_id": "call_12345",
    "status": "initiated",
    "twilio_call_sid": "CA1234567890abcdef",
    "created_at": "2024-01-15T14:00:00Z"
  }
}
```

#### Get Call Details
```http
GET /api/calls/{call_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "call_id": "call_12345",
    "status": "completed",
    "phone_number": "+1234567890",
    "duration": 205,
    "cost": 0.0662,
    "recording_url": "https://recordings.vocelio.ai/call_12345.mp3",
    "transcription": "Full call transcription...",
    "analysis": {
      "sentiment": "positive",
      "conversion": true,
      "quality_score": 4.6
    }
  }
}
```

#### List Calls
```http
GET /api/calls
```

**Query Parameters:**
- `status` (string): initiated, ringing, in_progress, completed, failed
- `campaign_id` (string): Filter by campaign
- `date_from` (string): ISO date string
- `date_to` (string): ISO date string

#### Update Call
```http
PUT /api/calls/{call_id}
Content-Type: application/json

{
  "status": "completed",
  "disposition": "interested",
  "customer_satisfaction": 4.5,
  "agent_notes": "Customer interested in premium package"
}
```

#### Get Active Calls
```http
GET /api/calls/active
```

**Response:**
```json
{
  "success": true,
  "data": {
    "active_calls": [
      {
        "call_id": "call_12345",
        "status": "in_progress",
        "duration": 120,
        "quality_score": 4.5
      }
    ],
    "summary": {
      "total_active": 15,
      "average_duration": 180
    }
  }
}
```

## 🎯 Campaign Service API

### Base Path: `/api/campaigns`

#### Create Campaign
```http
POST /api/campaigns
Content-Type: application/json

{
  "name": "Q1 Product Launch",
  "campaign_type": "outbound_sales",
  "settings": {
    "max_calls_per_day": 500,
    "max_attempts_per_prospect": 3
  },
  "schedule": {
    "start_date": "2024-01-20T09:00:00Z",
    "end_date": "2024-02-20T17:00:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "name": "Q1 Product Launch",
    "status": "draft",
    "created_at": "2024-01-15T14:00:00Z"
  }
}
```

#### Get Campaign
```http
GET /api/campaigns/{campaign_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_12345",
    "name": "Q1 Product Launch",
    "status": "active",
    "progress": {
      "total_prospects": 5000,
      "contacted": 1250,
      "progress_percentage": 25.0
    },
    "performance": {
      "success_rate": 85.0,
      "conversion_rate": 17.0,
      "roi": 4.85
    }
  }
}
```

#### List Campaigns
```http
GET /api/campaigns
```

**Query Parameters:**
- `status` (string): draft, active, paused, completed
- `campaign_type` (string): outbound_sales, lead_nurturing, etc.
- `search` (string): Search in name/description

#### Update Campaign
```http
PUT /api/campaigns/{campaign_id}
Content-Type: application/json

{
  "status": "paused",
  "settings": {
    "max_calls_per_day": 750
  }
}
```

#### Upload Leads
```http
POST /api/campaigns/{campaign_id}/leads
Content-Type: multipart/form-data

Form Data:
- file: [CSV file with leads]
- mapping: {"phone": "phone_number", "name": "full_name"}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "import_id": "import_12345",
    "status": "processing",
    "total_rows": 5000
  }
}
```

#### Get Campaign Analytics
```http
GET /api/campaigns/{campaign_id}/analytics
```

**Query Parameters:**
- `date_from` (string): Start date
- `date_to` (string): End date
- `granularity` (string): hour, day, week

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_calls": 1250,
      "success_rate": 85.04,
      "conversion_rate": 17.04,
      "total_cost": 812.50,
      "revenue": 21300.00
    },
    "time_series": [
      {
        "timestamp": "2024-01-20T09:00:00Z",
        "calls": 45,
        "success_rate": 86.7
      }
    ]
  }
}
```

## 📊 Analytics Service API

### Base Path: `/api/analytics`

#### Dashboard Overview
```http
GET /api/analytics/dashboard
```

**Query Parameters:**
- `date_from` (string): Start date
- `date_to` (string): End date

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_calls": 5250,
      "success_rate": 85.2,
      "total_revenue": 125000.00,
      "active_campaigns": 12
    },
    "trends": {
      "calls_trend": "+12.5%",
      "success_rate_trend": "+3.2%",
      "revenue_trend": "+18.7%"
    },
    "top_campaigns": [
      {
        "campaign_id": "campaign_123",
        "name": "Q1 Launch",
        "performance": 4.8
      }
    ]
  }
}
```

#### Call Analytics
```http
GET /api/analytics/calls
```

**Query Parameters:**
- `campaign_id` (string): Filter by campaign
- `agent_id` (string): Filter by agent
- `date_from` (string): Start date
- `date_to` (string): End date
- `granularity` (string): hour, day, week

#### Agent Performance
```http
GET /api/analytics/agents
```

**Response:**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "agent_id": "agent_123",
        "name": "John Agent",
        "calls": 156,
        "success_rate": 91.7,
        "conversion_rate": 22.4,
        "performance_score": 4.8
      }
    ],
    "summary": {
      "total_agents": 25,
      "average_performance": 4.3,
      "top_performer": "agent_123"
    }
  }
}
```

#### Real-time Metrics
```http
GET /api/analytics/realtime
```

**Response:**
```json
{
  "success": true,
  "data": {
    "active_calls": 45,
    "calls_today": 1250,
    "success_rate_today": 87.2,
    "queue_size": 28,
    "agents_online": 35
  }
}
```

## 👤 User Service API

### Base Path: `/api/users`

#### Get Current User
```http
GET /api/users/me
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_12345",
    "email": "user@example.com",
    "name": "John User",
    "role": "admin",
    "organization_id": "org_67890",
    "permissions": ["campaigns.create", "calls.view"],
    "preferences": {
      "timezone": "America/New_York",
      "notifications": true
    }
  }
}
```

#### Update User Profile
```http
PUT /api/users/me
Content-Type: application/json

{
  "name": "John Updated",
  "preferences": {
    "timezone": "America/Los_Angeles"
  }
}
```

#### List Organization Users
```http
GET /api/users
```

**Query Parameters:**
- `role` (string): Filter by role
- `status` (string): active, inactive
- `search` (string): Search by name/email

#### Create User
```http
POST /api/users
Content-Type: application/json

{
  "email": "newuser@example.com",
  "name": "New User",
  "role": "agent",
  "password": "temp_password"
}
```

#### Update User
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
  "role": "manager",
  "status": "active"
}
```

## 🤖 AI Service API

### Base Path: `/api/ai`

#### Analyze Conversation
```http
POST /api/ai/analyze
Content-Type: application/json

{
  "call_id": "call_12345",
  "transcript": "Full conversation transcript...",
  "analysis_types": ["sentiment", "intent", "keywords"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "call_id": "call_12345",
    "sentiment": {
      "overall": "positive",
      "score": 0.75
    },
    "intent": {
      "primary": "product_inquiry",
      "confidence": 0.89
    },
    "keywords": ["pricing", "features", "demo"],
    "summary": "Customer expressed strong interest in product features"
  }
}
```

#### Generate Optimization Suggestions
```http
POST /api/ai/optimize
Content-Type: application/json

{
  "campaign_id": "campaign_12345",
  "optimization_type": "performance"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "type": "timing",
        "description": "Call between 2-4 PM for 20% better results",
        "confidence": 0.92
      }
    ]
  }
}
```

## 🔔 Webhook Events

### Webhook Configuration
```http
POST /api/webhooks
Content-Type: application/json

{
  "url": "https://yourapp.com/webhooks/vocelio",
  "events": ["call.completed", "campaign.finished"],
  "secret": "your_webhook_secret"
}
```

### Event Types

- `call.initiated` - Call has been started
- `call.answered` - Call was answered
- `call.completed` - Call finished successfully
- `call.failed` - Call failed to connect
- `campaign.started` - Campaign began
- `campaign.paused` - Campaign was paused
- `campaign.completed` - Campaign finished
- `lead.imported` - Leads successfully imported
- `recording.ready` - Call recording available
- `transcription.complete` - Transcription finished

### Webhook Payload Example
```json
{
  "event": "call.completed",
  "timestamp": "2024-01-15T14:03:30Z",
  "data": {
    "call_id": "call_12345",
    "status": "completed",
    "duration": 205,
    "disposition": "interested"
  },
  "signature": "sha256=..."
}
```

## 🔒 Rate Limiting

All API endpoints are rate limited:

- **Standard Plan**: 1000 requests/hour
- **Professional Plan**: 5000 requests/hour  
- **Enterprise Plan**: 25000 requests/hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
```

## ⚠️ Error Codes

### Authentication Errors
- `AUTH_001` - Invalid or missing JWT token
- `AUTH_002` - Token expired
- `AUTH_003` - Insufficient permissions

### Validation Errors
- `VALIDATION_001` - Required field missing
- `VALIDATION_002` - Invalid field format
- `VALIDATION_003` - Field value out of range

### Resource Errors
- `RESOURCE_001` - Resource not found
- `RESOURCE_002` - Resource already exists
- `RESOURCE_003` - Resource cannot be modified

### Service Errors
- `SERVICE_001` - External service unavailable
- `SERVICE_002` - Service rate limit exceeded
- `SERVICE_003` - Service configuration error

### System Errors
- `SYSTEM_001` - Internal server error
- `SYSTEM_002` - Database connection error
- `SYSTEM_003` - Network timeout

## 🧪 Testing APIs

### Using cURL

```bash
# Get authentication token
curl -X POST https://api.vocelio.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Make authenticated request
curl -X GET https://api.vocelio.ai/api/campaigns \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Postman

1. Import the Vocelio API collection
2. Set environment variables for base URL and token
3. Use the authentication endpoint to get a token
4. Test other endpoints with the token

### SDKs and Libraries

**JavaScript/Node.js:**
```javascript
const VocelioAPI = require('@vocelio/api-client');

const client = new VocelioAPI({
  apiKey: 'your_api_key',
  baseURL: 'https://api.vocelio.ai'
});

// List campaigns
const campaigns = await client.campaigns.list();
```

**Python:**
```python
from vocelio import VocelioClient

client = VocelioClient(api_key='your_api_key')

# Create campaign
campaign = client.campaigns.create({
    'name': 'My Campaign',
    'campaign_type': 'outbound_sales'
})
```

---

**📚 This API reference provides comprehensive documentation for integrating with the Vocelio AI Call Center platform. For additional help, refer to our SDK documentation and examples.**
