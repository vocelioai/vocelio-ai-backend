# Vocelio AI Call Center - Complete Setup Guide

## 🎯 Overview

**Vocelio AI Call Center** is a comprehensive, AI-powered call center platform built on modern microservices architecture. This guide will walk you through setting up the entire platform from scratch.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Architecture](#system-architecture)
3. [Database Setup](#database-setup)
4. [Service Configuration](#service-configuration)
5. [Deployment Guide](#deployment-guide)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Required Software
- **Node.js** (v18 or higher)
- **npm** or **yarn**
- **Git**
- **Railway CLI** (for deployment)
- **Supabase Account** (for database)

### Required Services
- **Supabase** (PostgreSQL database)
- **Railway** (deployment platform)
- **Twilio** (voice communications)
- **OpenAI** (AI capabilities)
- **ElevenLabs** (text-to-speech)

### System Requirements
- **Minimum**: 2GB RAM, 2 CPU cores
- **Recommended**: 4GB RAM, 4 CPU cores
- **Storage**: 10GB available space

## 🏗️ System Architecture

```
Vocelio AI Call Center Architecture
├── 🌐 API Gateway (Port 3000)
├── 🎤 Voice Service (Port 3001)
├── 📞 Call Service (Port 3002)
├── 🎯 Campaign Service (Port 3003)
├── 📊 Analytics Service (Port 3004)
├── 👤 User Service (Port 3005)
├── 🤖 AI Service (Port 3006)
├── 📱 Dashboard (Port 3007)
└── 🗄️ Supabase Database
```

### Service Responsibilities

#### API Gateway
- **Purpose**: Central routing and authentication
- **Port**: 3000
- **Dependencies**: All services
- **Key Features**: Rate limiting, JWT authentication, request routing

#### Voice Service
- **Purpose**: Text-to-speech, voice cloning, voice recognition
- **Port**: 3001
- **Dependencies**: ElevenLabs, OpenAI Whisper
- **Key Features**: Multi-provider TTS, voice lab, voice marketplace

#### Call Service
- **Purpose**: Call management and Twilio integration
- **Port**: 3002
- **Dependencies**: Twilio, Voice Service
- **Key Features**: Call routing, real-time tracking, conversation analysis

#### Campaign Service
- **Purpose**: Campaign management and optimization
- **Port**: 3003
- **Dependencies**: Call Service, AI Service
- **Key Features**: AI optimization, A/B testing, lead management

#### Analytics Service
- **Purpose**: Real-time analytics and reporting
- **Port**: 3004
- **Dependencies**: All services, Supabase
- **Key Features**: Real-time dashboards, custom reports, performance metrics

#### User Service
- **Purpose**: User management and authentication
- **Port**: 3005
- **Dependencies**: Supabase
- **Key Features**: Multi-tenant architecture, RBAC, user profiles

#### AI Service
- **Purpose**: AI-powered features and optimization
- **Port**: 3006
- **Dependencies**: OpenAI, Voice Service
- **Key Features**: Conversation analysis, performance optimization, predictive analytics

#### Dashboard
- **Purpose**: Web-based user interface
- **Port**: 3007
- **Dependencies**: API Gateway
- **Key Features**: Campaign management, real-time monitoring, analytics visualization

## 🗄️ Database Setup

### Step 1: Create Supabase Project
1. Go to [Supabase](https://supabase.com)
2. Create new project
3. Note your project URL and API keys
4. Enable real-time subscriptions

### Step 2: Execute Database Schema
1. Open Supabase SQL Editor
2. Execute `SUPABASE_COMPLETE_SCHEMA.sql` (creates all tables)
3. Execute `SUPABASE_LOGIC_FUNCTIONS.sql` (creates functions and triggers)

### Step 3: Configure Row Level Security (RLS)
```sql
-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
-- ... (RLS is included in the schema file)
```

### Step 4: Set Up Real-time Subscriptions
```sql
-- Enable real-time for critical tables
ALTER PUBLICATION supabase_realtime ADD TABLE calls;
ALTER PUBLICATION supabase_realtime ADD TABLE campaigns;
ALTER PUBLICATION supabase_realtime ADD TABLE realtime_metrics;
```

## ⚙️ Service Configuration

### Environment Variables Template

Create `.env` file with the following variables:

```env
# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=your_supabase_database_url

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=24h

# API Configuration
API_GATEWAY_URL=http://localhost:3000
VOICE_SERVICE_URL=http://localhost:3001
CALL_SERVICE_URL=http://localhost:3002
CAMPAIGN_SERVICE_URL=http://localhost:3003
ANALYTICS_SERVICE_URL=http://localhost:3004
USER_SERVICE_URL=http://localhost:3005
AI_SERVICE_URL=http://localhost:3006

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
TWILIO_WEBHOOK_URL=your_webhook_url

# AI Service Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_DEFAULT_VOICE=your_default_voice_id

# Additional TTS Providers
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
GOOGLE_CLOUD_KEY=your_google_cloud_key

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# Email Configuration
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASS=your_smtp_password
FROM_EMAIL=noreply@yourcompany.com

# Webhook Configuration
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_TIMEOUT=30000

# Rate Limiting
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX_REQUESTS=100

# File Storage (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=info

# Security
CORS_ORIGIN=http://localhost:3007
HELMET_ENABLED=true
BCRYPT_ROUNDS=12

# Features
VOICE_CLONING_ENABLED=true
REAL_TIME_ANALYTICS=true
WEBHOOK_ENABLED=true
```

## 🚀 Deployment Guide

### Option 1: Automated Deployment

```bash
# Clone the repository
git clone https://github.com/yourusername/vocelio-backend.git
cd vocelio-backend

# Run automated deployment
scripts/deploy.bat  # Windows
# or
scripts/deploy.sh   # Linux/Mac
```

### Option 2: Manual Deployment

#### Step 1: Install Dependencies
```bash
npm install
```

#### Step 2: Build the Project
```bash
npm run build
```

#### Step 3: Run Tests
```bash
npm run test
```

#### Step 4: Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway create vocelio-ai-call-center

# Deploy
railway up
```

### Step 5: Configure Environment Variables
1. Go to Railway dashboard
2. Select your project
3. Go to Variables tab
4. Add all environment variables from the template

## 🔧 Service Configuration

### API Gateway Configuration

The API Gateway handles routing and authentication:

```javascript
// config/gateway.js
module.exports = {
  port: process.env.PORT || 3000,
  services: {
    voice: process.env.VOICE_SERVICE_URL,
    call: process.env.CALL_SERVICE_URL,
    campaign: process.env.CAMPAIGN_SERVICE_URL,
    analytics: process.env.ANALYTICS_SERVICE_URL,
    user: process.env.USER_SERVICE_URL,
    ai: process.env.AI_SERVICE_URL
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
  }
};
```

### Voice Service Configuration

Configure TTS providers and voice settings:

```javascript
// config/voice.js
module.exports = {
  providers: {
    elevenlabs: {
      enabled: true,
      apiKey: process.env.ELEVENLABS_API_KEY,
      defaultVoice: process.env.ELEVENLABS_DEFAULT_VOICE
    },
    azure: {
      enabled: true,
      key: process.env.AZURE_SPEECH_KEY,
      region: process.env.AZURE_SPEECH_REGION
    },
    google: {
      enabled: true,
      keyFile: process.env.GOOGLE_CLOUD_KEY
    }
  },
  features: {
    voiceCloning: process.env.VOICE_CLONING_ENABLED === 'true',
    voiceMarketplace: true,
    realtimeGeneration: true
  }
};
```

### Call Service Configuration

Configure Twilio and call handling:

```javascript
// config/call.js
module.exports = {
  twilio: {
    accountSid: process.env.TWILIO_ACCOUNT_SID,
    authToken: process.env.TWILIO_AUTH_TOKEN,
    phoneNumber: process.env.TWILIO_PHONE_NUMBER,
    webhookUrl: process.env.TWILIO_WEBHOOK_URL
  },
  features: {
    recording: true,
    transcription: true,
    realtimeAnalysis: true
  },
  limits: {
    maxConcurrentCalls: 100,
    maxCallDuration: 3600 // 1 hour
  }
};
```

## 📊 Testing

### Unit Tests
```bash
# Run all tests
npm run test

# Run specific service tests
npm run test:voice
npm run test:call
npm run test:campaign
```

### Integration Tests
```bash
# Run integration tests
npm run test:integration

# Test specific endpoints
npm run test:api
```

### Load Tests
```bash
# Install k6 (load testing tool)
npm install -g k6

# Run load tests
k6 run tests/load/api-load-test.js
```

### Manual Testing Endpoints

#### Health Check
```bash
curl http://localhost:3000/health
```

#### Authentication
```bash
# Register user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

#### Voice Generation
```bash
# Generate voice (requires auth token)
curl -X POST http://localhost:3000/api/voice/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voiceId":"voice_id_here"}'
```

## 📈 Monitoring

### Application Monitoring

The platform includes built-in monitoring:

1. **Health Checks**: All services expose `/health` endpoints
2. **Metrics Collection**: Real-time performance metrics
3. **Error Tracking**: Comprehensive error logging
4. **Performance Monitoring**: Response time and throughput tracking

### Database Monitoring

Monitor your Supabase database:

```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

-- Monitor table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check performance stats
SELECT * FROM pg_stat_user_tables;
```

### Log Monitoring

View application logs:

```bash
# Railway logs
railway logs

# Local development
npm run logs

# View specific service logs
npm run logs:voice
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connectivity
psql "postgresql://user:pass@host:port/dbname"

# Verify environment variables
echo $SUPABASE_URL
echo $DATABASE_URL
```

#### 2. Service Communication Issues
```bash
# Check service health
curl http://localhost:3001/health  # Voice Service
curl http://localhost:3002/health  # Call Service
curl http://localhost:3003/health  # Campaign Service
```

#### 3. Authentication Issues
```bash
# Verify JWT secret
echo $JWT_SECRET

# Test token generation
curl -X POST http://localhost:3000/api/auth/test-token
```

#### 4. Twilio Integration Issues
```bash
# Test Twilio credentials
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Calls.json" \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
```

#### 5. Voice Generation Issues
```bash
# Test ElevenLabs API
curl -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### Performance Optimization

#### Database Optimization
```sql
-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_calls_performance ON calls(created_at, status, campaign_id);
CREATE INDEX CONCURRENTLY idx_prospects_performance ON prospects(created_at, status, campaign_id);

-- Update table statistics
ANALYZE calls;
ANALYZE prospects;
ANALYZE campaigns;
```

#### Application Optimization
```javascript
// Enable caching
const redis = require('redis');
const client = redis.createClient(process.env.REDIS_URL);

// Use connection pooling
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

### Error Codes and Solutions

| Error Code | Description | Solution |
|------------|-------------|----------|
| AUTH_001 | Invalid JWT token | Refresh token or re-authenticate |
| DB_001 | Database connection failed | Check database credentials and connectivity |
| VOICE_001 | TTS generation failed | Verify API keys and text input |
| CALL_001 | Twilio API error | Check Twilio credentials and phone number |
| CAMPAIGN_001 | Campaign not found | Verify campaign ID and permissions |

### Debug Mode

Enable debug logging:

```bash
# Set debug environment
export LOG_LEVEL=debug
export DEBUG=vocelio:*

# Run with debug output
npm run dev:debug
```

## 📚 API Reference

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout

### Voice Service Endpoints
- `GET /api/voice/voices` - List available voices
- `POST /api/voice/generate` - Generate speech from text
- `POST /api/voice/clone` - Clone voice from audio sample
- `GET /api/voice/marketplace` - Browse voice marketplace

### Call Service Endpoints
- `POST /api/calls` - Initiate new call
- `GET /api/calls/:id` - Get call details
- `PUT /api/calls/:id` - Update call status
- `GET /api/calls/active` - List active calls

### Campaign Service Endpoints
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create new campaign
- `GET /api/campaigns/:id` - Get campaign details
- `PUT /api/campaigns/:id` - Update campaign
- `DELETE /api/campaigns/:id` - Delete campaign

### Analytics Service Endpoints
- `GET /api/analytics/dashboard` - Dashboard overview
- `GET /api/analytics/calls` - Call analytics
- `GET /api/analytics/campaigns` - Campaign analytics
- `GET /api/analytics/agents` - Agent performance

## 🚀 Getting Started Checklist

- [ ] Prerequisites installed
- [ ] Supabase project created
- [ ] Database schema executed
- [ ] Environment variables configured
- [ ] Services deployed
- [ ] Health checks passing
- [ ] Authentication working
- [ ] Test call successful
- [ ] Dashboard accessible
- [ ] Monitoring enabled

## 📞 Support

### Documentation
- [API Documentation](./API_REFERENCE.md)
- [Service Guides](./services/)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: General questions and community support

### Enterprise Support
For enterprise customers, we provide:
- 24/7 technical support
- Dedicated implementation assistance
- Custom feature development
- Performance optimization consultations

---

**🔥 Your Vocelio AI Call Center is now ready to revolutionize voice communications!**

This guide provides everything needed to set up and run the platform. For additional help, refer to the specific service guides in the `/docs` directory.
