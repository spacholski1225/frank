#!/bin/bash
# MVP validation script for Frank the Assistant

set -e

echo "🚀 Frank the Assistant - MVP Validation"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check environment
echo "📋 Checking environment..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ ANTHROPIC_API_KEY not set${NC}"
    echo "   Set it with: export ANTHROPIC_API_KEY=your_key"
    exit 1
fi
echo -e "${GREEN}✓ API key found${NC}"

# Check required files
echo ""
echo "📁 Checking required files..."
required_files=(
    "frank_system/configs/system_prompt.md"
    "frank_system/configs/food_database.md"
    "src/main.py"
    "src/agent.py"
    "src/tools/food_tool.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        exit 1
    fi
done

# Run unit tests
echo ""
echo "🧪 Running unit tests..."
pytest tests/ -v --ignore=tests/test_integration.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All unit tests passed${NC}"
else
    echo -e "${RED}❌ Some unit tests failed${NC}"
    exit 1
fi

# Start server in background
echo ""
echo "🌐 Starting Frank server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
sleep 5

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    kill $SERVER_PID 2>/dev/null || true
}
trap cleanup EXIT

# Test health endpoint
echo ""
echo "❤️  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test chat endpoint
echo ""
echo "💬 Testing chat endpoint..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Zjadłem owsiankę"}')

if echo "$CHAT_RESPONSE" | grep -q "session_id"; then
    echo -e "${GREEN}✓ Chat endpoint working${NC}"
    echo "   Response preview: $(echo $CHAT_RESPONSE | jq -r .response | head -c 50)..."
else
    echo -e "${RED}❌ Chat endpoint failed${NC}"
    echo "   Response: $CHAT_RESPONSE"
    exit 1
fi

# Test refresh-db endpoint
echo ""
echo "🔄 Testing database refresh..."
REFRESH_RESPONSE=$(curl -s -X POST http://localhost:8000/v1/system/refresh-db)
if echo "$REFRESH_RESPONSE" | grep -q "reloaded"; then
    echo -e "${GREEN}✓ Database refresh working${NC}"
else
    echo -e "${RED}❌ Database refresh failed${NC}"
    exit 1
fi

# Test nutrition status
echo ""
echo "📊 Testing nutrition status..."
NUTRITION_RESPONSE=$(curl -s http://localhost:8000/v1/status/nutrition)
if echo "$NUTRITION_RESPONSE" | grep -q "date"; then
    echo -e "${GREEN}✓ Nutrition status working${NC}"
else
    echo -e "${RED}❌ Nutrition status failed${NC}"
    exit 1
fi

# Summary
echo ""
echo "========================================"
echo -e "${GREEN}🎉 MVP VALIDATION PASSED!${NC}"
echo "========================================"
echo ""
echo "Frank the Assistant is ready to use!"
echo ""
echo "Next steps:"
echo "1. Try it: curl -X POST http://localhost:8000/v1/chat -d '{\"message\":\"Hello Frank\"}'"
echo "2. View logs: ls frank_system/obsidian_vault/Daily_Logs/"
echo "3. Customize: edit frank_system/configs/food_database.md"
