#!/bin/bash
# Railway Deployment Script for Vocelio AI Call Center

echo "🚀 Deploying Vocelio AI Call Center to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    curl -fsSL https://railway.app/install.sh | sh
    export PATH=$PATH:~/.railway/bin
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway auth:login

# Create new project if it doesn't exist
echo "📁 Setting up Railway project..."
railway project:new vocelio-ai-backend

# Link to the project
railway link

# Add required addons
echo "🗄️ Setting up database addons..."
railway add postgresql
railway add redis

# Set environment variables
echo "⚙️ Setting environment variables..."
railway env:set PYTHON_VERSION=3.11
railway env:set PORT=8000
railway env:set ENVIRONMENT=production
railway env:set DEBUG=false

# Deploy the application
echo "🚀 Deploying application..."
railway up

# Deploy specific services
echo "🔧 Deploying microservices..."
railway service:create api-gateway
railway service:create overview
railway service:create agents
railway service:create smart-campaigns
railway service:create call-center

echo "✅ Deployment initiated! Check Railway dashboard for status."
echo "🌐 Your API will be available at: https://vocelio-ai-backend.railway.app"

# Display next steps
echo ""
echo "📋 Next Steps:"
echo "1. Set your environment variables in Railway dashboard"
echo "2. Configure custom domain if needed"
echo "3. Set up monitoring and alerts"
echo "4. Deploy your React dashboard separately"
echo ""
echo "🔗 Railway Dashboard: https://railway.app/dashboard"
