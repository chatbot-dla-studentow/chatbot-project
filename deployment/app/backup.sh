#!/bin/bash
# Automatic Backup Script for ChatBot System
# Usage: ./backup.sh [destination_dir]
# Cron example: 0 2 * * * /opt/chatbot-project/backup.sh /opt/chatbot-backups

set -e

# Configuration
BACKUP_DIR="${1:-/opt/chatbot-backups}"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_PREFIX="chatbot-backup"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== ChatBot System Backup ===${NC}"
echo "Timestamp: $(date)"
echo "Destination: $BACKUP_DIR"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup a volume
backup_volume() {
    local volume_name=$1
    local backup_name="${BACKUP_PREFIX}-${volume_name}-${DATE}.tar.gz"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    echo -n "Backing up $volume_name... "
    
    if docker run --rm \
        -v "${volume_name}:/data" \
        -v "${BACKUP_DIR}:/backup" \
        ubuntu \
        tar czf "/backup/${backup_name}" -C /data . 2>/dev/null; then
        
        local size=$(du -h "$backup_path" | cut -f1)
        echo -e "${GREEN}✓ OK${NC} (${size})"
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Backup Qdrant (vector database)
echo -e "${BLUE}1. Qdrant Vector Database${NC}"
backup_volume "qdrant_data"

# Backup Ollama (models)
echo -e "${BLUE}2. Ollama Models${NC}"
backup_volume "ollama_data"

# Backup Node-RED (flows and configuration)
echo -e "${BLUE}3. Node-RED Flows${NC}"
backup_volume "nodered_data"

# Backup Open WebUI (optional)
if docker volume ls | grep -q "open_webui_data"; then
    echo -e "${BLUE}4. Open WebUI Data${NC}"
    backup_volume "open_webui_data"
fi

echo ""

# Backup configuration files
echo -e "${BLUE}5. Configuration Files${NC}"
CONFIG_BACKUP="${BACKUP_DIR}/${BACKUP_PREFIX}-config-${DATE}.tar.gz"
echo -n "Backing up configuration... "

tar czf "$CONFIG_BACKUP" \
    --exclude='**/venv' \
    --exclude='**/__pycache__' \
    --exclude='**/.git' \
    --exclude='**/node_modules' \
    .env \
    docker-compose.yml \
    agents/agent1_student/agent1_flow.json \
    agents/agent1_student/knowledge/ \
    2>/dev/null || true

if [ -f "$CONFIG_BACKUP" ]; then
    size=$(du -h "$CONFIG_BACKUP" | cut -f1)
    echo -e "${GREEN}✓ OK${NC} (${size})"
else
    echo -e "${YELLOW}⚠ Partial backup${NC}"
fi

echo ""

# Export Qdrant collections metadata
echo -e "${BLUE}6. Qdrant Metadata${NC}"
echo -n "Exporting collection info... "
COLLECTIONS_FILE="${BACKUP_DIR}/${BACKUP_PREFIX}-qdrant-collections-${DATE}.json"

if curl -sf http://localhost:6333/collections > "$COLLECTIONS_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ Qdrant not accessible${NC}"
fi

echo ""

# Clean old backups
echo -e "${BLUE}7. Cleanup Old Backups${NC}"
echo -n "Removing backups older than ${RETENTION_DAYS} days... "

DELETED=$(find "$BACKUP_DIR" -name "${BACKUP_PREFIX}-*.tar.gz" -mtime +${RETENTION_DAYS} -delete -print | wc -l)
echo -e "${GREEN}✓ Removed $DELETED old backups${NC}"

echo ""

# Summary
echo -e "${BLUE}Backup Summary:${NC}"
echo "Location: $BACKUP_DIR"
echo "Date: $DATE"
echo ""

# List created backups
echo "Created backups:"
ls -lh "$BACKUP_DIR" | grep "$DATE" | awk '{print "  " $9 " (" $5 ")"}'

echo ""

# Total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "Total backup directory size: $TOTAL_SIZE"

# Disk space
echo ""
echo "Available disk space:"
df -h "$BACKUP_DIR" | tail -n 1 | awk '{print "  " $4 " free of " $2 " (" $5 " used)"}'

echo ""
echo -e "${GREEN}=== Backup Completed Successfully ===${NC}"

# Create a latest symlink
ln -sf "${BACKUP_PREFIX}-qdrant_data-${DATE}.tar.gz" "${BACKUP_DIR}/${BACKUP_PREFIX}-qdrant_data-latest.tar.gz"
ln -sf "${BACKUP_PREFIX}-ollama_data-${DATE}.tar.gz" "${BACKUP_DIR}/${BACKUP_PREFIX}-ollama_data-latest.tar.gz"
ln -sf "${BACKUP_PREFIX}-nodered_data-${DATE}.tar.gz" "${BACKUP_DIR}/${BACKUP_PREFIX}-nodered_data-latest.tar.gz"

echo "Latest backup links created (for easy restore)"
