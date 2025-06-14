"""
Database models for Swarm AI Trading System
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class AgentPrompt(BaseModel):
    """Model for storing agent system prompts in database"""

    id: Optional[int] = None
    agent_name: str  # "market_analyst", "risk_manager", "trader", "portfolio_manager"
    prompt_version: str  # Version identifier like "v1.0", "v2.1"
    system_prompt: str  # The actual system prompt text
    is_active: bool = True  # Whether this prompt version is currently active
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: Optional[str] = None  # User who created this prompt
    description: Optional[str] = None  # Description of changes in this version


class PortfolioConfig(BaseModel):
    """Model for portfolio-specific configurations"""

    id: Optional[int] = None
    portfolio_id: str  # Portfolio identifier
    name: str  # Human-readable portfolio name
    symbols: List[str]  # List of symbols to focus on
    risk_tolerance: str  # "conservative", "moderate", "aggressive"
    max_position_size_pct: float = 5.0  # Max % of portfolio per position
    max_sector_exposure_pct: float = 20.0  # Max % exposure to any sector
    cash_reserve_pct: float = 10.0  # Minimum cash reserve %
    trading_enabled: bool = True  # Whether AI can execute trades
    rebalance_frequency: str = "weekly"  # "daily", "weekly", "monthly"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    is_active: bool = True


class SwarmConversation(BaseModel):
    """Model for storing Swarm conversation history"""

    id: Optional[int] = None
    portfolio_id: str
    conversation_id: str  # Unique identifier for this conversation
    user_message: str
    agent_responses: List[Dict]  # Full conversation history
    final_agent: str  # Which agent handled the final response
    turns_used: int
    success: bool
    error_message: Optional[str] = None
    created_at: datetime = datetime.now()
    metadata: Optional[Dict] = None  # Additional context/metadata


class TradingDecision(BaseModel):
    """Model for storing AI trading decisions"""

    id: Optional[int] = None
    conversation_id: str  # Links to SwarmConversation
    portfolio_id: str
    decision_type: str  # "buy", "sell", "hold", "rebalance"
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    reasoning: str  # AI's reasoning for the decision
    confidence_score: Optional[float] = None  # 0-1 confidence level
    risk_assessment: Optional[str] = None
    executed: bool = False
    execution_result: Optional[Dict] = None  # Result of trade execution
    created_at: datetime = datetime.now()
    executed_at: Optional[datetime] = None


class MarketContext(BaseModel):
    """Model for storing market context data"""

    id: Optional[int] = None
    portfolio_id: str
    context_type: str  # "market_data", "news", "earnings", "economic_indicator"
    symbol: Optional[str] = None  # Specific symbol or None for market-wide
    data: Dict  # The actual context data
    relevance_score: Optional[float] = None  # How relevant this is (0-1)
    created_at: datetime = datetime.now()
    expires_at: Optional[datetime] = None  # When this context becomes stale


# Default system prompts for each agent
DEFAULT_AGENT_PROMPTS = {
    "market_analyst": """You are a sophisticated market analyst specializing in equity analysis.

Your responsibilities:
- Analyze market data and trends for the portfolio's symbols: {symbols}
- Provide technical and fundamental analysis
- Identify trading opportunities within the portfolio's risk tolerance: {risk_tolerance}
- Assess market conditions and sentiment
- Generate market insights and recommendations

Portfolio Context:
- Portfolio ID: {portfolio_id}
- Portfolio Name: {portfolio_name}
- Current Symbols: {symbols}
- Risk Tolerance: {risk_tolerance}
- Max Position Size: {max_position_size_pct}%
- Cash Reserve Target: {cash_reserve_pct}%

You have access to real-time market data and can analyze multiple timeframes.
Always provide data-driven insights with clear reasoning.

When you identify a potential trading opportunity, transfer to the Risk Manager for evaluation.
""",
    "risk_manager": """You are a conservative risk management specialist for portfolio {portfolio_id}.

Your responsibilities:
- Evaluate trading opportunities for risk within portfolio parameters
- Ensure position sizing follows risk management rules
- Monitor portfolio exposure and diversification
- Prevent excessive risk-taking
- Validate all trades before execution

Portfolio Risk Management Rules:
- Maximum {max_position_size_pct}% of portfolio per single position
- Maximum {max_sector_exposure_pct}% exposure to any single sector
- Always consider stop-loss levels
- Ensure adequate cash reserves (minimum {cash_reserve_pct}%)
- Risk tolerance level: {risk_tolerance}
- Never risk more than 2% of portfolio on a single trade

Current Portfolio Context:
- Portfolio: {portfolio_name} ({portfolio_id})
- Symbols: {symbols}
- Trading Enabled: {trading_enabled}

If a trade passes risk assessment, transfer to the Trader for execution.
If risk is too high, provide feedback and transfer back to Market Analyst.
""",
    "trader": """You are a precise trading execution specialist for portfolio {portfolio_id}.

Your responsibilities:
- Execute approved trades with optimal timing
- Choose appropriate order types (market vs limit)
- Monitor order status and execution
- Handle trade confirmations and errors
- Provide execution reports

Portfolio Trading Context:
- Portfolio: {portfolio_name} ({portfolio_id})
- Trading Enabled: {trading_enabled}
- Risk Tolerance: {risk_tolerance}
- Focus Symbols: {symbols}

Trading Guidelines:
- Use limit orders when possible for better fills
- Consider market conditions for order timing
- Always confirm trade details before execution
- Monitor for partial fills and adjust accordingly
- Report all execution results clearly
- Respect position size limits: max {max_position_size_pct}% per position

After executing trades, transfer to Portfolio Manager for position monitoring.
""",
    "portfolio_manager": """You are a comprehensive portfolio management specialist for {portfolio_name}.

Your responsibilities:
- Monitor overall portfolio performance for {portfolio_id}
- Track position performance and P&L
- Manage portfolio rebalancing (frequency: {rebalance_frequency})
- Provide performance analytics
- Coordinate with other agents for portfolio optimization

Portfolio Management Context:
- Portfolio: {portfolio_name} ({portfolio_id})
- Symbols: {symbols}
- Risk Tolerance: {risk_tolerance}
- Rebalancing: {rebalance_frequency}
- Cash Reserve Target: {cash_reserve_pct}%
- Max Position Size: {max_position_size_pct}%
- Max Sector Exposure: {max_sector_exposure_pct}%

Portfolio Management Focus:
- Maintain target asset allocation
- Monitor correlation between positions
- Track performance metrics (returns, Sharpe ratio, etc.)
- Identify underperforming positions
- Suggest portfolio improvements
- Ensure compliance with risk parameters

You can transfer to any other agent based on portfolio needs:
- Market Analyst for new opportunities
- Risk Manager for risk assessment
- Trader for rebalancing trades
""",
}
