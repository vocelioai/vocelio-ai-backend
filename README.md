# 🎯 Vocelio AI Call Center - Complete Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.1+-blue.svg)](https://reactjs.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Powered-green.svg)](https://supabase.com/)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Enterprise-grade AI-powered call center platform with advanced voice generation, campaign management, and real-time analytics.**

## 🚀 **Quick Start (15 Minutes)**

```bash
# 1. Clone the repository
git clone https://github.com/your-username/vocelio-backend.git
cd vocelio-backend

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Deploy to Railway (Recommended)
cd scripts
./deploy-railway.ps1

# 4. Set up database
# Run SUPABASE_COMPLETE_SCHEMA.sql in your Supabase dashboard
# Run SUPABASE_LOGIC_FUNCTIONS.sql for advanced features

# 5. Start local development (optional)
docker-compose up --build
```

**🌐 Your API will be live at: `https://your-project.railway.app`**

## 📋 **Complete Documentation**

| 📚 Topic | 📖 Guide | 🎯 Use Case |
|----------|----------|-------------|
| **🚀 Quick Setup** | [15-Minute Guide](./docs/QUICK_START.md) | Get running immediately |
| **🏗️ Full Setup** | [Complete Guide](./docs/SETUP_GUIDE.md) | Production deployment |
| **🔌 API Reference** | [API Docs](./docs/API_REFERENCE.md) | Developer integration |
| **🤖 AI Assistant** | [AI Reference](./docs/AI_ASSISTANT_REFERENCE.md) | GPT/Claude guidance |

### 🎯 **Service-Specific Documentation**
- 🎤 [Voice Service](./docs/services/VOICE_SERVICE.md) - TTS, voice cloning, speech synthesis
- ☎️ [Call Service](./docs/services/CALL_SERVICE.md) - Call management and Twilio integration  
- 📊 [Campaign Service](./docs/services/CAMPAIGN_SERVICE.md) - Campaign management and optimization
- 📈 [Analytics Service](./docs/services/ANALYTICS_SERVICE.md) - Real-time analytics and reporting

## ✨ **Key Features**

### 🎯 **AI-Powered Voice Generation**
- **Advanced TTS**: OpenAI, ElevenLabs, Piper TTS integration
- **Voice Cloning**: Custom voice generation from samples
- **Voice Marketplace**: Pre-built professional voices
- **Real-time Processing**: Low-latency voice generation

### ☎️ **Enterprise Call Management**
- **Twilio Integration**: Professional telephony infrastructure
- **Real-time Monitoring**: Live call tracking and analytics
- **Call Recording**: Automatic conversation storage
- **Smart Routing**: Intelligent call distribution

### 📊 **Advanced Campaign Management**
- **AI Optimization**: Machine learning-powered campaigns
- **A/B Testing**: Multi-variant campaign testing
- **Lead Management**: CRM integration and tracking
- **Compliance**: GDPR, HIPAA, TCPA, DNC checking

### 📈 **Real-time Analytics**
- **Live Dashboards**: Real-time performance metrics
- **Conversion Tracking**: Advanced ROI analytics
- **Agent Performance**: Individual and team insights
- **Custom Reports**: Flexible reporting engine

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Dashboard│    │   API Gateway    │    │   Microservices │
│   (Port 3000)   │◄──►│   (Port 8000)    │◄──►│   (8001-8021)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Supabase DB   │    │   Redis Cache    │    │   External APIs │
│   (PostgreSQL)  │    │   (Sessions)     │    │ Twilio/OpenAI/etc│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🔧 **25 Microservices**
| Service | Port | Purpose |
|---------|------|---------|
| API Gateway | 8000 | Main entry point and routing |
| Overview | 8001 | Dashboard and metrics |
| Agents | 8002 | AI agent management |
| Smart Campaigns | 8003 | Campaign automation |
| Call Center | 8004 | Call management |
| Phone Numbers | 8005 | Number provisioning |
| Voice Marketplace | 8006 | Voice library |
| Voice Lab | 8007 | Voice generation |
| Flow Builder | 8008 | Conversation flows |
| Analytics Pro | 8009 | Advanced analytics |
| AI Brain | 8010 | Core AI processing |
| Integrations | 8011 | Third-party connections |
| Agent Store | 8012 | Agent marketplace |
| Billing Pro | 8013 | Payment processing |
| Team Hub | 8014 | Team management |
| Compliance | 8015 | Regulatory compliance |
| White Label | 8016 | Custom branding |
| Developer API | 8017 | Public API |
| Settings | 8018 | Configuration |
| Scripts | 8019 | Automation scripts |
| Notifications | 8020 | Alert system |
| Webhooks | 8021 | Event processing |

