# 🖱️ Railway Dashboard Deployment Checklist

## 📋 Phase 1: Core Services (Deploy First)

### 1. API Gateway (Port 8000) - Main Entry Point ⭐
**Railway Dashboard Steps:**
1. Go to https://railway.app/dashboard
2. Click "New Service" → "GitHub Repo"
3. Select `vocelioai/vocelio-ai-backend`
4. **Service Name**: `api-gateway`
5. **Root Directory**: `apps/api-gateway`
6. **Environment Variables**:
   ```
   PORT=8000
   SERVICE_NAME=api-gateway
   ENVIRONMENT=production
   ```
7. Click "Deploy"
8. **Expected URL**: `https://api-gateway-production.railway.app`
9. **Health Check**: `/health` endpoint

---

### 2. Agents (Port 8001) - Agent Management ⭐
**Railway Dashboard Steps:**
1. Click "New Service" → "GitHub Repo"
2. Select `vocelioai/vocelio-ai-backend`
3. **Service Name**: `agents`
4. **Root Directory**: `apps/agents`
5. **Environment Variables**:
   ```
   PORT=8001
   SERVICE_NAME=agents
   ENVIRONMENT=production
   MAX_AGENTS=100
   ```
6. Click "Deploy"
7. **Expected URL**: `https://agents-production.railway.app`
8. **Health Check**: `/health` endpoint

---

### 3. AI Brain (Port 8002) - Core AI Processing ⭐
**Railway Dashboard Steps:**
1. Click "New Service" → "GitHub Repo"
2. Select `vocelioai/vocelio-ai-backend`
3. **Service Name**: `ai-brain`
4. **Root Directory**: `apps/ai-brain`
5. **Environment Variables**:
   ```
   PORT=8002
   SERVICE_NAME=ai-brain
   ENVIRONMENT=production
   OPENAI_API_KEY=your-openai-key
   MODEL_NAME=gpt-4
   ```
6. Click "Deploy"
7. **Expected URL**: `https://ai-brain-production.railway.app`
8. **Health Check**: `/health` endpoint

---

### 4. Call Center (Port 8005) - Call Operations ⭐
**Railway Dashboard Steps:**
1. Click "New Service" → "GitHub Repo"
2. Select `vocelioai/vocelio-ai-backend`
3. **Service Name**: `call-center`
4. **Root Directory**: `apps/call-center`
5. **Environment Variables**:
   ```
   PORT=8005
   SERVICE_NAME=call-center
   ENVIRONMENT=production
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   ```
6. Click "Deploy"
7. **Expected URL**: `https://call-center-production.railway.app`
8. **Health Check**: `/health` endpoint

---

### 5. Integrations (Port 8010) - Calendar & External APIs ⭐
**Railway Dashboard Steps:**
1. Click "New Service" → "GitHub Repo"
2. Select `vocelioai/vocelio-ai-backend`
3. **Service Name**: `integrations`
4. **Root Directory**: `apps/integrations`
5. **Environment Variables**:
   ```
   PORT=8010
   SERVICE_NAME=integrations
   ENVIRONMENT=production
   GOOGLE_CALENDAR_ENABLED=true
   OUTLOOK_CALENDAR_ENABLED=true
   ```
6. Click "Deploy"
7. **Expected URL**: `https://integrations-production.railway.app`
8. **Health Check**: `/health` endpoint

---

## ✅ Phase 1 Verification

After deploying these 5 core services, test them:

```bash
# Test Core Services
curl https://api-gateway-production.railway.app/health
curl https://agents-production.railway.app/health
curl https://ai-brain-production.railway.app/health
curl https://call-center-production.railway.app/health
curl https://integrations-production.railway.app/health
```

**Expected Response for each**:
```json
{
  "status": "healthy",
  "service": "service-name",
  "timestamp": "2025-08-07T...",
  "version": "1.0.0"
}
```

---

## 📊 Progress Tracker

- [ ] **Overview** ✅ LIVE (already deployed)
- [ ] **API Gateway** (Port 8000)
- [ ] **Agents** (Port 8001)  
- [ ] **AI Brain** (Port 8002)
- [ ] **Call Center** (Port 8005)
- [ ] **Integrations** (Port 8010)

**Phase 1 Complete**: 6/25 services live

---

## 🔄 After Phase 1 Success

Once Phase 1 is working, proceed to Phase 2 with:
- Analytics Pro (8003)
- Billing Pro (8004)
- Compliance (8006)
- Flow Builder (8007)
- Developer API (8008)
- Knowledge Base (8009)
- Lead Management (8011)
- Notifications (8012)
- Scheduling (8013)
- Phone Numbers (8014)

## 🚨 Troubleshooting Tips

1. **Build Failures**: Check Dockerfile exists in service directory
2. **Port Issues**: Ensure PORT environment variable is set correctly
3. **Health Check Fails**: Verify `/health` endpoint responds
4. **Memory Issues**: Railway provides 512MB by default (upgrade if needed)

## 💡 Railway Dashboard Pro Tips

- **Logs**: Click service → "Logs" tab for real-time debugging
- **Metrics**: Monitor CPU, memory, and network usage
- **Environments**: Use different environments for staging/production
- **Custom Domains**: Add your own domain after deployment
- **Auto-deploy**: Railway automatically redeploys on GitHub commits

---

🎯 **Ready to start with Phase 1?** Go to Railway Dashboard and deploy the 5 core services!
