import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekTradingBot:
    """AI Trading Bot using DeepSeek with function calling capabilities"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

        # Import trading client
        from trading.alpaca_client import AlpacaPaperTradingClient

        self.trading_client = AlpacaPaperTradingClient()

        # Define available trading functions
        self.tools = [
            {"type": "function", "function": {"name": "get_account_info", "description": "Get current account information including buying power, cash, and portfolio value", "parameters": {"type": "object", "properties": {}, "required": []}}},
            {"type": "function", "function": {"name": "get_positions", "description": "Get all current positions in the portfolio", "parameters": {"type": "object", "properties": {}, "required": []}}},
            {
                "type": "function",
                "function": {
                    "name": "get_market_data",
                    "description": "Get real-time market data for a stock symbol",
                    "parameters": {"type": "object", "properties": {"symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL, TSLA)"}, "timeframe": {"type": "string", "description": "Timeframe: 1Min, 5Min, 15Min, 30Min, 1Hour, 1Day", "default": "1Day"}}, "required": ["symbol"]},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "place_market_order",
                    "description": "Place a market order to buy or sell stocks immediately at current market price",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL, TSLA)"},
                            "quantity": {"type": "number", "description": "Number of shares to trade"},
                            "side": {"type": "string", "enum": ["buy", "sell"], "description": "Buy or sell"},
                            "reason": {"type": "string", "description": "Reasoning for this trade decision"},
                        },
                        "required": ["symbol", "quantity", "side", "reason"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "place_limit_order",
                    "description": "Place a limit order to buy or sell stocks at a specific price",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL, TSLA)"},
                            "quantity": {"type": "number", "description": "Number of shares to trade"},
                            "side": {"type": "string", "enum": ["buy", "sell"], "description": "Buy or sell"},
                            "limit_price": {"type": "number", "description": "Limit price for the order"},
                            "reason": {"type": "string", "description": "Reasoning for this trade decision"},
                        },
                        "required": ["symbol", "quantity", "side", "limit_price", "reason"],
                    },
                },
            },
            {"type": "function", "function": {"name": "get_market_status", "description": "Check if the market is currently open or closed", "parameters": {"type": "object", "properties": {}, "required": []}}},
            {"type": "function", "function": {"name": "get_orders", "description": "Get recent orders and their status", "parameters": {"type": "object", "properties": {"status": {"type": "string", "enum": ["open", "closed", "all"], "default": "all"}, "limit": {"type": "integer", "default": 10}}, "required": []}}},
            {"type": "function", "function": {"name": "analyze_portfolio_performance", "description": "Analyze current portfolio performance and provide insights", "parameters": {"type": "object", "properties": {}, "required": []}}},
            {
                "type": "function",
                "function": {
                    "name": "continue_analysis",
                    "description": "Continue with additional analysis or trading decisions. Use this to make multiple iterative decisions.",
                    "parameters": {"type": "object", "properties": {"reason": {"type": "string", "description": "Reason for continuing analysis"}, "next_action": {"type": "string", "description": "What you plan to do next"}}, "required": ["reason", "next_action"]},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_analysis",
                    "description": "Signal that analysis and trading decisions are complete. Use this when you're satisfied with your actions.",
                    "parameters": {"type": "object", "properties": {"summary": {"type": "string", "description": "Summary of all actions taken"}, "final_recommendation": {"type": "string", "description": "Final recommendation or status"}}, "required": ["summary", "final_recommendation"]},
                },
            },
        ]

    async def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trading function and return the result"""
        try:
            logger.info(f"🔧 Executing function: {function_name} with args: {arguments}")

            if function_name == "get_account_info":
                return await self.trading_client.get_account_info()

            elif function_name == "get_positions":
                positions = await self.trading_client.get_positions()
                return {"positions": positions, "total_positions": len(positions)}

            elif function_name == "get_market_data":
                return await self.trading_client.get_market_data(symbol=arguments["symbol"], timeframe=arguments.get("timeframe", "1Day"))

            elif function_name == "place_market_order":
                result = await self.trading_client.place_market_order(symbol=arguments["symbol"], quantity=arguments["quantity"], side=arguments["side"])
                # Log the trade decision
                logger.info(f"🤖 AI TRADE DECISION: {arguments['side'].upper()} {arguments['quantity']} {arguments['symbol']} - Reason: {arguments['reason']}")
                result["ai_reasoning"] = arguments["reason"]
                return result

            elif function_name == "place_limit_order":
                result = await self.trading_client.place_limit_order(symbol=arguments["symbol"], quantity=arguments["quantity"], side=arguments["side"], limit_price=arguments["limit_price"])
                # Log the trade decision
                logger.info(f"🤖 AI TRADE DECISION: {arguments['side'].upper()} {arguments['quantity']} {arguments['symbol']} @ ${arguments['limit_price']} - Reason: {arguments['reason']}")
                result["ai_reasoning"] = arguments["reason"]
                return result

            elif function_name == "get_market_status":
                return await self.trading_client.get_market_status()

            elif function_name == "get_orders":
                orders = await self.trading_client.get_orders(status=arguments.get("status", "all"), limit=arguments.get("limit", 10))
                return {"orders": orders, "total_orders": len(orders)}

            elif function_name == "analyze_portfolio_performance":
                # Get comprehensive portfolio data
                account = await self.trading_client.get_account_info()
                positions = await self.trading_client.get_positions()
                orders = await self.trading_client.get_orders(limit=20)

                # Calculate performance metrics
                total_value = float(account.get("portfolio_value", 0))
                cash = float(account.get("cash", 0))
                buying_power = float(account.get("buying_power", 0))

                return {
                    "portfolio_value": total_value,
                    "cash": cash,
                    "buying_power": buying_power,
                    "positions_count": len(positions),
                    "recent_orders_count": len(orders),
                    "positions": positions[:5],  # Top 5 positions
                    "recent_orders": orders[:5],  # Recent 5 orders
                }

            elif function_name == "continue_analysis":
                logger.info(f"🔄 AI continuing analysis: {arguments['reason']}")
                logger.info(f"📋 Next action: {arguments['next_action']}")
                return {"status": "continuing", "reason": arguments["reason"], "next_action": arguments["next_action"], "timestamp": datetime.now().isoformat()}

            elif function_name == "complete_analysis":
                logger.info(f"✅ AI completing analysis: {arguments['summary']}")
                logger.info(f"🎯 Final recommendation: {arguments['final_recommendation']}")
                return {"status": "completed", "summary": arguments["summary"], "final_recommendation": arguments["final_recommendation"], "timestamp": datetime.now().isoformat()}

            else:
                return {"error": f"Unknown function: {function_name}"}

        except Exception as e:
            logger.error(f"❌ Error executing function {function_name}: {e}")
            return {"error": str(e)}

    async def store_conversation(self, portfolio_id: int, conversation_log: List[Dict], trade_actions: List[Dict], final_result: Dict) -> bool:
        """Store conversation and trading decisions in database"""
        try:
            # Import here to avoid circular imports
            import os

            api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            api_token = os.getenv("API_TOKEN", "default-dev-token")

            store_data = {
                "portfolio_id": portfolio_id,
                "analysis_type": "ai_iterative_trading",
                "analysis_result": {"conversation_log": conversation_log, "trade_actions": trade_actions, "final_result": final_result, "total_iterations": len([msg for msg in conversation_log if msg.get("role") == "assistant"]), "timestamp": datetime.now().isoformat()},
                "conversation_context": conversation_log,
                "symbols_analyzed": list(set([action.get("arguments", {}).get("symbol") for action in trade_actions if action.get("arguments", {}).get("symbol")])),
                "timestamp": datetime.now().isoformat(),
            }

            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{api_base_url}/portfolio/store-analysis", headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}, json=store_data) as response:
                    if response.status == 200:
                        logger.info(f"💾 Conversation stored for portfolio {portfolio_id}")
                        return True
                    else:
                        logger.warning(f"⚠️ Failed to store conversation: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"❌ Error storing conversation: {e}")
            return False

    async def process_conversation(self, messages: List[Dict[str, str]], max_iterations: int = 25, portfolio_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a conversation with the AI trading bot with iterative decision making

        Args:
            messages: List of conversation messages with role and content
            max_iterations: Maximum number of function calls (default 25)
            portfolio_id: Portfolio ID to store conversation
        """
        try:
            # Add system prompt for trading context
            system_prompt = {
                "role": "system",
                "content": """You are an AI trading assistant with access to real-time market data and trading functions.

TRADING GUIDELINES:
- You can make multiple iterative decisions up to 25 function calls
- Only make trades when you have strong conviction based on data analysis
- Always provide clear reasoning for trade decisions
- Consider risk management - don't risk more than 5% of portfolio on a single trade
- Check market status before placing orders
- Analyze current positions before making new trades
- Use limit orders for better price control when appropriate
- Consider market conditions, trends, and portfolio balance

ITERATIVE DECISION MAKING:
- Use 'continue_analysis' to make additional analysis or trading decisions
- Use 'complete_analysis' when you're satisfied with your actions
- You can analyze multiple stocks, place multiple orders, and reassess
- Think of this as a for loop - keep going until you're done

AVAILABLE FUNCTIONS:
- get_account_info: Check buying power and portfolio value
- get_positions: See current holdings
- get_market_data: Get real-time price data
- place_market_order: Execute immediate trades
- place_limit_order: Set price-specific trades
- get_market_status: Check if market is open
- get_orders: Review recent trading activity
- analyze_portfolio_performance: Get comprehensive portfolio analysis
- continue_analysis: Continue with more decisions
- complete_analysis: Signal you're done

Always explain your reasoning and be conservative with trades unless there's strong evidence.""",
            }

            # Prepare messages with system prompt
            full_messages = [system_prompt] + messages

            iteration = 0
            trade_actions = []
            analysis_complete = False
            conversation_log = []

            while iteration < max_iterations and not analysis_complete:
                iteration += 1
                logger.info(f"🤖 AI Processing iteration {iteration}/{max_iterations}")

                # Send messages to DeepSeek
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=full_messages,
                    tools=self.tools,
                    temperature=0.1,  # Lower temperature for more consistent trading decisions
                )

                message = response.choices[0].message

                # Log the conversation
                conversation_entry = {"iteration": iteration, "role": "assistant", "content": message.content, "tool_calls": [{"function": tool_call.function.name, "arguments": json.loads(tool_call.function.arguments)} for tool_call in (message.tool_calls or [])], "timestamp": datetime.now().isoformat()}
                conversation_log.append(conversation_entry)

                # Add AI response to conversation
                full_messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})

                # Check if AI wants to call functions
                if message.tool_calls:
                    logger.info(f"🔧 AI requested {len(message.tool_calls)} function calls")

                    # Execute each function call
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)

                        # Execute the function
                        result = await self.execute_function(function_name, arguments)

                        # Check for completion signal
                        if function_name == "complete_analysis":
                            analysis_complete = True
                            logger.info(f"🏁 AI signaled completion after {iteration} iterations")

                        # Track trading actions
                        if function_name in ["place_market_order", "place_limit_order"]:
                            trade_actions.append({"iteration": iteration, "function": function_name, "arguments": arguments, "result": result, "timestamp": datetime.now().isoformat()})

                        # Add function result to conversation
                        full_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(result, default=str),  # Convert UUID and other objects to string
                            }
                        )

                    # Continue conversation after function calls if not complete
                    if not analysis_complete:
                        continue
                else:
                    # No more function calls, AI has finished
                    break

            # Prepare final result
            final_result = {"ai_response": message.content, "trade_actions": trade_actions, "total_iterations": iteration, "conversation_length": len(full_messages), "analysis_completed": analysis_complete, "max_iterations_reached": iteration >= max_iterations, "timestamp": datetime.now().isoformat()}

            # Store conversation if portfolio_id provided
            if portfolio_id:
                await self.store_conversation(portfolio_id, conversation_log, trade_actions, final_result)

            return final_result

        except Exception as e:
            logger.error(f"❌ Error processing conversation: {e}")
            return {"error": str(e), "ai_response": None, "trade_actions": [], "timestamp": datetime.now().isoformat()}

    async def analyze_and_trade(self, context: str, symbols: List[str] = None, portfolio_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze market conditions and make trading decisions with iterative capability

        Args:
            context: Current market context or news
            symbols: Optional list of symbols to focus on
            portfolio_id: Portfolio ID to store conversation
        """
        symbols_text = f" Focus on these symbols: {', '.join(symbols)}" if symbols else ""

        messages = [
            {
                "role": "user",
                "content": f"""Analyze the current market situation and my portfolio. {context}{symbols_text}

Please:
1. Check my current account status and positions
2. Get market data for relevant symbols
3. Analyze portfolio performance
4. Make trading recommendations or execute trades if you see strong opportunities
5. Use continue_analysis to make multiple decisions if needed
6. Use complete_analysis when you're satisfied with your actions
7. Explain your reasoning for any actions taken

Be conservative and only trade when you have high confidence. You can make up to 25 function calls to thoroughly analyze and execute trades.""",
            }
        ]

        return await self.process_conversation(messages, portfolio_id=portfolio_id)


# Create global instance
trading_bot = DeepSeekTradingBot()
