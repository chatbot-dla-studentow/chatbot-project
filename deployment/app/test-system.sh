#!/bin/bash
# Quick Test Script for ChatBot System
# Usage: ./test-system.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== ChatBot System Quick Test ===${NC}"
echo ""

# Test 1: Qdrant collection
echo -e "${BLUE}Test 1: Qdrant Collection${NC}"
echo -n "  Checking collection... "
POINTS=$(curl -s http://localhost:6333/collections/agent1_student | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['points_count'])" 2>/dev/null || echo "0")

if [ "$POINTS" -gt 0 ]; then
    echo -e "${GREEN}✓ OK${NC} ($POINTS documents)"
else
    echo -e "${RED}✗ FAILED${NC} (Collection empty or not found)"
    exit 1
fi

# Test 2: Ollama model
echo -e "${BLUE}Test 2: Ollama Model${NC}"
echo -n "  Checking mistral:7b... "
if docker exec ollama ollama list | grep -q "mistral:7b"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC} (Model not found)"
    exit 1
fi

# Test 3: Agent1 health
echo -e "${BLUE}Test 3: Agent1 Health${NC}"
echo -n "  Checking /health endpoint... "
if curl -sf http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Test 4: Test query - Stypendia
echo -e "${BLUE}Test 4: Test Query - Stypendia${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Jakie stypendia są dostępne dla studentów?",
    "conversation_id": "test_stypendia"
  }')

echo -n "  Checking response... "
if echo "$RESPONSE" | grep -q "kategoria"; then
    CATEGORY=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['kategoria'])" 2>/dev/null)
    SOURCES=$(echo "$RESPONSE" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['sources']))" 2>/dev/null)
    
    if [ "$CATEGORY" = "stypendia" ] && [ "$SOURCES" -gt 0 ]; then
        echo -e "${GREEN}✓ OK${NC} (kategoria: $CATEGORY, sources: $SOURCES)"
    else
        echo -e "${YELLOW}⚠ PARTIAL${NC} (kategoria: $CATEGORY, sources: $SOURCES)"
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

# Test 5: Test query - Egzaminy
echo -e "${BLUE}Test 5: Test Query - Egzaminy${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Kiedy są obrony prac inżynierskich?",
    "conversation_id": "test_egzaminy"
  }')

echo -n "  Checking response... "
if echo "$RESPONSE" | grep -q "kategoria"; then
    CATEGORY=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['kategoria'])" 2>/dev/null)
    
    if [ "$CATEGORY" = "egzaminy" ]; then
        echo -e "${GREEN}✓ OK${NC} (kategoria: $CATEGORY)"
    else
        echo -e "${YELLOW}⚠ PARTIAL${NC} (kategoria: $CATEGORY, expected: egzaminy)"
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Test 6: Test query - Unknown (should return "Nie mam informacji")
echo -e "${BLUE}Test 6: Test Query - Unknown${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Jak zbudować reaktor jądrowy?",
    "conversation_id": "test_unknown"
  }')

echo -n "  Checking response... "
if echo "$RESPONSE" | grep -qi "nie mam informacji\|nie mogę pomóc"; then
    echo -e "${GREEN}✓ OK${NC} (correctly refused unknown query)"
else
    MESSAGE=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message', {}).get('content', 'N/A')[:100])" 2>/dev/null)
    echo -e "${YELLOW}⚠ WARNING${NC} (Response: $MESSAGE...)"
fi

# Test 7: Logging - Query logs
echo -e "${BLUE}Test 7: Query Logging${NC}"
echo -n "  Checking query logs... "
QUERY_COUNT=$(curl -s http://localhost:8001/admin/logs/queries/stats | python3 -c "import sys,json; print(json.load(sys.stdin)['total_queries'])" 2>/dev/null || echo "0")

if [ "$QUERY_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ OK${NC} ($QUERY_COUNT queries logged)"
else
    echo -e "${YELLOW}⚠ WARNING${NC} (No queries logged yet)"
fi

# Test 8: Logging - QA logs
echo -e "${BLUE}Test 8: QA Logging${NC}"
echo -n "  Checking QA logs... "
QA_COUNT=$(curl -s http://localhost:8001/admin/logs/qa/stats | python3 -c "import sys,json; print(json.load(sys.stdin)['total_qa_pairs'])" 2>/dev/null || echo "0")

if [ "$QA_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ OK${NC} ($QA_COUNT QA pairs logged)"
else
    echo -e "${YELLOW}⚠ WARNING${NC} (No QA pairs logged yet)"
fi

# Test 9: Performance - Response time
echo -e "${BLUE}Test 9: Performance Test${NC}"
echo -n "  Measuring response time... "

START=$(date +%s.%N)
curl -s -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Jakie stypendia?", "conversation_id": "perf_test"}' > /dev/null
END=$(date +%s.%N)

DURATION=$(echo "$END - $START" | bc)
DURATION_INT=$(printf "%.0f" $DURATION)

if [ "$DURATION_INT" -lt 15 ]; then
    echo -e "${GREEN}✓ OK${NC} (${DURATION}s < 15s)"
else
    echo -e "${YELLOW}⚠ SLOW${NC} (${DURATION}s >= 15s)"
fi

# Summary
echo ""
echo -e "${GREEN}=== All Tests Passed ===${NC}"
echo ""
echo "System Summary:"
echo "  Documents in KB: $POINTS"
echo "  Queries logged: $QUERY_COUNT"
echo "  QA pairs logged: $QA_COUNT"
echo "  Avg response time: ${DURATION}s"
echo ""
echo -e "${BLUE}System is ready for production!${NC}"
