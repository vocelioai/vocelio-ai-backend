# Railway Deployment Guide for Vocelio AI Call Center

## 🚀 Railway Deployment Steps

### 1. **Prepare Environment Variables**
Create these variables in Railway dashboard:

#### Database Configuration
```bash
# Supabase Configuration
DATABASE_URL="postgresql://[username]:[password]@[host]:[port]/[database]"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Redis Configuration (for caching and sessions)
REDIS_URL="redis://default:[password]@[host]:[port]"

# JWT Configuration
JWT_SECRET="your-super-secure-jwt-secret-key"
JWT_EXPIRES_IN="7d"

# Twilio Configuration (for voice calls)
TWILIO_ACCOUNT_SID="your-twilio-account-sid"
TWILIO_AUTH_TOKEN="your-twilio-auth-token"
TWILIO_PHONE_NUMBER="your-twilio-phone-number"

# OpenAI Configuration (for AI features)
OPENAI_API_KEY="your-openai-api-key"

# Webhook Configuration
WEBHOOK_SECRET="your-webhook-secret"

# Email Configuration (for notifications)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"

# File Storage (Supabase Storage or AWS S3)
STORAGE_BUCKET="vocelio-uploads"
STORAGE_URL="https://your-project.supabase.co/storage/v1"

# Monitoring & Analytics
SENTRY_DSN="your-sentry-dsn" # Optional
ANALYTICS_API_KEY="your-analytics-key" # Optional
```

### 2. **Deploy Services in Order**

#### Step 1: Deploy Database Schema
1. In your Supabase dashboard, run `SUPABASE_COMPLETE_SCHEMA.sql`
2. Then run `SUPABASE_LOGIC_FUNCTIONS.sql`

#### Step 2: Deploy Backend Services
```bash
# Connect Railway to your GitHub repository
railway login
railway link [your-project-id]

# Deploy each service
railway up --service api-gateway
railway up --service voice-service
railway up --service campaign-service
railway up --service analytics-service
railway up --service call-service
```

#### Step 3: Deploy Frontend Dashboard
```bash
railway up --service dashboard
```

### 3. **Post-Deployment Configuration**

#### Enable Supabase Extensions
Run in Supabase SQL editor:
```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Enable real-time for critical tables
ALTER PUBLICATION supabase_realtime ADD TABLE calls;
ALTER PUBLICATION supabase_realtime ADD TABLE campaigns;
ALTER PUBLICATION supabase_realtime ADD TABLE agents;
```

#### Configure Domain & SSL
1. Add custom domain in Railway dashboard
2. Configure SSL certificates (automatic with Railway)
3. Update CORS settings in API Gateway

### 4. **Health Checks & Monitoring**

Each service includes health check endpoints:
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed service status
- `GET /metrics` - Prometheus metrics

### 5. **Database Migrations**

For future updates, use the migration system:
```bash
# Generate new migration
npm run migration:generate

# Run migrations
npm run migration:run

# Rollback if needed
npm run migration:rollback
```

### 6. **Scaling Configuration**

Railway auto-scaling settings:
- **API Gateway**: 2-10 instances (high traffic)
- **Voice Service**: 1-5 instances (real-time calls)
- **Campaign Service**: 1-3 instances (background tasks)
- **Analytics Service**: 1-2 instances (data processing)
- **Call Service**: 2-8 instances (core functionality)

### 7. **Monitoring Dashboards**

Access monitoring at:
- Railway Dashboard: Service metrics & logs
- Supabase Dashboard: Database performance
- Custom Analytics: `/analytics/dashboard`

### 🔒 **Security Checklist**

- [ ] All environment variables configured
- [ ] JWT secrets are secure and unique
- [ ] Database RLS policies enabled
- [ ] API rate limiting configured
- [ ] CORS properly configured
- [ ] Webhook signatures verified
- [ ] File upload restrictions in place

### 🚨 **Troubleshooting**

#### Common Issues:
1. **Database Connection**: Check DATABASE_URL format
2. **Missing Tables**: Ensure schema scripts ran successfully
3. **CORS Errors**: Update allowed origins in API Gateway
4. **Real-time Issues**: Verify Supabase real-time configuration

#### Useful Commands:
```bash
# View logs
railway logs --service [service-name]

# Check service status
railway status

# Restart service
railway redeploy --service [service-name]
```

### 📈 **Performance Optimization**

1. **Database Optimization**:
   - Indexes are pre-configured
   - Connection pooling enabled
   - Query optimization in place

2. **API Optimization**:
   - Response caching implemented
   - Request/response compression
   - Database query optimization

3. **Real-time Features**:
   - WebSocket connection management
   - Event-driven architecture
   - Efficient pub/sub patterns

---

## 🎯 **Quick Start Commands**

```bash
# 1. Push to GitHub
git add .
git commit -m "feat: complete Vocelio AI Call Center implementation"
git push origin main

# 2. Deploy to Railway
railway login
railway link
railway up

# 3. Configure environment variables in Railway dashboard

# 4. Run database migrations in Supabase

# 5. Test deployment
curl https://your-app.railway.app/health
```

Your Vocelio AI Call Center is now production-ready! 🚀