## 🛠️ **Technology Stack**

### **Backend**
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Advanced relational database with Supabase
- **Redis** - High-speed caching and session management
- **Pydantic** - Data validation and serialization

### **Frontend**
- **React 19** - Modern UI framework
- **Tailwind CSS** - Utility-first styling
- **Lucide Icons** - Beautiful icon library
- **ReactFlow** - Interactive flow diagrams

### **Infrastructure**
- **Railway** - Cloud deployment platform
- **Docker** - Containerization
- **Supabase** - Database and authentication
- **Twilio** - Voice communications

### **AI & Voice**
- **OpenAI** - GPT models and TTS
- **ElevenLabs** - Premium voice generation
- **Piper TTS** - Local voice synthesis
- **Custom AI Models** - Conversation optimization

## 🚀 **Deployment Options**

### **🌟 Railway (Recommended)**
One-click deployment with automatic scaling:
```bash
cd scripts
./deploy-railway.ps1
```

### **🐳 Docker**
Local development and self-hosting:
```bash
docker-compose up --build
```

### **☁️ AWS/GCP**
Enterprise deployment with full control:
- See [AWS Deployment Guide](./docs/deployment/aws/AWS_GUIDE.md)
- See [GCP Deployment Guide](./docs/deployment/gcp/GCP_GUIDE.md)

## 📊 **Database Schema**

### **Advanced PostgreSQL Features**
- **25+ Tables** - Complete business logic coverage
- **Advanced Functions** - 1160+ lines of business logic
- **Real-time Subscriptions** - Live data updates
- **Row Level Security** - Multi-tenant data isolation
- **Advanced Analytics** - Built-in reporting functions

### **Key Tables**
```sql
organizations         -- Multi-tenant organization management
users                -- User accounts and permissions  
agents               -- AI agent configurations
campaigns            -- Campaign management
calls                -- Call tracking and analytics
prospects            -- Lead management
voice_clones         -- Custom voice storage
analytics_events     -- Real-time event tracking
```

## 🔐 **Security & Compliance**

### **Enterprise Security**
- **JWT Authentication** - Secure token-based auth
- **Row Level Security** - Database-level permissions
- **API Rate Limiting** - DDoS protection
- **CORS Configuration** - Cross-origin security

### **Regulatory Compliance**
- **GDPR** - European data protection
- **HIPAA** - Healthcare data security
- **TCPA** - Telecom compliance
- **DNC Registry** - Do Not Call checking

## 📈 **Performance & Monitoring**

### **Built-in Monitoring**
- **Prometheus Metrics** - Performance monitoring
- **Health Checks** - Service availability
- **Error Tracking** - Sentry integration
- **Real-time Alerts** - Proactive monitoring

### **Performance Features**
- **Connection Pooling** - Database optimization
- **Redis Caching** - Sub-millisecond response times
- **Load Balancing** - Horizontal scaling
- **Circuit Breakers** - Fault tolerance

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# 1. Fork and clone
git clone https://github.com/your-username/vocelio-backend.git

# 2. Set up environment
cp .env.example .env

# 3. Start development
docker-compose up --build

# 4. Run tests
pytest tests/
```

## 📞 **Support**

### **Community Support**
- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Community Q&A
- **Discord** - Real-time community chat

### **Enterprise Support**
- **Email** - support@vocelio.ai
- **Implementation Services** - Custom setup assistance
- **Training** - Team onboarding programs

## 📜 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **OpenAI** - Advanced AI capabilities
- **Supabase** - Backend infrastructure
- **Railway** - Deployment platform
- **Twilio** - Voice communications
- **FastAPI** - Python web framework

---

**🚀 Built with ❤️ for the future of AI-powered communications**

**Ready to deploy? Start with our [15-Minute Quick Start Guide](./docs/QUICK_START.md)**
