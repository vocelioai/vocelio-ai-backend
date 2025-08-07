# 🚂 Railway Deployment Guide

This guide walks you through deploying the Vocelio AI Call Center to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be pushed to GitHub (✅ Already done!)
3. **Railway CLI** (optional): Install with `npm install -g @railway/cli`

## Quick Deployment Steps

### 1. Connect GitHub Repository

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `vocelioai/vocelio-ai-backend`

### 2. Deploy Services (Recommended Order)

**Start with these core services:**

1. **API Gateway** (Port 8000) - Main entry point
2. **Agents** (Port 8001) - Agent management
3. **AI Brain** (Port 8002) - Core AI processing
4. **Call Center** (Port 8005) - Call management
5. **Integrations** (Port 8010) - Calendar & external APIs

**Then deploy supporting services:**

6. Analytics Pro (Port 8003)
7. Billing Pro (Port 8004)
8. Compliance (Port 8006)
9. Flow Builder (Port 8007)
10. Developer API (Port 8008)
11. Knowledge Base (Port 8009)
12. Lead Management (Port 8011)
13. Notifications (Port 8012)
14. Scheduling (Port 8013)
15. Phone Numbers (Port 8014)
16. Scripts (Port 8015)
17. Smart Campaigns (Port 8016)
18. Settings (Port 8017)
19. Team Hub (Port 8018)
20. Voice Lab (Port 8019)
21. Overview (Port 8020)
22. Voice Marketplace (Port 8021)
23. White Label (Port 8022)
24. Agent Store (Port 8023)
25. Webhooks (Port 8024)

### 3. Configure Environment Variables

For each service, add these environment variables in Railway:

```bash
# Essential for all services
PORT=8000  # (Railway sets this automatically)
DATABASE_URL=postgresql://...  # (Add your database)
REDIS_URL=redis://...          # (Add your Redis instance)

# Service-specific URLs (Railway auto-generates)
API_GATEWAY_URL=https://your-api-gateway.railway.app
AGENTS_SERVICE_URL=https://your-agents.railway.app
# ... etc for all services
```

### 4. Database Setup

Railway makes database setup easy:

1. In your Railway project, click "New Service"
2. Choose "PostgreSQL" from the database options
3. Railway will automatically create and configure the database
4. Copy the `DATABASE_URL` and add it to all your services

### 5. Domain Configuration

Railway automatically provides:
- **Individual service URLs**: `https://servicename-production.railway.app`
- **Custom domains**: Add your own domain in Railway settings

## Service Dependencies

**Inter-service communication:**
- Services communicate via HTTP using Railway-provided URLs
- Environment variables contain service endpoints
- Railway handles internal networking automatically

## Monitoring & Logs

Railway provides built-in:
- **Real-time logs** for each service
- **Metrics dashboard** with CPU, memory, network usage
- **Health checks** via `/health` endpoints
- **Deployment history** and rollback capabilities

## Cost Optimization

**Railway Pricing Tiers:**
- **Hobby**: $5/month + usage (perfect for development)
- **Pro**: $20/month + usage (recommended for production)
- **Team**: $20/user/month + usage (for teams)

**Tips to optimize costs:**
1. Start with core services only
2. Scale up based on actual usage
3. Use Railway's sleep feature for development
4. Monitor resource usage regularly

## Troubleshooting

**Common Issues:**

1. **Port Configuration**: Ensure each service uses `PORT` env var
2. **Service URLs**: Update inter-service communication URLs
3. **Database Connections**: Verify `DATABASE_URL` is set correctly
4. **Health Checks**: All services must respond to `/health`

**Useful Railway Commands:**
```bash
railway login              # Login to Railway
railway status             # Check deployment status
railway logs               # View logs
railway open               # Open in browser
railway env                # Manage environment variables
```

## Production Checklist

- [ ] All 25 services deployed successfully
- [ ] Database connected and migrated
- [ ] Environment variables configured
- [ ] Custom domain configured (optional)
- [ ] SSL certificates active (automatic)
- [ ] Monitoring alerts set up
- [ ] Backup strategy implemented

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Active community support
- **GitHub Issues**: Report issues in this repository

---

🎉 **Congratulations!** Your Vocelio AI Call Center is now live on Railway!
