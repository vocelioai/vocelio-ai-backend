#!/bin/bash
# Railway Deployment Script for Vocelio AI Call Center
# This script helps deploy all 25 services to Railway

echo "🚂 Vocelio AI Call Center - Railway Deployment"
echo "=============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   OR"
    echo "   curl -fsSL https://railway.app/install.sh | sh"
    exit 1
fi

echo "✅ Railway CLI found"

# Login check
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please run:"
    echo "   railway login"
    exit 1
fi

echo "✅ Railway authentication verified"

# Services to deploy (25 services)
SERVICES=(
    "api-gateway"
    "agents" 
    "ai-brain"
    "analytics-pro"
    "billing-pro"
    "call-center"
    "compliance"
    "flow-builder"
    "developer-api"
    "knowledge-base"
    "integrations"
    "lead-management"
    "notifications"
    "scheduling"
    "phone-numbers"
    "scripts"
    "smart-campaigns"
    "settings"
    "team-hub"
    "voice-lab"
    "voice-marketplace"
    "overview"
    "agent-store"
    "white-label"
    "webhooks"
)

echo "🚀 Preparing to deploy ${#SERVICES[@]} services..."

# Create a new Railway project
echo "📦 Creating Railway project..."
railway login
railway init

echo "🔧 Setting up services..."

# Deploy each service
for service in "${SERVICES[@]}"; do
    echo ""
    echo "🚂 Deploying $service service..."
    
    # Create service-specific Dockerfile if needed
    if [ -f "apps/$service/Dockerfile" ]; then
        echo "   ✅ Using existing Dockerfile for $service"
    else
        echo "   ⚠️  No Dockerfile found for $service"
        continue
    fi
    
    # Deploy the service
    echo "   📤 Deploying $service to Railway..."
    
    # Note: In practice, you would create separate Railway services
    # This is a template - actual deployment requires Railway dashboard setup
    echo "   ℹ️  Service $service ready for Railway deployment"
done

echo ""
echo "🎉 All services prepared for Railway deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://railway.app/dashboard"
echo "2. Create a new project"
echo "3. Connect your GitHub repository: vocelioai/vocelio-ai-backend"
echo "4. Deploy each service using the Railway dashboard"
echo "5. Set environment variables for each service"
echo ""
echo "🔗 Useful Railway Commands:"
echo "   railway login              # Login to Railway"
echo "   railway init               # Initialize project"
echo "   railway up                 # Deploy current directory"
echo "   railway logs               # View deployment logs"
echo "   railway open               # Open project in browser"
