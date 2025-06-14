"""
Swarm-based AI Trading System

This module implements a multi-agent trading system using the Swarms framework.
It provides specialized agents for different aspects of trading:
- Market Analysis Agent
- Risk Management Agent
- Trading Execution Agent
- Portfolio Management Agent
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI
from swarms import Agent, AgentRearrange

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.db.swarm_db import get_swarm_db
from src.trading.alpaca_client import AlpacaPaperTradingClient

logger = logging.getLogger(__name__)


class SwarmTradingSystem:
    """
    Multi-agent trading system using Swarms framework for orchestration.
    """

    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")

        self.alpaca_client = AlpacaPaperTradingClient()
        self.db = get_swarm_db()

        # Initialize OpenAI client with DeepSeek API
        self.openai_client = OpenAI(api_key=self.deepseek_api_key, base_url="https://api.deepseek.com")

        # Create agents
        self.market_analyst = self._create_market_analyst()
        self.risk_manager = self._create_risk_manager()
        self.trader = self._create_trader()
        self.portfolio_manager = self._create_portfolio_manager()

        # Create agent orchestrator
        self.agent_rearrange = AgentRearrange(agents=[self.market_analyst, self.risk_manager, self.trader, self.portfolio_manager], flow="Market Analyst -> Risk Manager -> Trader -> Portfolio Manager")

    def _create_market_analyst(self) -> Agent:
        """Create the Market Analysis Agent"""
        return Agent(
            agent_name="Market Analyst",
            system_prompt="""You are a sophisticated market analyst specializing in equity analysis.

            Your responsibilities:
            - Analyze market data and trends
            - Provide technical and fundamental analysis
            - Identify trading opportunities
            - Assess market conditions and sentiment
            - Generate market insights and recommendations

            You have access to real-time market data and can analyze multiple timeframes.
            Always provide data-driven insights with clear reasoning.

            When you identify a potential trading opportunity, recommend transferring to the Risk Manager for evaluation.
            """,
            llm=self.openai_client,
            max_loops=1,
            tools=[self.get_market_data, self.get_market_status, self.analyze_portfolio_performance],
        )

    def _create_risk_manager(self) -> Agent:
        """Create the Risk Management Agent"""
        return Agent(
            agent_name="Risk Manager",
            system_prompt="""You are a conservative risk management specialist.

            Your responsibilities:
            - Evaluate trading opportunities for risk
            - Ensure position sizing follows risk management rules
            - Monitor portfolio exposure and diversification
            - Prevent excessive risk-taking
            - Validate all trades before execution

            Risk Management Rules:
            - Maximum 5% of portfolio per single position
            - Maximum 20% exposure to any single sector
            - Always consider stop-loss levels
            - Ensure adequate cash reserves (minimum 10%)
            - Never risk more than 2% of portfolio on a single trade

            If a trade passes risk assessment, recommend transferring to the Trader for execution.
            If risk is too high, provide feedback and recommend going back to Market Analyst.
            """,
            llm=self.openai_client,
            max_loops=1,
            tools=[self.get_account_info, self.get_positions, self.calculate_position_size],
        )

    def _create_trader(self) -> Agent:
        """Create the Trading Execution Agent"""
        return Agent(
            agent_name="Trader",
            system_prompt="""You are a precise trading execution specialist.

            Your responsibilities:
            - Execute approved trades with optimal timing
            - Choose appropriate order types (market vs limit)
            - Monitor order status and execution
            - Handle trade confirmations and errors
            - Provide execution reports

            Trading Guidelines:
            - Use limit orders when possible for better fills
            - Consider market conditions for order timing
            - Always confirm trade details before execution
            - Monitor for partial fills and adjust accordingly
            - Report all execution results clearly

            After executing trades, recommend transferring to Portfolio Manager for position monitoring.
            """,
            llm=self.openai_client,
            max_loops=1,
            tools=[self.place_market_order, self.place_limit_order, self.get_orders, self.get_market_status],
        )

    def _create_portfolio_manager(self) -> Agent:
        """Create the Portfolio Management Agent"""
        return Agent(
            agent_name="Portfolio Manager",
            system_prompt="""You are a comprehensive portfolio management specialist.

            Your responsibilities:
            - Monitor overall portfolio performance
            - Track position performance and P&L
            - Manage portfolio rebalancing
            - Provide performance analytics
            - Coordinate with other agents for portfolio optimization

            Portfolio Management Focus:
            - Maintain target asset allocation
            - Monitor correlation between positions
            - Track performance metrics (returns, Sharpe ratio, etc.)
            - Identify underperforming positions
            - Suggest portfolio improvements

            You can recommend transferring to any other agent based on portfolio needs:
            - Market Analyst for new opportunities
            - Risk Manager for risk assessment
            - Trader for rebalancing trades
            """,
            llm=self.openai_client,
            max_loops=1,
            tools=[self.get_account_info, self.get_positions, self.analyze_portfolio_performance, self.get_orders],
        )

    # Trading Functions (async wrappers for Swarm)
    def get_account_info(self) -> str:
        """Get account information"""
        try:
            loop = asyncio.get_event_loop()
            account = loop.run_until_complete(self.alpaca_client.get_account())
            return json.dumps({"account_id": str(account.id), "buying_power": float(account.buying_power), "cash": float(account.cash), "portfolio_value": float(account.portfolio_value), "status": account.status}, indent=2)
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return f"Error retrieving account information: {str(e)}"

    def get_positions(self) -> str:
        """Get current positions"""
        try:
            loop = asyncio.get_event_loop()
            positions = loop.run_until_complete(self.alpaca_client.get_positions())

            if not positions:
                return "No current positions"

            position_data = []
            for pos in positions:
                position_data.append({"symbol": pos.symbol, "qty": float(pos.qty), "market_value": float(pos.market_value), "cost_basis": float(pos.cost_basis), "unrealized_pl": float(pos.unrealized_pl), "unrealized_plpc": float(pos.unrealized_plpc)})

            return json.dumps(position_data, indent=2)
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return f"Error retrieving positions: {str(e)}"

    def get_market_data(self, symbol: str, timeframe: str = "1Day") -> str:
        """Get market data for a symbol"""
        try:
            loop = asyncio.get_event_loop()
            bars = loop.run_until_complete(self.alpaca_client.get_market_data(symbol, timeframe))

            if not bars:
                return f"No market data available for {symbol}"

            # Convert to serializable format
            market_data = []
            for bar in bars[-10:]:  # Last 10 bars
                market_data.append({"timestamp": bar.timestamp.isoformat(), "open": float(bar.open), "high": float(bar.high), "low": float(bar.low), "close": float(bar.close), "volume": int(bar.volume)})

            return json.dumps({"symbol": symbol, "timeframe": timeframe, "data": market_data}, indent=2)
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return f"Error retrieving market data for {symbol}: {str(e)}"

    def get_market_status(self) -> str:
        """Get market status"""
        try:
            loop = asyncio.get_event_loop()
            clock = loop.run_until_complete(self.alpaca_client.get_market_clock())

            return json.dumps({"is_open": clock.is_open, "next_open": clock.next_open.isoformat() if clock.next_open else None, "next_close": clock.next_close.isoformat() if clock.next_close else None}, indent=2)
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return f"Error retrieving market status: {str(e)}"

    def place_market_order(self, symbol: str, qty: int, side: str) -> str:
        """Place a market order"""
        try:
            loop = asyncio.get_event_loop()
            order = loop.run_until_complete(self.alpaca_client.place_market_order(symbol, qty, side))

            return json.dumps({"order_id": str(order.id), "symbol": order.symbol, "qty": int(order.qty), "side": order.side, "order_type": order.order_type, "status": order.status, "submitted_at": order.submitted_at.isoformat()}, indent=2)
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            return f"Error placing market order: {str(e)}"

    def place_limit_order(self, symbol: str, qty: int, side: str, limit_price: float) -> str:
        """Place a limit order"""
        try:
            loop = asyncio.get_event_loop()
            order = loop.run_until_complete(self.alpaca_client.place_limit_order(symbol, qty, side, limit_price))

            return json.dumps({"order_id": str(order.id), "symbol": order.symbol, "qty": int(order.qty), "side": order.side, "order_type": order.order_type, "limit_price": float(order.limit_price), "status": order.status, "submitted_at": order.submitted_at.isoformat()}, indent=2)
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return f"Error placing limit order: {str(e)}"

    def get_orders(self, status: str = "all") -> str:
        """Get orders"""
        try:
            loop = asyncio.get_event_loop()
            orders = loop.run_until_complete(self.alpaca_client.get_orders(status))

            if not orders:
                return f"No {status} orders found"

            order_data = []
            for order in orders:
                order_data.append({"order_id": str(order.id), "symbol": order.symbol, "qty": int(order.qty), "side": order.side, "order_type": order.order_type, "status": order.status, "submitted_at": order.submitted_at.isoformat()})

            return json.dumps(order_data, indent=2)
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return f"Error retrieving orders: {str(e)}"

    def analyze_portfolio_performance(self) -> str:
        """Analyze portfolio performance"""
        try:
            loop = asyncio.get_event_loop()
            account = loop.run_until_complete(self.alpaca_client.get_account())
            positions = loop.run_until_complete(self.alpaca_client.get_positions())

            total_value = float(account.portfolio_value)
            cash = float(account.cash)
            equity = total_value - cash

            analysis = {
                "portfolio_value": total_value,
                "cash": cash,
                "equity": equity,
                "cash_percentage": (cash / total_value) * 100 if total_value > 0 else 0,
                "equity_percentage": (equity / total_value) * 100 if total_value > 0 else 0,
                "position_count": len(positions),
                "analysis_timestamp": datetime.now().isoformat(),
            }

            if positions:
                total_unrealized_pl = sum(float(pos.unrealized_pl) for pos in positions)
                analysis["total_unrealized_pl"] = total_unrealized_pl
                analysis["unrealized_pl_percentage"] = (total_unrealized_pl / equity) * 100 if equity > 0 else 0

            return json.dumps(analysis, indent=2)
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return f"Error analyzing portfolio performance: {str(e)}"

    def calculate_position_size(self, symbol: str, risk_percentage: float = 2.0) -> str:
        """Calculate appropriate position size based on risk management"""
        try:
            loop = asyncio.get_event_loop()
            account = loop.run_until_complete(self.alpaca_client.get_account())

            portfolio_value = float(account.portfolio_value)
            risk_amount = portfolio_value * (risk_percentage / 100)

            # Get current price for position sizing
            bars = loop.run_until_complete(self.alpaca_client.get_market_data(symbol, "1Day"))

            if not bars:
                return f"Cannot calculate position size - no market data for {symbol}"

            current_price = float(bars[-1].close)
            max_shares = int(risk_amount / current_price)

            return json.dumps({"symbol": symbol, "current_price": current_price, "portfolio_value": portfolio_value, "risk_percentage": risk_percentage, "risk_amount": risk_amount, "max_shares": max_shares, "position_value": max_shares * current_price}, indent=2)
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return f"Error calculating position size: {str(e)}"

    async def process_conversation(self, message: str, portfolio_id: str = "default", max_turns: int = 25, starting_agent: str = "market_analyst") -> Dict[str, Any]:
        """
        Process a conversation using the Swarms system
        """
        try:
            logger.info(f"🤖 Starting Swarms conversation with {starting_agent}")

            # Select starting agent
            agent_map = {"market_analyst": self.market_analyst, "risk_manager": self.risk_manager, "trader": self.trader, "portfolio_manager": self.portfolio_manager}

            starting_agent_obj = agent_map.get(starting_agent, self.market_analyst)

            # Run conversation with the selected agent
            response = starting_agent_obj.run(message)

            # Store conversation in database
            from src.models.swarm_models import SwarmConversation

            conversation = SwarmConversation(
                portfolio_id=portfolio_id,
                conversation_id=f"{portfolio_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_message=message,
                agent_responses=[{"agent": starting_agent_obj.agent_name, "response": response, "timestamp": datetime.now().isoformat()}],
                final_agent=starting_agent_obj.agent_name,
                turns_used=1,
                success=True,
                error_message=None,
                conversation_metadata={"starting_agent": starting_agent, "max_turns": max_turns},
            )

            # Save to database
            conversation_id = self.db.save_conversation(conversation)

            return {"success": True, "response": response, "final_agent": starting_agent_obj.agent_name, "conversation_id": conversation_id, "portfolio_id": portfolio_id, "turns_used": 1}

        except Exception as e:
            logger.error(f"❌ Error in Swarms conversation: {e}")

            # Store failed conversation
            from src.models.swarm_models import SwarmConversation

            failed_conversation = SwarmConversation(
                portfolio_id=portfolio_id,
                conversation_id=f"{portfolio_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_failed",
                user_message=message,
                agent_responses=[],
                final_agent=starting_agent,
                turns_used=0,
                success=False,
                error_message=str(e),
                conversation_metadata={"starting_agent": starting_agent, "max_turns": max_turns, "error": str(e)},
            )

            try:
                conversation_id = self.db.save_conversation(failed_conversation)
            except Exception as db_error:
                logger.error(f"Failed to save error conversation: {db_error}")
                conversation_id = None

            return {"success": False, "error": str(e), "response": f"Error processing conversation: {str(e)}", "conversation_id": conversation_id, "portfolio_id": portfolio_id}

    def get_conversation_history(self, portfolio_id: str = "default") -> List[Dict]:
        """Get conversation history for a portfolio"""
        return self.db.get_conversation_history(portfolio_id)

    def clear_conversation_history(self, portfolio_id: str = "default") -> bool:
        """Clear conversation history for a portfolio"""
        try:
            # Note: This would need to be implemented in the database layer
            # For now, we'll just return True as a placeholder
            logger.info(f"Clear conversation history requested for portfolio: {portfolio_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
            return False
