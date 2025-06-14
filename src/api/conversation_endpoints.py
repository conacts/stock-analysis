"""
Enhanced Conversation History Endpoints for Portfolio-Specific Context

These endpoints provide sophisticated conversation threading and context management
for portfolio-specific AI interactions and trigger automation.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel

from src.database.db_manager import DatabaseManager


class ConversationMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None
    agent: Optional[str] = None  # Which AI agent generated this


class TradingDecision(BaseModel):
    decision_id: str
    symbol: str
    action: str  # "buy", "sell", "hold"
    quantity: Optional[float] = None
    price: Optional[float] = None
    reasoning: str
    confidence: float
    timestamp: str
    executed: bool = False
    outcome: Optional[str] = None  # "success", "failure", "pending"


class MarketContext(BaseModel):
    market_regime: str  # "bull", "bear", "sideways"
    volatility_level: str  # "low", "medium", "high"
    recent_events: List[Dict[str, Any]]
    sector_performance: Dict[str, float]
    economic_indicators: Dict[str, Any]
    last_updated: str


class PortfolioState(BaseModel):
    total_value: float
    daily_return: float
    positions: List[Dict[str, Any]]
    risk_metrics: Dict[str, float]
    allocation: Dict[str, float]
    last_updated: str


class PortfolioConversationContext(BaseModel):
    portfolio_id: str
    conversation_thread_id: str
    last_analysis_date: str
    conversation_history: List[ConversationMessage]
    trading_decisions: List[TradingDecision]
    market_context: MarketContext
    portfolio_state: PortfolioState
    context_summary: str
    total_conversations: int
    performance_since_start: float


class ConversationThread(BaseModel):
    thread_id: str
    conversation_type: str  # "daily_analysis", "trading_decision", "risk_check", "market_event"
    user_message: str
    ai_responses: List[ConversationMessage]
    market_context: Optional[MarketContext] = None
    portfolio_state: Optional[PortfolioState] = None
    actions_taken: List[TradingDecision] = []
    trigger_source: Optional[str] = None  # "scheduled", "manual", "market_event"
    metadata: Dict[str, Any] = {}


class ConversationContextRequest(BaseModel):
    days_back: int = 7
    include_market_context: bool = True
    include_trading_decisions: bool = True
    include_portfolio_state: bool = True
    conversation_types: Optional[List[str]] = None  # Filter by conversation types


class ConversationSummaryRequest(BaseModel):
    days_back: int = 30
    summary_type: str = "performance"  # "performance", "decisions", "risk", "full"


async def get_conversation_context(portfolio_id: str, request: ConversationContextRequest, token: str) -> PortfolioConversationContext:
    """Get comprehensive conversation context for portfolio"""
    try:
        db = DatabaseManager()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days_back)

        # Get conversation history
        conversation_history = await _get_conversation_history(db, portfolio_id, start_date, end_date, request.conversation_types)

        # Get trading decisions
        trading_decisions = []
        if request.include_trading_decisions:
            trading_decisions = await _get_trading_decisions(db, portfolio_id, start_date, end_date)

        # Get market context
        market_context = None
        if request.include_market_context:
            market_context = await _get_market_context(db)

        # Get portfolio state
        portfolio_state = None
        if request.include_portfolio_state:
            portfolio_state = await _get_portfolio_state(db, portfolio_id)

        # Generate context summary
        context_summary = await _generate_context_summary(conversation_history, trading_decisions, market_context)

        # Calculate performance metrics
        performance_since_start = await _calculate_performance_since_start(db, portfolio_id, start_date)

        # Generate unique thread ID for this context session
        thread_id = f"ctx_{portfolio_id}_{int(datetime.now().timestamp())}"

        return PortfolioConversationContext(
            portfolio_id=portfolio_id,
            conversation_thread_id=thread_id,
            last_analysis_date=end_date.isoformat(),
            conversation_history=conversation_history,
            trading_decisions=trading_decisions,
            market_context=market_context or _default_market_context(),
            portfolio_state=portfolio_state or _default_portfolio_state(),
            context_summary=context_summary,
            total_conversations=len(conversation_history),
            performance_since_start=performance_since_start,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation context: {str(e)}")


async def get_conversation_summary(portfolio_id: str, request: ConversationSummaryRequest, token: str) -> Dict[str, Any]:
    """Get summarized conversation insights for portfolio"""
    try:
        db = DatabaseManager()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days_back)

        if request.summary_type == "performance":
            return await _generate_performance_summary(db, portfolio_id, start_date, end_date)
        elif request.summary_type == "decisions":
            return await _generate_decisions_summary(db, portfolio_id, start_date, end_date)
        elif request.summary_type == "risk":
            return await _generate_risk_summary(db, portfolio_id, start_date, end_date)
        elif request.summary_type == "full":
            return await _generate_full_summary(db, portfolio_id, start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail="Invalid summary type")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate conversation summary: {str(e)}")


async def store_conversation_thread(portfolio_id: str, conversation: ConversationThread, token: str) -> Dict[str, Any]:
    """Store conversation with portfolio-specific threading"""
    try:
        db = DatabaseManager()

        # Generate thread ID if not provided
        if not conversation.thread_id:
            conversation.thread_id = str(uuid.uuid4())

        # Store in database
        query = """
        INSERT INTO portfolio_conversation_threads (
            portfolio_id, thread_id, conversation_type, user_message,
            ai_responses, market_context, portfolio_state, actions_taken,
            trigger_source, metadata, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        values = (
            portfolio_id,
            conversation.thread_id,
            conversation.conversation_type,
            conversation.user_message,
            json.dumps([msg.dict() for msg in conversation.ai_responses]),
            json.dumps(conversation.market_context.dict() if conversation.market_context else None),
            json.dumps(conversation.portfolio_state.dict() if conversation.portfolio_state else None),
            json.dumps([action.dict() for action in conversation.actions_taken]),
            conversation.trigger_source,
            json.dumps(conversation.metadata),
            datetime.now(),
        )

        result = db.execute_query(query, values)
        conversation_id = result[0][0] if result else None

        return {"success": True, "conversation_id": conversation_id, "thread_id": conversation.thread_id, "portfolio_id": portfolio_id, "stored_at": datetime.now().isoformat()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store conversation thread: {str(e)}")


# Helper functions


async def _get_conversation_history(db: DatabaseManager, portfolio_id: str, start_date: datetime, end_date: datetime, conversation_types: Optional[List[str]] = None) -> List[ConversationMessage]:
    """Retrieve conversation history from database"""

    if conversation_types:
        type_placeholders = ",".join(["%s"] * len(conversation_types))
        query = f"""
        SELECT ai_responses, created_at, conversation_type
        FROM portfolio_conversation_threads
        WHERE portfolio_id = %s
        AND created_at BETWEEN %s AND %s
        AND conversation_type IN ({type_placeholders})
        ORDER BY created_at ASC
        """  # nosec B608 - Using parameterized queries, safe from SQL injection
        params = [portfolio_id, start_date, end_date] + conversation_types
    else:
        query = """
        SELECT ai_responses, created_at, conversation_type
        FROM portfolio_conversation_threads
        WHERE portfolio_id = %s
        AND created_at BETWEEN %s AND %s
        ORDER BY created_at ASC
        """
        params = [portfolio_id, start_date, end_date]

    results = db.execute_query(query, params)

    conversations = []
    for row in results:
        ai_responses_json, created_at, conv_type = row
        if ai_responses_json:
            ai_responses = json.loads(ai_responses_json)
            for response in ai_responses:
                conversations.append(ConversationMessage(role=response.get("role", "assistant"), content=response.get("content", ""), timestamp=created_at.isoformat(), agent=response.get("agent")))

    return conversations


async def _get_trading_decisions(db: DatabaseManager, portfolio_id: str, start_date: datetime, end_date: datetime) -> List[TradingDecision]:
    """Retrieve trading decisions from conversation threads"""

    query = """
    SELECT actions_taken, created_at
    FROM portfolio_conversation_threads
    WHERE portfolio_id = %s
    AND created_at BETWEEN %s AND %s
    AND actions_taken IS NOT NULL
    ORDER BY created_at ASC
    """

    results = db.execute_query(query, [portfolio_id, start_date, end_date])

    decisions = []
    for row in results:
        actions_json, created_at = row
        if actions_json:
            actions = json.loads(actions_json)
            for action in actions:
                decisions.append(
                    TradingDecision(
                        decision_id=action.get("decision_id", str(uuid.uuid4())),
                        symbol=action.get("symbol", ""),
                        action=action.get("action", "hold"),
                        quantity=action.get("quantity"),
                        price=action.get("price"),
                        reasoning=action.get("reasoning", ""),
                        confidence=action.get("confidence", 0.5),
                        timestamp=action.get("timestamp", created_at.isoformat()),
                        executed=action.get("executed", False),
                        outcome=action.get("outcome"),
                    )
                )

    return decisions


async def _get_market_context(db: DatabaseManager) -> MarketContext:
    """Get current market context"""
    # This would integrate with market data APIs
    # For now, return a default context
    return MarketContext(market_regime="sideways", volatility_level="medium", recent_events=[], sector_performance={}, economic_indicators={}, last_updated=datetime.now().isoformat())


async def _get_portfolio_state(db: DatabaseManager, portfolio_id: str) -> PortfolioState:
    """Get current portfolio state"""
    # This would integrate with portfolio data
    # For now, return a default state
    return PortfolioState(total_value=100000.0, daily_return=0.01, positions=[], risk_metrics={}, allocation={}, last_updated=datetime.now().isoformat())


async def _generate_context_summary(conversations: List[ConversationMessage], decisions: List[TradingDecision], market_context: Optional[MarketContext]) -> str:
    """Generate a summary of the conversation context"""

    summary_parts = []

    if conversations:
        summary_parts.append(f"Recent conversations: {len(conversations)} messages")

    if decisions:
        executed_decisions = [d for d in decisions if d.executed]
        summary_parts.append(f"Trading decisions: {len(decisions)} total, {len(executed_decisions)} executed")

    if market_context:
        summary_parts.append(f"Market regime: {market_context.market_regime}")
        summary_parts.append(f"Volatility: {market_context.volatility_level}")

    return "; ".join(summary_parts) if summary_parts else "No recent activity"


async def _calculate_performance_since_start(db: DatabaseManager, portfolio_id: str, start_date: datetime) -> float:
    """Calculate portfolio performance since start date"""
    # This would calculate actual performance
    # For now, return a placeholder
    return 0.05  # 5% return


def _default_market_context() -> MarketContext:
    """Default market context when none available"""
    return MarketContext(market_regime="unknown", volatility_level="medium", recent_events=[], sector_performance={}, economic_indicators={}, last_updated=datetime.now().isoformat())


def _default_portfolio_state() -> PortfolioState:
    """Default portfolio state when none available"""
    return PortfolioState(total_value=0.0, daily_return=0.0, positions=[], risk_metrics={}, allocation={}, last_updated=datetime.now().isoformat())


# Summary generation functions


async def _generate_performance_summary(db: DatabaseManager, portfolio_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate performance-focused summary"""
    return {"summary_type": "performance", "portfolio_id": portfolio_id, "period": f"{start_date.date()} to {end_date.date()}", "total_return": 0.05, "best_decisions": [], "worst_decisions": [], "ai_accuracy": 0.75, "generated_at": datetime.now().isoformat()}


async def _generate_decisions_summary(db: DatabaseManager, portfolio_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate decisions-focused summary"""
    return {"summary_type": "decisions", "portfolio_id": portfolio_id, "period": f"{start_date.date()} to {end_date.date()}", "total_decisions": 0, "executed_decisions": 0, "successful_decisions": 0, "decision_accuracy": 0.0, "generated_at": datetime.now().isoformat()}


async def _generate_risk_summary(db: DatabaseManager, portfolio_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate risk-focused summary"""
    return {"summary_type": "risk", "portfolio_id": portfolio_id, "period": f"{start_date.date()} to {end_date.date()}", "risk_events": 0, "risk_actions_taken": 0, "max_drawdown": 0.0, "risk_score": 0.5, "generated_at": datetime.now().isoformat()}


async def _generate_full_summary(db: DatabaseManager, portfolio_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate comprehensive summary"""
    performance = await _generate_performance_summary(db, portfolio_id, start_date, end_date)
    decisions = await _generate_decisions_summary(db, portfolio_id, start_date, end_date)
    risk = await _generate_risk_summary(db, portfolio_id, start_date, end_date)

    return {"summary_type": "full", "portfolio_id": portfolio_id, "period": f"{start_date.date()} to {end_date.date()}", "performance": performance, "decisions": decisions, "risk": risk, "generated_at": datetime.now().isoformat()}
