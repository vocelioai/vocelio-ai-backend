# Quick Start Guide - Vocelio AI Call Center

## 🚀 Get Up and Running in 15 Minutes

This guide will help you set up your Vocelio AI Call Center platform quickly and start making your first AI-powered calls.

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- [ ] **Git** - [Download here](https://git-scm.com/)
- [ ] **Supabase account** - [Sign up here](https://supabase.com)
- [ ] **Twilio account** - [Sign up here](https://twilio.com)
- [ ] **OpenAI API key** - [Get key here](https://platform.openai.com/api-keys)
- [ ] **ElevenLabs account** (optional) - [Sign up here](https://elevenlabs.io)

## ⚡ Quick Setup (15 minutes)

### Step 1: Clone and Install (2 minutes)

```bash
# Clone the repository
git clone https://github.com/vocelio/vocelio-backend.git
cd vocelio-backend

# Install dependencies
npm install
```

### Step 2: Database Setup (5 minutes)

1. **Create Supabase Project**
   - Go to [Supabase](https://supabase.com)
   - Click "New Project"
   - Choose organization and name your project
   - Wait for database to be ready (2-3 minutes)

2. **Get Database Credentials**
   - Go to Settings → API
   - Copy your `Project URL` and `anon public` key
   - Go to Settings → Database
   - Copy your `Connection string`

3. **Setup Database Schema**
   - Open Supabase SQL Editor
   - Copy and paste the contents of `SUPABASE_COMPLETE_SCHEMA.sql`
   - Click "Run" (takes ~30 seconds)
   - Copy and paste the contents of `SUPABASE_LOGIC_FUNCTIONS.sql`
   - Click "Run" (takes ~30 seconds)

### Step 3: Environment Configuration (3 minutes)

Create `.env` file in your project root:

```env
# Database Configuration (REQUIRED)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
DATABASE_URL=your_supabase_database_url

# JWT Configuration (REQUIRED)
JWT_SECRET=your_super_secret_jwt_key_here
JWT_EXPIRES_IN=24h

# Twilio Configuration (REQUIRED for calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# AI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Voice Configuration (OPTIONAL - for better voices)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_DEFAULT_VOICE=21m00Tcm4TlvDq8ikWAM

# Service Ports (DEFAULT - change if needed)
API_GATEWAY_PORT=3000
VOICE_SERVICE_PORT=3001
CALL_SERVICE_PORT=3002
CAMPAIGN_SERVICE_PORT=3003
ANALYTICS_SERVICE_PORT=3004
USER_SERVICE_PORT=3005
AI_SERVICE_PORT=3006
```

### Step 4: Quick Test Run (3 minutes)

```bash
# Build the project
npm run build

# Start all services
npm run dev

# Or start individual services
npm run dev:gateway    # API Gateway (port 3000)
npm run dev:voice      # Voice Service (port 3001)
npm run dev:call       # Call Service (port 3002)
npm run dev:campaign   # Campaign Service (port 3003)
npm run dev:analytics  # Analytics Service (port 3004)
```

### Step 5: Verify Setup (2 minutes)

Test that everything is working:

```bash
# Check if services are running
curl http://localhost:3000/health

# Expected response:
# {"success": true, "status": "healthy", "services": {"voice": "up", "call": "up", ...}}
```

## 🎯 Your First AI Call in 5 Minutes

### 1. Create Your Organization (1 minute)

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "your_password",
    "name": "Admin User",
    "organization_name": "Your Company"
  }'
```

Save the JWT token from the response!

### 2. Create an AI Agent (1 minute)

```bash
curl -X POST http://localhost:3000/api/agents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Assistant",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "personality": "professional and friendly",
    "script": "Hi, this is Sarah from Your Company. I am calling to tell you about our amazing AI call center solution that can automate your sales calls. Are you interested in learning more?"
  }'
```

### 3. Make Your First Call (1 minute)

```bash
curl -X POST http://localhost:3000/api/calls \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "agent_id": "agent_id_from_step_2",
    "script": "Hi, this is a test call from Vocelio AI. This call is being made to test our AI call center platform. Thank you for your time!"
  }'
```

### 4. Monitor Your Call (2 minutes)

```bash
# Check call status
curl -X GET http://localhost:3000/api/calls/your_call_id \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# View real-time metrics
curl -X GET http://localhost:3000/api/analytics/realtime \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🎛️ Dashboard Access

If you want a visual interface:

1. **Start the Dashboard**
   ```bash
   npm run dev:dashboard
   ```

2. **Open in Browser**
   - Go to `http://localhost:3007`
   - Login with your credentials
   - Start managing campaigns visually!

## 🚀 Next Steps

Now that your basic setup is working, you can:

### Create Your First Campaign
```bash
curl -X POST http://localhost:3000/api/campaigns \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Demo Campaign",
    "campaign_type": "outbound_sales",
    "settings": {
      "max_calls_per_day": 100,
      "max_attempts_per_prospect": 3
    },
    "script": {
      "opening": "Hi, this is [AGENT_NAME] from [COMPANY]. I am calling to offer you a free demo of our AI solution.",
      "pitch": "Our platform can automate your sales calls and increase conversion rates by 300%.",
      "closing": "Would you be interested in a 15-minute demo this week?"
    }
  }'
```

### Upload Leads
```bash
# Create a CSV file with leads (leads.csv)
# Format: name,phone,email,company
# John Doe,+1234567890,john@example.com,Tech Corp

curl -X POST http://localhost:3000/api/campaigns/YOUR_CAMPAIGN_ID/leads \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@leads.csv"
```

### Start Campaign
```bash
curl -X PUT http://localhost:3000/api/campaigns/YOUR_CAMPAIGN_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

## 🔧 Common Issues & Solutions

### Issue: "Database connection failed"
**Solution:** Check your Supabase credentials in `.env` file

### Issue: "Twilio authentication failed"  
**Solution:** Verify your Twilio Account SID and Auth Token

### Issue: "Port already in use"
**Solution:** Change the port in `.env` file or kill the process using the port

### Issue: "OpenAI API error"
**Solution:** Check your OpenAI API key and ensure you have credits

### Issue: "Voice generation failed"
**Solution:** Verify ElevenLabs API key or use default voice provider

## 📞 Testing Your Setup

### Test Voice Generation
```bash
curl -X POST http://localhost:3001/api/voice/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the voice generation system.",
    "voice_id": "21m00Tcm4TlvDq8ikWAM"
  }'
```

### Test Call Analysis
```bash
curl -X POST http://localhost:3006/api/ai/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Customer: Hi. Agent: Hello, I am calling about our AI solution. Customer: That sounds interesting, tell me more.",
    "analysis_types": ["sentiment", "intent"]
  }'
```

## 🎯 Performance Tips

### For Development
- Use `npm run dev` to start all services with hot reload
- Enable debug logging: `export LOG_LEVEL=debug`
- Use local Redis for better performance: `npm install redis`

### For Production
- Use `npm run build` and `npm start`
- Set up monitoring: Install Sentry or similar
- Use a production database: PostgreSQL recommended
- Set up load balancing for high traffic

## 📚 What's Next?

1. **Read the Full Documentation**
   - [Complete Setup Guide](./SETUP_GUIDE.md)
   - [Service Guides](./services/)
   - [API Reference](./API_REFERENCE.md)

2. **Explore Advanced Features**
   - Voice cloning and marketplace
   - A/B testing campaigns
   - Real-time analytics dashboard
   - Compliance and DNC management

3. **Deploy to Production**
   - [Railway Deployment Guide](./deployment/railway/DEPLOYMENT_GUIDE.md)
   - Environment configuration for production
   - Monitoring and alerting setup

4. **Integrate with Your System**
   - Webhook configuration
   - CRM integration
   - Custom reporting setup

## 🆘 Need Help?

- **Documentation Issues**: Check our [troubleshooting guide](./TROUBLESHOOTING.md)
- **API Questions**: Review the [API reference](./API_REFERENCE.md)
- **Feature Requests**: Open an issue on GitHub
- **Enterprise Support**: Contact our team for dedicated support

---

**🎉 Congratulations! Your Vocelio AI Call Center is now running and ready to revolutionize your voice communications!**

**Next:** [Explore the full setup guide](./SETUP_GUIDE.md) or [check out the API reference](./API_REFERENCE.md)
