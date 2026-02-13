#!/bin/bash
# Restore Script for ChatBot System Backups
# Usage: ./restore.sh <backup_dir> <date>
# Example: ./restore.sh /opt/chatbot-backups 20260213-143022

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <backup_dir> [date]${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 /opt/chatbot-backups                    # Restore latest"
    echo "  $0 /opt/chatbot-backups 20260213-143022    # Restore specific date"
    exit 1
fi

BACKUP_DIR="$1"
DATE="${2:-latest}"
BACKUP_PREFIX="chatbot-backup"

if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}Error: Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}=== ChatBot System Restore ===${NC}"
echo "Backup directory: $BACKUP_DIR"
echo "Restore date: $DATE"
echo ""

# Warning
echo -e "${YELLOW}WARNING: This will overwrite current data!${NC}"
echo -e "${YELLOW}Make sure all services are stopped before proceeding.${NC}"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""

# Stop services
echo -e "${BLUE}1. Stopping services...${NC}"
docker compose down
echo -e "${GREEN}✓ Services stopped${NC}"

echo ""

# Function to restore a volume
restore_volume() {
    local volume_name=$1
    local backup_file="${BACKUP_DIR}/${BACKUP_PREFIX}-${volume_name}-${DATE}.tar.gz"
    
    echo -n "Restoring $volume_name... "
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${YELLOW}⚠ Backup file not found: $backup_file${NC}"
        return 1
    fi
    
    # Remove existing volume
    docker volume rm "$volume_name" 2>/dev/null || true
    
    # Create new volume
    docker volume create "$volume_name" > /dev/null
    
    # Restore data
    if docker run --rm \
        -v "${volume_name}:/data" \
        -v "${BACKUP_DIR}:/backup" \
        ubuntu \
        tar xzf "/backup/$(basename $backup_file)" -C /data 2>/dev/null; then
        
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Restore Qdrant
echo -e "${BLUE}2. Qdrant Vector Database${NC}"
restore_volume "qdrant_data"

# Restore Ollama
echo -e "${BLUE}3. Ollama Models${NC}"
restore_volume "ollama_data"

# Restore Node-RED
echo -e "${BLUE}4. Node-RED Flows${NC}"
restore_volume "nodered_data"

# Restore Open WebUI (if exists)
if [ -f "${BACKUP_DIR}/${BACKUP_PREFIX}-open_webui_data-${DATE}.tar.gz" ]; then
    echo -e "${BLUE}5. Open WebUI Data${NC}"
    restore_volume "open_webui_data"
fi

echo ""

# Restore configuration files
echo -e "${BLUE}6. Configuration Files${NC}"
CONFIG_BACKUP="${BACKUP_DIR}/${BACKUP_PREFIX}-config-${DATE}.tar.gz"

if [ -f "$CONFIG_BACKUP" ]; then
    echo -n "Restoring configuration... "
    
    # Backup current .env if exists
    if [ -f ".env" ]; then
        cp .env .env.backup-$(date +%Y%m%d-%H%M%S)
    fi
    
    tar xzf "$CONFIG_BACKUP"
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ Config backup not found${NC}"
fi

echo ""

# Start services
echo -e "${BLUE}7. Starting services...${NC}"
docker compose up -d
echo -e "${GREEN}✓ Services started${NC}"

echo ""

# Wait for services to be healthy
echo -e "${BLUE}8. Waiting for services to be healthy...${NC}"
sleep 10

# Check health
echo "Checking service health..."

check_health() {
    local name=$1
    local url=$2
    
    echo -n "  $name... "
    for i in {1..30}; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        fi
        sleep 2
    done
    echo -e "${RED}✗ TIMEOUT${NC}"
    return 1
}

check_health "Qdrant  " "http://localhost:6333/health"
check_health "Ollama  " "http://localhost:11434/api/tags"
check_health "Node-RED" "http://localhost:1880/"
check_health "Agent1  " "http://localhost:8001/health"

echo ""
echo -e "${GREEN}=== Restore Completed ===${NC}"
echo ""
echo "Verification steps:"
echo "  1. Check service status: ./deploy.sh status"
echo "  2. Check logs: ./deploy.sh logs"
echo "  3. Run health check: ./health-check.sh"
echo "  4. Test query: make test-query"
