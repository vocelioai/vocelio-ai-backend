#!/bin/bash
# Railway Services Health Check Script
# Test all deployed services systematically

echo "🚂 Railway Services Health Check"
echo "================================"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service URLs (update these as you deploy)
declare -A SERVICES=(
    ["overview"]="https://vocelio-ai-backend-production.up.railway.app"
    ["api-gateway"]="https://api-gateway-production.railway.app"
    ["agents"]="https://agents-production.railway.app"
    ["ai-brain"]="https://ai-brain-production.railway.app"
    ["call-center"]="https://call-center-production.railway.app"
    ["integrations"]="https://integrations-production.railway.app"
    ["analytics-pro"]="https://analytics-pro-production.railway.app"
    ["billing-pro"]="https://billing-pro-production.railway.app"
    ["compliance"]="https://compliance-production.railway.app"
    ["flow-builder"]="https://flow-builder-production.railway.app"
    ["developer-api"]="https://developer-api-production.railway.app"
    ["knowledge-base"]="https://knowledge-base-production.railway.app"
    ["lead-management"]="https://lead-management-production.railway.app"
    ["notifications"]="https://notifications-production.railway.app"
    ["scheduling"]="https://scheduling-production.railway.app"
    ["phone-numbers"]="https://phone-numbers-production.railway.app"
    ["scripts"]="https://scripts-production.railway.app"
    ["smart-campaigns"]="https://smart-campaigns-production.railway.app"
    ["settings"]="https://settings-production.railway.app"
    ["team-hub"]="https://team-hub-production.railway.app"
    ["voice-lab"]="https://voice-lab-production.railway.app"
    ["voice-marketplace"]="https://voice-marketplace-production.railway.app"
    ["white-label"]="https://white-label-production.railway.app"
    ["agent-store"]="https://agent-store-production.railway.app"
    ["webhooks"]="https://webhooks-production.railway.app"
)

# Function to test a service
test_service() {
    local name=$1
    local url=$2
    
    echo -n "Testing $name: "
    
    # Test health endpoint
    response=$(curl -s -w "%{http_code}" "$url/health" -o /tmp/response.json 2>/dev/null)
    http_code="${response: -3}"
    
    if [ "$http_code" == "200" ]; then
        service_name=$(cat /tmp/response.json 2>/dev/null | grep -o '"service":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✅ HEALTHY${NC} ($service_name)"
        return 0
    else
        echo -e "${RED}❌ DOWN${NC} (HTTP: $http_code)"
        return 1
    fi
}

# Phase 1 Services (Priority)
echo -e "\n${YELLOW}📋 Phase 1: Core Services${NC}"
echo "------------------------"

phase1_services=("overview" "api-gateway" "agents" "ai-brain" "call-center" "integrations")
phase1_healthy=0

for service in "${phase1_services[@]}"; do
    if [[ -v SERVICES[$service] ]]; then
        test_service "$service" "${SERVICES[$service]}"
        if [ $? -eq 0 ]; then
            ((phase1_healthy++))
        fi
    else
        echo "Testing $service: ${YELLOW}⏳ NOT DEPLOYED${NC}"
    fi
done

echo -e "\n${YELLOW}Phase 1 Status: $phase1_healthy/6 services healthy${NC}"

# Phase 2 Services (Business)
echo -e "\n${YELLOW}📋 Phase 2: Business Services${NC}"
echo "----------------------------"

phase2_services=("analytics-pro" "billing-pro" "compliance" "flow-builder" "developer-api" "knowledge-base" "lead-management" "notifications" "scheduling" "phone-numbers")
phase2_healthy=0

for service in "${phase2_services[@]}"; do
    if [[ -v SERVICES[$service] ]]; then
        test_service "$service" "${SERVICES[$service]}"
        if [ $? -eq 0 ]; then
            ((phase2_healthy++))
        fi
    else
        echo "Testing $service: ${YELLOW}⏳ NOT DEPLOYED${NC}"
    fi
done

echo -e "\n${YELLOW}Phase 2 Status: $phase2_healthy/10 services healthy${NC}"

# Phase 3 Services (Advanced)
echo -e "\n${YELLOW}📋 Phase 3: Advanced Services${NC}"
echo "----------------------------"

phase3_services=("scripts" "smart-campaigns" "settings" "team-hub" "voice-lab" "voice-marketplace" "white-label" "agent-store" "webhooks")
phase3_healthy=0

for service in "${phase3_services[@]}"; do
    if [[ -v SERVICES[$service] ]]; then
        test_service "$service" "${SERVICES[$service]}"
        if [ $? -eq 0 ]; then
            ((phase3_healthy++))
        fi
    else
        echo "Testing $service: ${YELLOW}⏳ NOT DEPLOYED${NC}"
    fi
done

echo -e "\n${YELLOW}Phase 3 Status: $phase3_healthy/9 services healthy${NC}"

# Overall Summary
total_healthy=$((phase1_healthy + phase2_healthy + phase3_healthy))
echo -e "\n${YELLOW}🎯 OVERALL STATUS${NC}"
echo "================="
echo -e "Total Services: ${GREEN}$total_healthy/25 healthy${NC}"
echo -e "Phase 1 (Core): ${GREEN}$phase1_healthy/6${NC}"
echo -e "Phase 2 (Business): ${GREEN}$phase2_healthy/10${NC}"
echo -e "Phase 3 (Advanced): ${GREEN}$phase3_healthy/9${NC}"

if [ $total_healthy -eq 25 ]; then
    echo -e "\n🎉 ${GREEN}ALL SERVICES HEALTHY! DEPLOYMENT COMPLETE!${NC} 🎉"
elif [ $phase1_healthy -eq 6 ]; then
    echo -e "\n✅ ${GREEN}Phase 1 Complete!${NC} Ready for Phase 2 deployment."
elif [ $phase1_healthy -gt 0 ]; then
    echo -e "\n⚠️ ${YELLOW}Phase 1 in progress.${NC} Deploy remaining core services first."
else
    echo -e "\n🚀 ${YELLOW}Ready to start Phase 1 deployment!${NC}"
fi

# Clean up
rm -f /tmp/response.json

echo -e "\n🔗 Railway Dashboard: https://railway.app/dashboard"
echo "📖 Deployment Guide: See RAILWAY_DASHBOARD_GUIDE.md"
