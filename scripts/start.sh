#!/bin/bash

# Vocelio Backend Startup Script
echo "🚀 Starting Vocelio Backend Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo -e "${RED}❌ Port $port is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
        return 0
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local app_path=$3
    
    echo -e "${BLUE}🔧 Starting $service_name on port $port...${NC}"
    
    if check_port $port; then
        cd "$app_path" || exit 1
        
        # Install dependencies if requirements.txt exists
        if [ -f "requirements.txt" ]; then
            echo -e "${YELLOW}📦 Installing dependencies for $service_name...${NC}"
            pip install -r requirements.txt > /dev/null 2>&1
        fi
        
        # Start the service in the background
        uvicorn src.main:app --host 0.0.0.0 --port $port --reload > logs/$service_name.log 2>&1 &
        local pid=$!
        echo $pid > "pids/$service_name.pid"
        
        echo -e "${GREEN}✅ $service_name started (PID: $pid)${NC}"
        cd - > /dev/null
    else
        echo -e "${RED}❌ Cannot start $service_name - port $port is busy${NC}"
        exit 1
    fi
}

# Create directories for logs and PIDs
mkdir -p logs pids

# Check if Python and required packages are available
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip is not installed${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env file with your configuration${NC}"
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"

# Start API Gateway first
start_service "API Gateway" 8000 "apps/api-gateway"

# Wait a moment for gateway to start
sleep 2

# Start core services
start_service "Agents Service" 8002 "apps/agents"

# You can add more services here as they are implemented
# start_service "Overview Service" 8001 "apps/overview"
# start_service "Smart Campaigns" 8003 "apps/smart-campaigns"
# start_service "Call Center" 8004 "apps/call-center"

echo ""
echo -e "${GREEN}🎉 Vocelio Backend Services Started Successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "  • API Gateway:     ${GREEN}http://localhost:8000${NC}"
echo -e "  • API Docs:        ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  • Agents Service:  ${GREEN}http://localhost:8002${NC}"
echo ""
echo -e "${BLUE}🔍 Health Checks:${NC}"
echo -e "  • Gateway Health:  ${GREEN}http://localhost:8000/health${NC}"
echo -e "  • All Services:    ${GREEN}http://localhost:8000/services${NC}"
echo ""
echo -e "${YELLOW}📝 Logs are available in the 'logs/' directory${NC}"
echo -e "${YELLOW}🛑 To stop services, run: ./scripts/stop.sh${NC}"
echo ""
echo -e "${GREEN}✨ Happy coding with Vocelio! ✨${NC}"
