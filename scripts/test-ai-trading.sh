#!/bin/bash

# Test AI Trading Bot
# This script demonstrates the AI trading capabilities

API_TOKEN="default-dev-token"
BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🤖 AI Trading Bot Test Suite${NC}"
echo "=================================================="

# Test 1: Simple AI Chat
echo -e "\n${BLUE}Test 1: AI Chat - Portfolio Analysis${NC}"
echo "Asking AI to analyze current portfolio..."

curl -s -X POST -H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Please analyze my current portfolio and account status. What do you think about my positions?"
      }
    ]
  }' \
  "$BASE_URL/trading/ai-conversation" | jq '.ai_response'

echo -e "\n${YELLOW}Waiting 3 seconds...${NC}"
sleep 3

# Test 2: AI Trading Decision with Context
echo -e "\n${BLUE}Test 2: AI Trading Decision - Market Context${NC}"
echo "Providing market context and asking for trading decisions..."

curl -s -X POST -H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json" \
  -d '{
    "context": "The market has been volatile lately. Tech stocks are showing mixed signals. I want to rebalance my portfolio and maybe take some profits or add to positions.",
    "symbols": ["AAPL", "TSLA", "NVDA", "MSFT"]
  }' \
  "$BASE_URL/trading/ai-trade" | jq '{
    ai_response: .ai_response,
    trade_actions: .trade_actions,
    total_iterations: .total_iterations
  }'

echo -e "\n${YELLOW}Waiting 3 seconds...${NC}"
sleep 3

# Test 3: Conversation with Trading History
echo -e "\n${BLUE}Test 3: Conversation with Context${NC}"
echo "Having a conversation with trading history context..."

curl -s -X POST -H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json" \
  -d '{
    "context": "I just placed several orders earlier today. Can you check my recent orders and current positions, then advise if I should make any adjustments?",
    "conversation_messages": [
      {
        "role": "user",
        "content": "I bought some AAPL and TSLA earlier today"
      },
      {
        "role": "assistant",
        "content": "I see you made some purchases. Let me check your current positions and recent orders to provide better advice."
      },
      {
        "role": "user",
        "content": "Yes, please analyze my portfolio and suggest next steps"
      }
    ]
  }' \
  "$BASE_URL/trading/ai-trade" | jq '{
    ai_response: .ai_response,
    trade_actions: .trade_actions,
    conversation_length: .conversation_length
  }'

echo -e "\n${YELLOW}Waiting 3 seconds...${NC}"
sleep 3

# Test 4: Specific Trading Question
echo -e "\n${BLUE}Test 4: Specific Trading Question${NC}"
echo "Asking AI about a specific trading scenario..."

curl -s -X POST -H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "I have $199K buying power. Should I buy more NVDA at current prices? What about diversification? Please check current market data and my positions before advising."
      }
    ],
    "max_iterations": 3
  }' \
  "$BASE_URL/trading/ai-conversation" | jq '{
    ai_response: .ai_response,
    trade_actions: .trade_actions,
    total_iterations: .total_iterations
  }'

echo -e "\n${GREEN}✅ AI Trading Bot Tests Complete!${NC}"
echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "- The AI can analyze your portfolio and account"
echo "- It can make trading decisions based on context"
echo "- It maintains conversation history"
echo "- It can execute actual trades when confident"
echo "- All trades include AI reasoning"
echo ""
echo -e "${BLUE}Check your orders with:${NC} ./trading_cli.sh orders"
echo -e "${BLUE}Check your positions with:${NC} ./trading_cli.sh positions"
