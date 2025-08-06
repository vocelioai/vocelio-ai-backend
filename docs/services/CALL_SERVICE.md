# Call Service Guide - Vocelio AI Call Center

## 📞 Overview

The Call Service manages all call-related operations including call initiation, routing, real-time monitoring, Twilio integration, conversation analysis, and call lifecycle management. It serves as the central hub for voice communications in your AI call center.

## 🏗️ Architecture

```
Call Service Architecture
├── 📞 Call Controller (API endpoints)
├── 🔄 Call Manager (Call lifecycle)
├── 📡 Twilio Integration (Voice provider)
├── 🎯 Call Router (Intelligent routing)
├── 📊 Real-time Monitor (Live tracking)
├── 🎙️ Conversation Analyzer (AI analysis)
├── 📝 Call Logger (Audit & compliance)
└── 🔔 Event Dispatcher (Webhooks & notifications)
```

## ⚙️ Configuration

### Environment Variables

```env
# Call Service Configuration
CALL_SERVICE_PORT=3002
CALL_SERVICE_HOST=0.0.0.0

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://yourapp.com/webhooks/twilio
TWILIO_API_VERSION=2010-04-01

# Call Configuration
MAX_CALL_DURATION=3600
MAX_CONCURRENT_CALLS=100
CALL_TIMEOUT=30
RING_TIMEOUT=45
DEFAULT_CALLER_ID=+1234567890

# Recording Configuration
CALL_RECORDING_ENABLED=true
RECORDING_FORMAT=mp3
RECORDING_CHANNELS=dual
RECORDING_STORAGE=s3
RECORDING_BUCKET=vocelio-recordings

# Transcription Configuration
TRANSCRIPTION_ENABLED=true
TRANSCRIPTION_PROVIDER=openai_whisper
TRANSCRIPTION_LANGUAGE=en-US
REAL_TIME_TRANSCRIPTION=true

# AI Analysis Configuration
CONVERSATION_ANALYSIS=true
SENTIMENT_ANALYSIS=true
INTENT_DETECTION=true
KEYWORD_EXTRACTION=true

# Quality Monitoring
QUALITY_MONITORING=true
QUALITY_THRESHOLD=4.0
AUTO_QUALITY_SCORING=true

# Compliance Configuration
CALL_CONSENT_REQUIRED=true
DNC_CHECK_ENABLED=true
RECORDING_NOTICE=true
COMPLIANCE_LOGGING=true

# Performance Configuration
CALL_QUEUE_SIZE=1000
WORKER_THREADS=4
RETRY_ATTEMPTS=3
RETRY_DELAY=5000
```

### Twilio Configuration

```javascript
// config/twilio.js
module.exports = {
  accountSid: process.env.TWILIO_ACCOUNT_SID,
  authToken: process.env.TWILIO_AUTH_TOKEN,
  phoneNumber: process.env.TWILIO_PHONE_NUMBER,
  
  // Voice settings
  voice: {
    language: 'en-US',
    voice: 'Polly.Joanna',
    timeout: 30,
    record: true,
    transcribe: true
  },
  
  // Webhook configuration
  webhooks: {
    statusCallback: process.env.TWILIO_WEBHOOK_URL + '/status',
    recordingStatusCallback: process.env.TWILIO_WEBHOOK_URL + '/recording',
    transcriptionCallback: process.env.TWILIO_WEBHOOK_URL + '/transcription'
  },
  
  // Security
  validateWebhooks: true,
  webhookSecret: process.env.TWILIO_WEBHOOK_SECRET,
  
  // Features
  features: {
    recording: true,
    transcription: true,
    conferencing: true,
    forwarding: true,
    voicemail: true
  }
};
```

## 🚀 API Endpoints

### Call Management

