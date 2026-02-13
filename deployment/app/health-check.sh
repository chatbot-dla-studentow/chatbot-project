#!/bin/bash
# Health Check Script for ChatBot System
# Usage: ./health-check.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}=== ChatBot System Health Check ===${NC}"
echo ""
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Track overall health
HEALTHY=true

# Function to check service
check_service() {
    local service_name=$1
    local url=$2
    local container=$3
    
    echo -n "Checking $service_name... "
    
    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "${RED}✗ Container not running${NC}"
        HEALTHY=false
        return 1
    fi
    
    # Check health endpoint
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        HEALTHY=false
        return 1
    fi
}

# Check Docker
echo -n "Checking Docker... "
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ Docker not running${NC}"
    HEALTHY=false
    exit 1
fi

# Check network
echo -n "Checking Docker network... "
if docker network inspect ai_network > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ Network 'ai_network' not found${NC}"
    HEALTHY=false
fi

echo ""

# Check core services
echo -e "${BLUE}Core Services:${NC}"
check_service "Qdrant       " "http://localhost:6333/health" "qdrant"
check_service "Ollama       " "http://localhost:11434/api/tags" "ollama"
check_service "Node-RED     " "http://localhost:1880/" "node-red"

echo ""

# Check agents
echo -e "${BLUE}Agent Services:${NC}"
check_service "Agent1       " "http://localhost:8001/health" "agent1_student"
check_service "Agent2       " "http://localhost:8002/health" "agent2_ticket" || true
check_service "Agent3       " "http://localhost:8003/health" "agent3_analytics" || true
check_service "Agent4       " "http://localhost:8004/health" "agent4_bos" || true
check_service "Agent5       " "http://localhost:8005/health" "agent5_security" || true

echo ""

# Check Qdrant collections
echo -e "${BLUE}Qdrant Collections:${NC}"
echo -n "Checking agent1_student collection... "
if curl -sf "http://localhost:6333/collections/agent1_student" > /dev/null 2>&1; then
    POINTS=$(curl -s "http://localhost:6333/collections/agent1_student" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['points_count'])" 2>/dev/null || echo "?")
    echo -e "${GREEN}✓ OK${NC} (${POINTS} points)"
else
    echo -e "${RED}✗ Collection not found${NC}"
    HEALTHY=false
fi

echo ""

# Check Ollama models
echo -e "${BLUE}Ollama Models:${NC}"
echo -n "Checking installed models... "
MODELS=$(docker exec ollama ollama list 2>/dev/null | tail -n +2 | wc -l)
if [ "$MODELS" -gt 0 ]; then
    echo -e "${GREEN}✓ OK${NC} (${MODELS} models)"
    docker exec ollama ollama list | tail -n +2 | while read line; do
        echo "  - $line"
    done
else
    echo -e "${YELLOW}⚠ No models installed${NC}"
fi

echo ""

# Check disk usage
echo -e "${BLUE}Disk Usage:${NC}"
df -h . | tail -n 1 | awk '{print "  Root partition: " $5 " used (" $3 "/" $2 ")"}'

# Check Docker volumes
echo ""
echo -e "${BLUE}Docker Volume Usage:${NC}"
docker system df -v | grep "VOLUME NAME" -A 20 | grep -E "(qdrant_data|ollama_data|nodered_data|open_webui_data)" | awk '{print "  " $1 ": " $3}'

echo ""

# Memory usage
echo -e "${BLUE}Memory Usage:${NC}"
free -h | awk 'NR==2{print "  RAM: " $3 "/" $2 " (" $3/$2*100 "%)"}'

echo ""

# CPU usage
echo -e "${BLUE}CPU Usage:${NC}"
top -bn1 | grep "Cpu(s)" | awk '{print "  CPU: " $2 " user, " $4 " system"}'

echo ""

# Container resource usage
echo -e "${BLUE}Container Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep -E "(NAME|agent|qdrant|ollama|node-red)" | head -n 10

echo ""

# Check logs for errors (last 100 lines)
echo -e "${BLUE}Recent Errors (last 100 log lines):${NC}"
ERROR_COUNT=$(docker compose logs --tail=100 2>&1 | grep -ci "error" || echo "0")
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $ERROR_COUNT error mentions in recent logs${NC}"
else
    echo -e "${GREEN}✓ No errors in recent logs${NC}"
fi

echo ""
echo "================================================"

# Final status
if [ "$HEALTHY" = true ]; then
    echo -e "${GREEN}Overall Status: HEALTHY ✓${NC}"
    exit 0
else
    echo -e "${RED}Overall Status: UNHEALTHY ✗${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check logs: ./deploy.sh logs"
    echo "  2. Restart services: ./deploy.sh restart"
    echo "  3. Check detailed logs: docker compose logs [service_name]"
    exit 1
fi
