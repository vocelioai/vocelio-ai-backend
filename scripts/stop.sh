#!/bin/bash

# Vocelio Backend Stop Script
echo "🛑 Stopping Vocelio Backend Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="pids/$service_name.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${BLUE}🔧 Stopping $service_name (PID: $pid)...${NC}"
            kill $pid
            
            # Wait for process to stop
            sleep 2
            
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  Force stopping $service_name...${NC}"
                kill -9 $pid
            fi
            
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name was not running${NC}"
        fi
        
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No PID file found for $service_name${NC}"
    fi
}

# Stop all services
echo -e "${BLUE}🛑 Stopping all services...${NC}"

# Stop services in reverse order
stop_service "Agents Service"
stop_service "API Gateway"

# Clean up any remaining Python processes on our ports
echo -e "${BLUE}🧹 Cleaning up any remaining processes...${NC}"

# Kill any processes using our ports
for port in 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010 8011 8012 8013 8014 8015 8016 8017 8018; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}🔧 Killing process on port $port...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
    fi
done

# Clean up directories
rm -rf pids logs

echo ""
echo -e "${GREEN}✅ All Vocelio Backend Services Stopped${NC}"
echo -e "${BLUE}💡 To start services again, run: ./scripts/start.sh${NC}"
