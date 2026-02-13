#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Knowledge Base Initialization ===${NC}"
echo ""

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT1_DIR="$SCRIPT_DIR/agents/agent1_student"
VENV_DIR="$AGENT1_DIR/venv"

# Navigate to agent1 directory
cd "$AGENT1_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install -q --upgrade pip

# Install requirements
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt

# Check if Qdrant is accessible
echo -e "${BLUE}Checking Qdrant connection...${NC}"
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"

for i in {1..30}; do
    if curl -f "http://${QDRANT_HOST}:${QDRANT_PORT}/health" &> /dev/null; then
        echo -e "${GREEN}Qdrant is accessible${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}Warning: Qdrant is not accessible. Make sure it's running.${NC}"
        echo -e "${YELLOW}You can start it with: docker compose up -d qdrant${NC}"
        exit 1
    fi
    sleep 2
done

# Parse knowledge base
echo ""
echo -e "${BLUE}Step 1: Parsing knowledge base...${NC}"
if [ -f "helpers/parse_knowledge_base.py" ]; then
    python3 helpers/parse_knowledge_base.py
    echo -e "${GREEN}✓ Knowledge base parsed${NC}"
else
    echo -e "${YELLOW}Warning: parse_knowledge_base.py not found, skipping...${NC}"
fi

# Load knowledge base into Qdrant
echo ""
echo -e "${BLUE}Step 2: Loading knowledge base into Qdrant...${NC}"
if [ -f "helpers/load_knowledge_base.py" ]; then
    python3 helpers/load_knowledge_base.py
    echo -e "${GREEN}✓ Knowledge base loaded${NC}"
else
    echo -e "${YELLOW}Warning: load_knowledge_base.py not found${NC}"
    exit 1
fi

# Verify knowledge base
echo ""
echo -e "${BLUE}Step 3: Verifying knowledge base...${NC}"
if [ -f "helpers/verify_knowledge_base.py" ]; then
    python3 helpers/verify_knowledge_base.py
    echo -e "${GREEN}✓ Knowledge base verified${NC}"
else
    echo -e "${YELLOW}Warning: verify_knowledge_base.py not found, skipping verification...${NC}"
fi

# Check knowledge quality
echo ""
echo -e "${BLUE}Step 4: Checking knowledge quality...${NC}"
if [ -f "helpers/check_knowledge_quality.py" ]; then
    python3 helpers/check_knowledge_quality.py
    echo -e "${GREEN}✓ Knowledge quality checked${NC}"
else
    echo -e "${YELLOW}Warning: check_knowledge_quality.py not found, skipping...${NC}"
fi

# Initialize logging collections
echo ""
echo -e "${BLUE}Step 5: Initializing logging collections...${NC}"
if [ -f "helpers/init_log_collections.py" ]; then
    python3 helpers/init_log_collections.py
    echo -e "${GREEN}✓ Logging collections initialized${NC}"
else
    echo -e "${YELLOW}Warning: init_log_collections.py not found, skipping...${NC}"
fi

# Deactivate virtual environment
deactivate

echo ""
echo -e "${GREEN}=== Knowledge Base Initialization Complete ===${NC}"
echo ""
echo -e "${BLUE}Collection Statistics:${NC}"
curl -s "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/agent1_student" | python3 -m json.tool 2>/dev/null || echo "Could not fetch collection stats"
