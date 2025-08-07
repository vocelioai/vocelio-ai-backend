# 🚀 Phase 1 Core Services Deployment Checklist

## Railway Dashboard URL: https://railway.app/dashboard

### 🎯 Service 1: API Gateway
**Status:** ⏳ Pending
**Directory:** `1-api-gateway/`
**Port:** 8001

#### Deployment Steps:
1. ✅ Click "New Service" in Railway Dashboard
2. ✅ Select "GitHub Repo" 
3. ✅ Choose `vocelioai/vocelio-ai-backend`
4. ✅ Configure Service:
   - **Name:** `api-gateway`
   - **Root Directory:** `1-api-gateway`
   - **Start Command:** `python main.py`
5. ✅ Set Environment Variables:
   ```
   PORT=8001
   PYTHONPATH=/app
   ENVIRONMENT=production
   ```
6. ✅ Deploy and copy the Railway URL
7. ✅ Test health endpoint: `{URL}/health`

**Railway URL:** `_________________` (fill in after deployment)

---

### 🤖 Service 2: Agents
**Status:** ⏳ Pending
**Directory:** `2-agents/`
**Port:** 8002

#### Deployment Steps:
1. ✅ Click "New Service" in Railway Dashboard
2. ✅ Select "GitHub Repo"
3. ✅ Choose `vocelioai/vocelio-ai-backend`
4. ✅ Configure Service:
   - **Name:** `agents`
   - **Root Directory:** `2-agents`
   - **Start Command:** `python main.py`
5. ✅ Set Environment Variables:
   ```
   PORT=8002
   PYTHONPATH=/app
   ENVIRONMENT=production
   ```
6. ✅ Deploy and copy the Railway URL
7. ✅ Test health endpoint: `{URL}/health`

**Railway URL:** `_________________` (fill in after deployment)

---

### 🧠 Service 3: AI Brain
**Status:** ⏳ Pending
**Directory:** `3-ai-brain/`
**Port:** 8003

#### Deployment Steps:
1. ✅ Click "New Service" in Railway Dashboard
2. ✅ Select "GitHub Repo"
3. ✅ Choose `vocelioai/vocelio-ai-backend`
4. ✅ Configure Service:
   - **Name:** `ai-brain`
   - **Root Directory:** `3-ai-brain`
   - **Start Command:** `python main.py`
5. ✅ Set Environment Variables:
   ```
   PORT=8003
   PYTHONPATH=/app
   ENVIRONMENT=production
   ```
6. ✅ Deploy and copy the Railway URL
7. ✅ Test health endpoint: `{URL}/health`

**Railway URL:** `_________________` (fill in after deployment)

---

### 📞 Service 4: Call Center
**Status:** ⏳ Pending
**Directory:** `4-call-center/`
**Port:** 8004

#### Deployment Steps:
1. ✅ Click "New Service" in Railway Dashboard
2. ✅ Select "GitHub Repo"
3. ✅ Choose `vocelioai/vocelio-ai-backend`
4. ✅ Configure Service:
   - **Name:** `call-center`
   - **Root Directory:** `4-call-center`
   - **Start Command:** `python main.py`
5. ✅ Set Environment Variables:
   ```
   PORT=8004
   PYTHONPATH=/app
   ENVIRONMENT=production
   ```
6. ✅ Deploy and copy the Railway URL
7. ✅ Test health endpoint: `{URL}/health`

**Railway URL:** `_________________` (fill in after deployment)

---

### 🔗 Service 5: Integrations
**Status:** ⏳ Pending
**Directory:** `5-integrations/`
**Port:** 8005

#### Deployment Steps:
1. ✅ Click "New Service" in Railway Dashboard
2. ✅ Select "GitHub Repo"
3. ✅ Choose `vocelioai/vocelio-ai-backend`
4. ✅ Configure Service:
   - **Name:** `integrations`
   - **Root Directory:** `5-integrations`
   - **Start Command:** `python main.py`
5. ✅ Set Environment Variables:
   ```
   PORT=5005
   PYTHONPATH=/app
   ENVIRONMENT=production
   ```
6. ✅ Deploy and copy the Railway URL
7. ✅ Test health endpoint: `{URL}/health`

**Railway URL:** `_________________` (fill in after deployment)

---

## 🔍 Phase 1 Verification Script

Once all 5 services are deployed, run this test:

```bash
# Test all Phase 1 services
curl -s "OVERVIEW_URL/health"
curl -s "API_GATEWAY_URL/health"
curl -s "AGENTS_URL/health"
curl -s "AI_BRAIN_URL/health"
curl -s "CALL_CENTER_URL/health"
curl -s "INTEGRATIONS_URL/health"
```

## 📊 Phase 1 Success Criteria
- ✅ All 6 services (Overview + 5 core) respond with 200 OK
- ✅ Health endpoints return valid JSON
- ✅ No deployment errors in Railway logs
- ✅ Services restart successfully

## 🎯 Expected URLs Format
```
Overview: https://vocelio-ai-backend-production.up.railway.app
API Gateway: https://api-gateway-production-XXXX.up.railway.app
Agents: https://agents-production-XXXX.up.railway.app
AI Brain: https://ai-brain-production-XXXX.up.railway.app
Call Center: https://call-center-production-XXXX.up.railway.app
Integrations: https://integrations-production-XXXX.up.railway.app
```

---

## 🚀 Next Steps After Phase 1
1. ✅ Update this checklist with actual URLs
2. ✅ Run health check tests
3. ✅ Proceed to Phase 2: Business Services (10 services)
4. ✅ Complete all 25 services deployment
5. ✅ Final system integration testing
