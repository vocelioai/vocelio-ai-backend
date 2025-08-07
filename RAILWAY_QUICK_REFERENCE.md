# 🎯 Railway Dashboard Quick Reference

## 🚀 Phase 1: Core Services (Deploy These First)

| Service | Port | Directory | Key Environment Variables |
|---------|------|-----------|---------------------------|
| **API Gateway** ⭐ | 8000 | `apps/api-gateway` | `PORT=8000, SERVICE_NAME=api-gateway` |
| **Agents** ⭐ | 8001 | `apps/agents` | `PORT=8001, SERVICE_NAME=agents, MAX_AGENTS=100` |
| **AI Brain** ⭐ | 8002 | `apps/ai-brain` | `PORT=8002, SERVICE_NAME=ai-brain, OPENAI_API_KEY=your-key` |
| **Call Center** ⭐ | 8005 | `apps/call-center` | `PORT=8005, SERVICE_NAME=call-center, TWILIO_ACCOUNT_SID=your-sid` |
| **Integrations** ⭐ | 8010 | `apps/integrations` | `PORT=8010, SERVICE_NAME=integrations` |

## 📋 Railway Dashboard Workflow

### For Each Service:
1. **New Service** → **GitHub Repo**
2. **Repository**: `vocelioai/vocelio-ai-backend`
3. **Root Directory**: `apps/[service-name]`
4. **Environment Variables**: Set PORT + service-specific vars
5. **Deploy** → **Monitor Logs** → **Test Health Endpoint**

## 🔗 Expected URLs After Deployment

```
✅ Overview:     https://vocelio-ai-backend-production.up.railway.app/
🎯 API Gateway:  https://api-gateway-production.railway.app/
🎯 Agents:       https://agents-production.railway.app/
🎯 AI Brain:     https://ai-brain-production.railway.app/
🎯 Call Center:  https://call-center-production.railway.app/
🎯 Integrations: https://integrations-production.railway.app/
```

## ✅ Health Check Commands

```bash
# Test all Phase 1 services
curl https://api-gateway-production.railway.app/health
curl https://agents-production.railway.app/health
curl https://ai-brain-production.railway.app/health
curl https://call-center-production.railway.app/health
curl https://integrations-production.railway.app/health
```

## 🚨 Common Railway Dashboard Issues

| Issue | Solution |
|-------|----------|
| **Build Fails** | Check `apps/[service]/Dockerfile` exists |
| **Port Error** | Verify `PORT` environment variable is set |
| **Health Check Fails** | Ensure `/health` endpoint responds |
| **Out of Memory** | Upgrade Railway plan or optimize service |

## 💡 Railway Dashboard Tips

- **Logs Tab**: Real-time debugging and error tracking
- **Metrics Tab**: Monitor resource usage (CPU, memory, network)
- **Settings Tab**: Configure custom domains and environment variables
- **Deployments Tab**: View deployment history and rollback if needed

---

🎯 **Start Phase 1**: Deploy these 5 core services, then we'll move to Phase 2!