#### Initiate Call
```http
POST /api/calls
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "campaign_id": "campaign_12345",
  "prospect_id": "prospect_67890",
  "phone_number": "+1234567890",
  "agent_id": "agent_11111",
  "script_id": "script_22222",
  "priority": "normal",
  "scheduled_at": "2024-01-15T14:00:00Z",
  "settings": {
    "recording": true,
    "transcription": true,
    "analysis": true,
    "max_duration": 1800,
    "caller_id": "+1987654321"
  },
  "metadata": {
    "lead_source": "website",
    "previous_calls": 2,
    "customer_value": "high"
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
    "phone_number": "+1234567890",
    "agent_id": "agent_11111",
    "campaign_id": "campaign_12345",
    "created_at": "2024-01-15T14:00:00Z",
    "estimated_duration": 180,
    "call_url": "https://api.twilio.com/calls/CA1234567890abcdef",
    "tracking": {
      "call_id": "call_12345",
      "status_webhook": "https://yourapp.com/webhooks/call/status",
      "real_time_updates": true
    }
  }
}
```

#### Get Call Details
```http
GET /api/calls/{call_id}
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "call_id": "call_12345",
    "twilio_call_sid": "CA1234567890abcdef",
    "status": "completed",
    "phone_number": "+1234567890",
    "agent_id": "agent_11111",
    "campaign_id": "campaign_12345",
    "prospect_id": "prospect_67890",
    "
": "2024-01-15T14:00:00Z",
    "answered_at": "2024-01-15T14:00:05Z",
    "ended_at": "2024-01-15T14:03:30Z",
    "duration": {
      "ring_time": 5,
      "talk_time": 205,
      "total_time": 210
    },
    "outcome": {
      "status": "completed",
      "disposition": "interested",
      "conversion": true,
      "next_action": "schedule_demo",
      "notes": "Customer interested in premium package"
    },
    "quality": {
      "audio_quality": 4.8,
      "connection_quality": 4.9,
      "customer_satisfaction": 4.7,
      "agent_performance": 4.6
    },
    "cost": {
      "call_cost": 0.015,
      "duration_cost": 0.0512,
      "total_cost": 0.0662,
      "currency": "USD"
    },
    "recording": {
      "url": "https://recordings.com/call_12345.mp3",
      "duration": 205,
      "format": "mp3",
      "channels": "dual",
      "size": 1024000
    },
    "transcription": {
      "text": "Hello, this is John from Vocelio...",
      "confidence": 0.95,
      "language": "en-US",
      "url": "https://transcripts.com/call_12345.txt"
    },
    "analysis": {
      "sentiment": {
        "overall": "positive",
        "customer": "interested",
        "agent": "professional",
        "score": 0.75
      },
      "keywords": ["interested", "demo", "pricing", "features"],
      "intent": "purchase_consideration",
      "topics": ["product_features", "pricing", "demo_request"],
      "talk_ratio": {
        "agent": 0.4,
        "customer": 0.6
      }
    }
  }
}
```

#### Update Call Status
```http
PUT /api/calls/{call_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "completed",
  "disposition": "interested",
  "conversion_result": true,
  "customer_satisfaction": 4.5,
  "agent_notes": "Customer very interested in premium features",
  "next_action": "schedule_demo",
  "follow_up_date": "2024-01-20T10:00:00Z",
  "tags": ["hot_lead", "enterprise", "decision_maker"]
}
```

