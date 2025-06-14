"""
Database service for Swarm AI Trading System
"""

import json
import logging
import os
from typing import List, Optional

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from ..models.swarm_models import DEFAULT_AGENT_PROMPTS, AgentPrompt, MarketContext, PortfolioConfig, SwarmConversation, TradingDecision

# Load environment variables
load_dotenv(".env.local", override=True)

logger = logging.getLogger(__name__)


class SwarmDatabase:
    """Database service for Swarm AI Trading System"""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection and create tables"""
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Create connection pool for better performance
        self.pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=self.database_url)

        self._create_tables()
        self._initialize_default_prompts()

    def get_connection(self):
        """Get a connection from the pool"""
        return self.pool.getconn()

    def return_connection(self, conn):
        """Return a connection to the pool"""
        self.pool.putconn(conn)

    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Agent prompts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agent_prompts (
                        id SERIAL PRIMARY KEY,
                        agent_name VARCHAR(100) NOT NULL,
                        prompt_version VARCHAR(50) NOT NULL,
                        system_prompt TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(100),
                        description TEXT,
                        UNIQUE(agent_name, prompt_version)
                    )
                """)

                # Portfolio configurations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_configs (
                        id SERIAL PRIMARY KEY,
                        portfolio_id VARCHAR(100) UNIQUE NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        symbols JSONB NOT NULL,
                        risk_tolerance VARCHAR(50) NOT NULL,
                        max_position_size_pct DECIMAL(5,2) DEFAULT 5.0,
                        max_sector_exposure_pct DECIMAL(5,2) DEFAULT 20.0,
                        cash_reserve_pct DECIMAL(5,2) DEFAULT 10.0,
                        trading_enabled BOOLEAN DEFAULT TRUE,
                        rebalance_frequency VARCHAR(50) DEFAULT 'weekly',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)

                # Swarm conversations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS swarm_conversations (
                        id SERIAL PRIMARY KEY,
                        portfolio_id VARCHAR(100) NOT NULL,
                        conversation_id VARCHAR(100) UNIQUE NOT NULL,
                        user_message TEXT NOT NULL,
                        agent_responses JSONB NOT NULL,
                        final_agent VARCHAR(100) NOT NULL,
                        turns_used INTEGER NOT NULL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        conversation_metadata JSONB
                    )
                """)

                # Trading decisions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trading_decisions (
                        id SERIAL PRIMARY KEY,
                        conversation_id VARCHAR(100) NOT NULL,
                        portfolio_id VARCHAR(100) NOT NULL,
                        decision_type VARCHAR(50) NOT NULL,
                        symbol VARCHAR(20),
                        quantity DECIMAL(15,6),
                        price DECIMAL(15,6),
                        reasoning TEXT NOT NULL,
                        confidence_score DECIMAL(3,2),
                        risk_assessment TEXT,
                        executed BOOLEAN DEFAULT FALSE,
                        execution_result JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        executed_at TIMESTAMP
                    )
                """)

                # Market context table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS swarm_market_context (
                        id SERIAL PRIMARY KEY,
                        portfolio_id VARCHAR(100) NOT NULL,
                        context_type VARCHAR(100) NOT NULL,
                        symbol VARCHAR(20),
                        data JSONB NOT NULL,
                        relevance_score DECIMAL(3,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    )
                """)

                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_prompts_active ON agent_prompts(agent_name, is_active)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_configs_active ON portfolio_configs(portfolio_id, is_active)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_portfolio ON swarm_conversations(portfolio_id, created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_portfolio ON trading_decisions(portfolio_id, created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_portfolio ON swarm_market_context(portfolio_id, context_type, created_at)")

                conn.commit()
                logger.info("✅ Swarm database tables created/verified")
        finally:
            self.return_connection(conn)

    def _initialize_default_prompts(self):
        """Initialize default agent prompts if they don't exist"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for agent_name, prompt_text in DEFAULT_AGENT_PROMPTS.items():
                    # Check if default prompt exists
                    cursor.execute("SELECT id FROM agent_prompts WHERE agent_name = %s AND prompt_version = 'default'", (agent_name,))

                    if not cursor.fetchone():
                        cursor.execute(
                            """
                            INSERT INTO agent_prompts
                            (agent_name, prompt_version, system_prompt, description, created_by)
                            VALUES (%s, 'default', %s, 'Default system prompt', 'system')
                        """,
                            (agent_name, prompt_text),
                        )

                conn.commit()
                logger.info("✅ Default agent prompts initialized")
        finally:
            self.return_connection(conn)

    # Agent Prompt Methods
    def get_active_prompt(self, agent_name: str) -> Optional[AgentPrompt]:
        """Get the active system prompt for an agent"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT * FROM agent_prompts
                    WHERE agent_name = %s AND is_active = TRUE
                    ORDER BY created_at DESC LIMIT 1
                """,
                    (agent_name,),
                )

                row = cursor.fetchone()
                if row:
                    return AgentPrompt(**dict(row))
                return None
        finally:
            self.return_connection(conn)

    def save_prompt(self, prompt: AgentPrompt) -> int:
        """Save a new agent prompt version"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Deactivate previous prompts for this agent
                cursor.execute(
                    """
                    UPDATE agent_prompts SET is_active = FALSE
                    WHERE agent_name = %s
                """,
                    (prompt.agent_name,),
                )

                # Insert new prompt
                cursor.execute(
                    """
                    INSERT INTO agent_prompts
                    (agent_name, prompt_version, system_prompt, is_active, created_by, description)
                    VALUES (%s, %s, %s, TRUE, %s, %s)
                    RETURNING id
                """,
                    (prompt.agent_name, prompt.prompt_version, prompt.system_prompt, prompt.created_by, prompt.description),
                )

                prompt_id = cursor.fetchone()[0]
                conn.commit()

                logger.info(f"✅ Saved new prompt for {prompt.agent_name} v{prompt.prompt_version}")
                return prompt_id
        finally:
            self.return_connection(conn)

    # Portfolio Configuration Methods
    def get_portfolio_config(self, portfolio_id: str) -> Optional[PortfolioConfig]:
        """Get portfolio configuration"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT * FROM portfolio_configs
                    WHERE portfolio_id = %s AND is_active = TRUE
                """,
                    (portfolio_id,),
                )

                row = cursor.fetchone()
                if row:
                    config_dict = dict(row)
                    # symbols is already JSONB, no need to parse
                    return PortfolioConfig(**config_dict)
                return None
        finally:
            self.return_connection(conn)

    def save_portfolio_config(self, config: PortfolioConfig) -> int:
        """Save or update portfolio configuration"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Check if config exists
                existing = self.get_portfolio_config(config.portfolio_id)

                if existing:
                    # Update existing
                    cursor.execute(
                        """
                        UPDATE portfolio_configs SET
                        name = %s, symbols = %s, risk_tolerance = %s,
                        max_position_size_pct = %s, max_sector_exposure_pct = %s,
                        cash_reserve_pct = %s, trading_enabled = %s,
                        rebalance_frequency = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE portfolio_id = %s
                    """,
                        (config.name, json.dumps(config.symbols), config.risk_tolerance, config.max_position_size_pct, config.max_sector_exposure_pct, config.cash_reserve_pct, config.trading_enabled, config.rebalance_frequency, config.portfolio_id),
                    )
                    config_id = existing.id
                else:
                    # Insert new
                    cursor.execute(
                        """
                        INSERT INTO portfolio_configs
                        (portfolio_id, name, symbols, risk_tolerance, max_position_size_pct,
                         max_sector_exposure_pct, cash_reserve_pct, trading_enabled, rebalance_frequency)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """,
                        (config.portfolio_id, config.name, json.dumps(config.symbols), config.risk_tolerance, config.max_position_size_pct, config.max_sector_exposure_pct, config.cash_reserve_pct, config.trading_enabled, config.rebalance_frequency),
                    )
                    config_id = cursor.fetchone()[0]

                conn.commit()
                logger.info(f"✅ Saved portfolio config for {config.portfolio_id}")
                return config_id
        finally:
            self.return_connection(conn)

    def get_default_portfolio_config(self, portfolio_id: str) -> PortfolioConfig:
        """Get default portfolio configuration if none exists"""
        return PortfolioConfig(
            portfolio_id=portfolio_id,
            name=f"Portfolio {portfolio_id}",
            symbols=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"],  # Default tech stocks
            risk_tolerance="moderate",
            max_position_size_pct=5.0,
            max_sector_exposure_pct=20.0,
            cash_reserve_pct=10.0,
            trading_enabled=True,
            rebalance_frequency="weekly",
        )

    # Conversation Methods
    def save_conversation(self, conversation: SwarmConversation) -> int:
        """Save conversation history"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO swarm_conversations
                    (portfolio_id, conversation_id, user_message, agent_responses,
                     final_agent, turns_used, success, error_message, conversation_metadata, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """,
                    (conversation.portfolio_id, conversation.conversation_id, conversation.user_message, json.dumps(conversation.agent_responses), conversation.final_agent, conversation.turns_used, conversation.success, conversation.error_message, json.dumps(conversation.metadata) if conversation.metadata else None),
                )

                conv_id = cursor.fetchone()[0]
                conn.commit()
                return conv_id
        finally:
            self.return_connection(conn)

    def get_conversation_history(self, portfolio_id: str, limit: int = 10) -> List[SwarmConversation]:
        """Get recent conversation history for a portfolio"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT * FROM swarm_conversations
                    WHERE portfolio_id = %s
                    ORDER BY created_at DESC LIMIT %s
                """,
                    (portfolio_id, limit),
                )

                conversations = []
                for row in cursor.fetchall():
                    conv_dict = dict(row)
                    conv_dict["agent_responses"] = conv_dict["agent_responses"]  # Already parsed by JSONB
                    if conv_dict["conversation_metadata"]:
                        conv_dict["metadata"] = conv_dict["conversation_metadata"]  # Map back to expected field name
                    conversations.append(SwarmConversation(**conv_dict))

                return conversations
        finally:
            self.return_connection(conn)

    # Trading Decision Methods
    def save_trading_decision(self, decision: TradingDecision) -> int:
        """Save a trading decision"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO trading_decisions
                    (conversation_id, portfolio_id, decision_type, symbol, quantity,
                     price, reasoning, confidence_score, risk_assessment, executed, execution_result, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """,
                    (decision.conversation_id, decision.portfolio_id, decision.decision_type, decision.symbol, decision.quantity, decision.price, decision.reasoning, decision.confidence_score, decision.risk_assessment, decision.executed, json.dumps(decision.execution_result) if decision.execution_result else None),
                )

                decision_id = cursor.fetchone()[0]
                conn.commit()
                return decision_id
        finally:
            self.return_connection(conn)

    # Market Context Methods
    def save_market_context(self, context: MarketContext) -> int:
        """Save market context data"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO swarm_market_context
                    (portfolio_id, context_type, symbol, data, relevance_score, expires_at, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """,
                    (context.portfolio_id, context.context_type, context.symbol, json.dumps(context.data), context.relevance_score, context.expires_at),
                )

                context_id = cursor.fetchone()[0]
                conn.commit()
                return context_id
        finally:
            self.return_connection(conn)

    def get_relevant_context(self, portfolio_id: str, context_type: Optional[str] = None) -> List[MarketContext]:
        """Get relevant market context for a portfolio"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if context_type:
                    cursor.execute(
                        """
                        SELECT * FROM swarm_market_context
                        WHERE portfolio_id = %s AND context_type = %s
                        AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                        ORDER BY relevance_score DESC, created_at DESC
                        LIMIT 10
                    """,
                        (portfolio_id, context_type),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT * FROM swarm_market_context
                        WHERE portfolio_id = %s
                        AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                        ORDER BY relevance_score DESC, created_at DESC
                        LIMIT 20
                    """,
                        (portfolio_id,),
                    )

                contexts = []
                for row in cursor.fetchall():
                    context_dict = dict(row)
                    context_dict["data"] = context_dict["data"]  # Already parsed by JSONB
                    contexts.append(MarketContext(**context_dict))

                return contexts
        finally:
            self.return_connection(conn)

    def close(self):
        """Close database connection pool"""
        if self.pool:
            self.pool.closeall()


# Global database instance
_db_instance = None


def get_swarm_db() -> SwarmDatabase:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SwarmDatabase()
    return _db_instance
