#!/bin/bash

# Trading CLI Helper Script
# Usage: ./trading_cli.sh [command] [args...]

API_TOKEN="default-dev-token"
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ "$method" = "GET" ]; then
        curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL$endpoint"
    else
        curl -s -X "$method" -H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint"
    fi
}

# Commands
case "$1" in
    "account"|"acc")
        echo -e "${BLUE}📊 Account Information:${NC}"
        api_call GET "/trading/account" | jq
        ;;

    "positions"|"pos")
        echo -e "${BLUE}💼 Current Positions:${NC}"
        api_call GET "/trading/positions" | jq
        ;;

    "orders"|"ord")
        echo -e "${BLUE}📋 Recent Orders:${NC}"
        api_call GET "/trading/orders" | jq '.orders[0:5]'
        ;;

    "market"|"price")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Usage: $0 market SYMBOL${NC}"
            exit 1
        fi
        echo -e "${BLUE}📈 Market Data for $2:${NC}"
        api_call GET "/trading/market-data/$2" | jq '.bars[0:3]'
        ;;

    "status")
        echo -e "${BLUE}🕐 Market Status:${NC}"
        api_call GET "/trading/market-status" | jq
        ;;

    "buy")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}❌ Usage: $0 buy SYMBOL QUANTITY [LIMIT_PRICE]${NC}"
            echo -e "${YELLOW}Examples:${NC}"
            echo -e "  $0 buy AAPL 10          # Market order"
            echo -e "  $0 buy AAPL 10 150.00   # Limit order"
            exit 1
        fi

        if [ -n "$4" ]; then
            # Limit order
            echo -e "${GREEN}💰 Placing LIMIT BUY order: $3 shares of $2 at \$$4${NC}"
            data="{\"symbol\": \"$2\", \"qty\": $3, \"side\": \"buy\", \"limit_price\": $4, \"time_in_force\": \"day\"}"
            api_call POST "/trading/orders/limit" "$data" | jq
        else
            # Market order
            echo -e "${GREEN}💰 Placing MARKET BUY order: $3 shares of $2${NC}"
            data="{\"symbol\": \"$2\", \"qty\": $3, \"side\": \"buy\", \"time_in_force\": \"day\"}"
            api_call POST "/trading/orders/market" "$data" | jq
        fi
        ;;

    "sell")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}❌ Usage: $0 sell SYMBOL QUANTITY [LIMIT_PRICE]${NC}"
            exit 1
        fi

        if [ -n "$4" ]; then
            # Limit order
            echo -e "${YELLOW}💸 Placing LIMIT SELL order: $3 shares of $2 at \$$4${NC}"
            data="{\"symbol\": \"$2\", \"qty\": $3, \"side\": \"sell\", \"limit_price\": $4, \"time_in_force\": \"day\"}"
            api_call POST "/trading/orders/limit" "$data" | jq
        else
            # Market order
            echo -e "${YELLOW}💸 Placing MARKET SELL order: $3 shares of $2${NC}"
            data="{\"symbol\": \"$2\", \"qty\": $3, \"side\": \"sell\", \"time_in_force\": \"day\"}"
            api_call POST "/trading/orders/market" "$data" | jq
        fi
        ;;

    "summary"|"portfolio")
        echo -e "${BLUE}📊 Portfolio Summary:${NC}"
        api_call GET "/trading/portfolio-summary" | jq '.summary'
        ;;

    "ai")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Usage: $0 ai SYMBOL1,SYMBOL2,SYMBOL3${NC}"
            echo -e "${YELLOW}Example: $0 ai AAPL,TSLA,NVDA${NC}"
            exit 1
        fi
        echo -e "${BLUE}🤖 AI Analysis for: $2${NC}"
        # Convert comma-separated symbols to JSON array
        symbols=$(echo "$2" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
        api_call POST "/trading/ai-analysis" "$symbols" | jq
        ;;

    "ai-trade")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Usage: $0 ai-trade \"CONTEXT\" [SYMBOLS]${NC}"
            echo -e "${YELLOW}Example: $0 ai-trade \"Market is bullish, consider tech stocks\" AAPL,TSLA${NC}"
            exit 1
        fi

        context="$2"
        symbols_array="[]"

        if [ -n "$3" ]; then
            # Convert comma-separated symbols to JSON array
            symbols_array=$(echo "$3" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
        fi

        echo -e "${BLUE}🤖 AI Trading Decision: $context${NC}"
        data="{\"context\": \"$context\", \"symbols\": $symbols_array}"
        api_call POST "/trading/ai-trade" "$data" | jq
        ;;

    "ai-chat")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Usage: $0 ai-chat \"MESSAGE\"${NC}"
            echo -e "${YELLOW}Example: $0 ai-chat \"Should I buy more AAPL today?\"${NC}"
            exit 1
        fi

        message="$2"
        echo -e "${BLUE}🤖 AI Conversation: $message${NC}"
        data="{\"messages\": [{\"role\": \"user\", \"content\": \"$message\"}]}"
        api_call POST "/trading/ai-conversation" "$data" | jq
        ;;

    "help"|"")
        echo -e "${GREEN}🚀 Trading CLI Commands:${NC}"
        echo ""
        echo -e "${BLUE}Account & Portfolio:${NC}"
        echo -e "  $0 account (acc)     - Show account information"
        echo -e "  $0 positions (pos)   - Show current positions"
        echo -e "  $0 orders (ord)      - Show recent orders"
        echo -e "  $0 summary           - Show portfolio summary"
        echo ""
        echo -e "${BLUE}Market Data:${NC}"
        echo -e "  $0 market SYMBOL     - Get market data for symbol"
        echo -e "  $0 status            - Check market open/close status"
        echo ""
        echo -e "${BLUE}Trading:${NC}"
        echo -e "  $0 buy SYMBOL QTY [PRICE]   - Buy shares (market or limit)"
        echo -e "  $0 sell SYMBOL QTY [PRICE]  - Sell shares (market or limit)"
        echo ""
        echo -e "${BLUE}AI Analysis:${NC}"
        echo -e "  $0 ai SYMBOL1,SYMBOL2       - Get AI analysis (legacy)"
        echo -e "  $0 ai-trade \"CONTEXT\" [SYMBOLS] - AI trading decisions"
        echo -e "  $0 ai-chat \"MESSAGE\"        - Chat with AI trader"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo -e "  $0 buy AAPL 10              # Buy 10 AAPL at market price"
        echo -e "  $0 buy TSLA 5 200.00        # Buy 5 TSLA at \$200 limit"
        echo -e "  $0 market NVDA              # Get NVDA price data"
        echo -e "  $0 ai AAPL,TSLA,NVDA        # Analyze multiple stocks"
        echo -e "  $0 ai-trade \"Bullish on tech\" AAPL,MSFT  # AI trading decision"
        echo -e "  $0 ai-chat \"Should I sell my TSLA?\"      # Chat with AI"
        ;;

    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo -e "Run ${GREEN}$0 help${NC} for available commands"
        exit 1
        ;;
esac