#### List Calls
```http
GET /api/calls
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `status` - Filter by status (initiated, ringing, in_progress, completed, failed)
- `campaign_id` - Filter by campaign
- `agent_id` - Filter by agent
- `date_from` - Start date filter
- `date_to` - End date filter
- `page` - Page number
- `limit` - Results per page

### Real-time Call Monitoring

#### Get Active Calls
```http
GET /api/calls/active
Authorization: Bearer {jwt_token}
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
        "phone_number": "+1234567890",
        "agent_name": "John Agent",
        "duration": 120,
        "quality_score": 4.5,
        "real_time_metrics": {
          "audio_quality": 4.8,
          "connection_stability": 4.9,
          "background_noise": 0.1
        }
      }
    ],
    "summary": {
      "total_active": 15,
      "average_duration": 180,
      "success_rate": 85.5,
      "queue_size": 5
    }
  }
}
```

#### Real-time Call Metrics
```http
GET /api/calls/{call_id}/metrics
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "call_id": "call_12345",
    "status": "in_progress",
    "duration": 120,
    "real_time_metrics": {
      "audio_quality": 4.8,
      "connection_quality": 4.9,
      "background_noise": 0.1,
      "speech_clarity": 4.7,
      "latency": 45
    },
    "conversation_flow": {
      "agent_talk_time": 48,
      "customer_talk_time": 72,
      "silence_periods": 3,
      "interruptions": 1
    },
    "sentiment_tracking": {
      "current_sentiment": "positive",
      "sentiment_history": [
        {"time": 30, "sentiment": "neutral"},
        {"time": 60, "sentiment": "positive"},
        {"time": 90, "sentiment": "positive"},
        {"time": 120, "sentiment": "positive"}
      ]
    }
  }
}
```

### Call Control

#### Hang Up Call
```http
POST /api/calls/{call_id}/hangup
Authorization: Bearer {jwt_token}
```

#### Transfer Call
```http
POST /api/calls/{call_id}/transfer
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "transfer_to": "+1987654321",
  "transfer_type": "warm", // warm, cold, conference
  "reason": "escalation",
  "notes": "Customer requesting supervisor"
}
```

#### Put Call on Hold
```http
POST /api/calls/{call_id}/hold
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "hold_music": "default",
  "hold_message": "Please hold while we connect you",
  "max_hold_time": 300
}
```

### Call Recording & Transcription

#### Get Call Recording
```http
GET /api/calls/{call_id}/recording
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recording_url": "https://recordings.com/call_12345.mp3",
    "duration": 205,
    "format": "mp3",
    "channels": "dual",
    "file_size": 1024000,
    "created_at": "2024-01-15T14:03:30Z",
    "expires_at": "2024-01-15T14:03:30Z",
    "download_url": "https://api.vocelio.com/downloads/recording_12345"
  }
}
```

#### Get Call Transcription
```http
GET /api/calls/{call_id}/transcription
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transcription": {
      "full_text": "Agent: Hello, this is John from Vocelio...",
      "confidence": 0.95,
      "language": "en-US",
      "segments": [
        {
          "speaker": "agent",
          "text": "Hello, this is John from Vocelio AI",
          "start_time": 0,
          "end_time": 3.2,
          "confidence": 0.98
        },
        {
          "speaker": "customer",
          "text": "Hi John, I received your call",
          "start_time": 3.5,
          "end_time": 6.1,
          "confidence": 0.94
        }
      ],
      "summary": "Customer expressed interest in AI call center solution",
      "key_points": [
        "Customer runs a sales team of 15 people",
        "Currently using manual dialing",
        "Interested in automation features",
        "Budget approved for Q1 implementation"
      ]
    }
  }
}
```

## 🎯 Call Routing & Queue Management

### Smart Call Routing

```javascript
// Routing configuration
const routingRules = {
  criteria: {
    agent_skills: "Match agent skills to call requirements",
    agent_availability: "Route to available agents first",
    agent_performance: "Prefer high-performing agents",
    language: "Match customer language preference",
    timezone: "Consider customer timezone",
    call_priority: "Prioritize high-value calls"
  },
  
  algorithms: {
    round_robin: "Distribute calls evenly",
    least_idle: "Route to least idle agent",
    most_skilled: "Route to most skilled agent",
    weighted: "Use performance-based weights"
  },
  
  fallback: {
    queue: true,
    voicemail: true,
    callback: true,
    escalation: true
  }
};
```

### Queue Management

```http
GET /api/calls/queue
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "queue": [
      {
        "call_id": "call_queued_123",
        "phone_number": "+1234567890",
        "campaign_id": "campaign_456",
        "priority": "high",
        "wait_time": 45,
        "estimated_wait": 120,
        "position": 3,
        "callback_requested": false
      }
    ],
    "statistics": {
      "total_queued": 12,
      "average_wait_time": 95,
      "longest_wait": 240,
      "abandonment_rate": 5.2
    }
  }
}
```

## 📊 Call Analytics

### Call Performance Metrics

```http
GET /api/calls/analytics/performance
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `start_date` - Analysis start date
- `end_date` - Analysis end date
- `campaign_id` - Filter by campaign
- `agent_id` - Filter by agent
- `granularity` - hour, day, week, month

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_calls": 1250,
      "successful_calls": 1068,
      "success_rate": 85.44,
      "average_duration": 185.5,
      "total_cost": 156.75,
      "revenue_generated": 12500.00,
      "roi": 7.97
    },
    "by_hour": [
      {
        "hour": "09:00",
        "calls": 45,
        "success_rate": 88.9,
        "avg_duration": 195.2
      }
    ],
    "by_disposition": [
      {
        "disposition": "interested",
        "count": 320,
        "percentage": 25.6,
        "conversion_rate": 75.0
      },
      {
        "disposition": "not_interested", 
        "count": 485,
        "percentage": 38.8,
        "conversion_rate": 0.0
      }
    ],
    "quality_metrics": {
      "average_audio_quality": 4.7,
      "average_customer_satisfaction": 4.3,
      "technical_issues": 2.1
    }
  }
}
```

### Conversation Analysis

```http
GET /api/calls/{call_id}/analysis
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "call_id": "call_12345",
    "analysis": {
      "sentiment_analysis": {
        "overall_sentiment": "positive",
        "customer_sentiment": "interested",
        "agent_sentiment": "professional",
        "sentiment_progression": [
          {"time": 0, "sentiment": "neutral"},
          {"time": 30, "sentiment": "positive"},
          {"time": 60, "sentiment": "very_positive"}
        ]
      },
      "intent_detection": {
        "primary_intent": "product_inquiry",
        "secondary_intents": ["pricing_question", "demo_request"],
        "confidence": 0.89
      },
      "topic_modeling": {
        "main_topics": [
          {"topic": "product_features", "relevance": 0.78},
          {"topic": "pricing", "relevance": 0.65},
          {"topic": "implementation", "relevance": 0.45}
        ]
      },
      "keyword_extraction": {
        "keywords": [
          {"keyword": "automation", "count": 5, "relevance": 0.85},
          {"keyword": "roi", "count": 3, "relevance": 0.72},
          {"keyword": "integration", "count": 4, "relevance": 0.68}
        ]
      },
      "conversation_flow": {
        "talk_time_ratio": {
          "agent": 0.45,
          "customer": 0.55
        },
        "interruptions": 2,
        "silence_periods": 3,
        "pace": "optimal"
      },
      "objection_handling": {
        "objections_raised": [
          {"objection": "price_concern", "handled": true, "technique": "value_demonstration"},
          {"objection": "complexity_concern", "handled": true, "technique": "simplification"}
        ],
        "success_rate": 100
      }
    },
    "coaching_insights": [
      "Excellent rapport building in first 30 seconds",
      "Could improve on asking open-ended questions",
      "Strong closing technique used"
    ],
    "next_actions": [
      "Send demo invitation email",
      "Schedule follow-up call for Friday",
      "Provide pricing documentation"
    ]
  }
}
```

## 🔔 Webhooks & Events

### Webhook Configuration

```javascript
// Webhook events
const webhookEvents = {
  call_initiated: "Call has been initiated",
  call_ringing: "Phone is ringing",
  call_answered: "Call was answered",
  call_completed: "Call has ended successfully",
  call_failed: "Call failed to connect",
  call_no_answer: "No answer received",
  call_busy: "Line was busy",
  recording_available: "Call recording is ready",
  transcription_complete: "Transcription processing complete",
  analysis_complete: "Call analysis finished"
};
```

### Webhook Payload Example

```json
{
  "event": "call_completed",
  "timestamp": "2024-01-15T14:03:30Z",
  "call_id": "call_12345",
  "organization_id": "org_67890",
  "data": {
    "status": "completed",
    "duration": 205,
    "disposition": "interested",
    "conversion": true,
    "quality_score": 4.6,
    "cost": 0.0662,
    "recording_url": "https://recordings.com/call_12345.mp3",
    "transcription_url": "https://transcripts.com/call_12345.txt"
  },
  "signature": "sha256=1234567890abcdef..."
}
```

## 🔒 Compliance & Security

### Do Not Call (DNC) Checking

```http
POST /api/calls/dnc-check
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "phone_numbers": ["+1234567890", "+1987654321"],
  "list_type": "national", // national, internal, both
  "purpose": "marketing" // marketing, transactional, informational
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "phone_number": "+1234567890",
        "is_dnc": false,
        "list_type": "none",
        "can_call": true,
        "last_checked": "2024-01-15T14:00:00Z"
      },
      {
        "phone_number": "+1987654321",
        "is_dnc": true,
        "list_type": "national",
        "can_call": false,
        "registered_date": "2023-05-15T00:00:00Z"
      }
    ]
  }
}
```

### Consent Management

```http
POST /api/calls/{call_id}/consent
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "consent_type": "marketing_calls",
  "consent_given": true,
  "consent_method": "verbal",
  "consent_timestamp": "2024-01-15T14:01:30Z",
  "recording_segment": {
    "start_time": 90,
    "end_time": 105,
    "transcript": "Yes, I consent to receive marketing calls"
  }
}
```

## ⚡ Performance Optimization

### Connection Pooling

```javascript
// Twilio client pool configuration
const twilioPool = {
  minConnections: 5,
  maxConnections: 50,
  idleTimeout: 30000,
  connectionTimeout: 5000,
  retryAttempts: 3,
  retryDelay: 1000
};
```

### Caching Strategy

```javascript
// Call data caching
const cacheStrategy = {
  active_calls: {
    ttl: 60, // 1 minute
    strategy: "real_time"
  },
  call_history: {
    ttl: 3600, // 1 hour
    strategy: "lru"
  },
  agent_status: {
    ttl: 30, // 30 seconds
    strategy: "real_time"
  }
};
```

## 🧪 Testing

### Unit Tests

```bash
# Run call service tests
npm run test:call

# Test specific functionality
npm run test:call:routing
npm run test:call:recording
npm run test:call:analysis
```

### Integration Tests

```bash
# Test Twilio integration
npm run test:twilio

# Test end-to-end call flow
npm run test:e2e:call
```

### Load Testing

```javascript
// k6 load test for call initiation
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '10m', target: 200 },
    { duration: '5m', target: 0 }
  ]
};

export default function() {
  let payload = {
    campaign_id: 'campaign_test',
    phone_number: '+1555' + Math.floor(Math.random() * 1000000).toString().padStart(7, '0'),
    agent_id: 'agent_test'
  };

  let response = http.post('http://localhost:3002/api/calls', JSON.stringify(payload), {
    headers: {
      'Authorization': 'Bearer ' + __ENV.JWT_TOKEN,
      'Content-Type': 'application/json'
    }
  });

  check(response, {
    'call initiated': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 2000
  });
}
```

## 🚨 Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| CALL_001 | Invalid phone number format | Use E.164 format (+1234567890) |
| CALL_002 | Twilio API error | Check Twilio credentials |
| CALL_003 | Agent not available | Assign available agent or queue |
| CALL_004 | DNC violation | Remove number from campaign |
| CALL_005 | Recording failed | Check storage configuration |
| CALL_006 | Transcription timeout | Retry or use alternative provider |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "CALL_002",
    "message": "Twilio authentication failed",
    "details": {
      "twilio_error": "Invalid credentials",
      "error_code": 20003
    },
    "suggestion": "Verify your Twilio Account SID and Auth Token"
  }
}
```

## 📈 Monitoring & Alerts

### Key Metrics to Monitor

- **Call Success Rate**: Percentage of successful calls
- **Average Call Duration**: Mean duration of completed calls  
- **Connection Quality**: Audio and network quality scores
- **Queue Performance**: Wait times and abandonment rates
- **Cost per Call**: Average cost including provider fees
- **Agent Utilization**: Agent availability and productivity

### Alert Configuration

```javascript
// Alert thresholds
const alerts = {
  success_rate: {
    warning: 85,
    critical: 75
  },
  queue_wait_time: {
    warning: 120, // 2 minutes
    critical: 300  // 5 minutes
  },
  connection_quality: {
    warning: 4.0,
    critical: 3.5
  },
  error_rate: {
    warning: 5,
    critical: 10
  }
};
```

---

**📞 Your Call Service is ready to handle high-volume, intelligent voice communications for your AI call center!**
