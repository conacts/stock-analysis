-- Enhanced Conversation Threading for Portfolio-Specific Context
-- Migration: 004_enhanced_conversation_threads.sql

-- Create enhanced conversation threads table
CREATE TABLE IF NOT EXISTS portfolio_conversation_threads (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(50) NOT NULL,
    thread_id VARCHAR(100) NOT NULL,
    conversation_type VARCHAR(50) NOT NULL, -- 'daily_analysis', 'trading_decision', 'risk_check', 'market_event'
    user_message TEXT,
    ai_responses JSONB,
    market_context JSONB,
    portfolio_state JSONB,
    actions_taken JSONB,
    trigger_source VARCHAR(50), -- 'scheduled', 'manual', 'market_event'
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_portfolio_conversations_portfolio_id ON portfolio_conversation_threads(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_conversations_created_at ON portfolio_conversation_threads(created_at);
CREATE INDEX IF NOT EXISTS idx_portfolio_conversations_thread_id ON portfolio_conversation_threads(thread_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_conversations_type ON portfolio_conversation_threads(conversation_type);
CREATE INDEX IF NOT EXISTS idx_portfolio_conversations_portfolio_date ON portfolio_conversation_threads(portfolio_id, created_at);

-- Create portfolio configuration table for trigger settings
CREATE TABLE IF NOT EXISTS portfolio_trigger_configs (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(50) NOT NULL UNIQUE,
    automation_level VARCHAR(20) DEFAULT 'monitor_only', -- 'monitor_only', 'suggest_only', 'auto_execute'
    risk_tolerance VARCHAR(20) DEFAULT 'moderate', -- 'conservative', 'moderate', 'aggressive'
    max_position_size DECIMAL(5,4) DEFAULT 0.10, -- 10% max position size
    daily_loss_limit DECIMAL(5,4) DEFAULT 0.02, -- 2% daily loss limit
    trading_hours JSONB, -- Custom trading hours
    preferred_sectors JSONB, -- Array of preferred sectors
    blacklisted_symbols JSONB, -- Array of blacklisted symbols
    rebalancing_frequency VARCHAR(20) DEFAULT 'weekly', -- 'daily', 'weekly', 'monthly'
    notification_settings JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create market context storage table
CREATE TABLE IF NOT EXISTS market_context_history (
    id SERIAL PRIMARY KEY,
    market_regime VARCHAR(20), -- 'bull', 'bear', 'sideways'
    volatility_level VARCHAR(20), -- 'low', 'medium', 'high'
    recent_events JSONB,
    sector_performance JSONB,
    economic_indicators JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for market context
CREATE INDEX IF NOT EXISTS idx_market_context_created_at ON market_context_history(created_at);

-- Create portfolio performance tracking table
CREATE TABLE IF NOT EXISTS portfolio_performance_tracking (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    total_value DECIMAL(15,2),
    daily_return DECIMAL(8,6),
    positions JSONB,
    risk_metrics JSONB,
    allocation JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(portfolio_id, date)
);

-- Create indexes for performance tracking
CREATE INDEX IF NOT EXISTS idx_portfolio_performance_portfolio_id ON portfolio_performance_tracking(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_performance_date ON portfolio_performance_tracking(date);
CREATE INDEX IF NOT EXISTS idx_portfolio_performance_portfolio_date ON portfolio_performance_tracking(portfolio_id, date);

-- Create trading decisions tracking table
CREATE TABLE IF NOT EXISTS trading_decisions_tracking (
    id SERIAL PRIMARY KEY,
    decision_id VARCHAR(100) NOT NULL UNIQUE,
    portfolio_id VARCHAR(50) NOT NULL,
    conversation_thread_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL, -- 'buy', 'sell', 'hold'
    quantity DECIMAL(15,6),
    price DECIMAL(15,4),
    reasoning TEXT,
    confidence DECIMAL(3,2), -- 0.00 to 1.00
    executed BOOLEAN DEFAULT FALSE,
    execution_price DECIMAL(15,4),
    execution_time TIMESTAMP,
    outcome VARCHAR(20), -- 'success', 'failure', 'pending', 'cancelled'
    performance_impact DECIMAL(8,6), -- Impact on portfolio performance
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for trading decisions
CREATE INDEX IF NOT EXISTS idx_trading_decisions_portfolio_id ON trading_decisions_tracking(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_symbol ON trading_decisions_tracking(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_created_at ON trading_decisions_tracking(created_at);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_executed ON trading_decisions_tracking(executed);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_thread_id ON trading_decisions_tracking(conversation_thread_id);

-- Create trigger automation logs table
CREATE TABLE IF NOT EXISTS trigger_automation_logs (
    id SERIAL PRIMARY KEY,
    trigger_id VARCHAR(100) NOT NULL,
    portfolio_id VARCHAR(50),
    trigger_type VARCHAR(50) NOT NULL, -- 'daily_analysis', 'risk_monitor', 'market_event'
    trigger_source VARCHAR(50), -- 'scheduled', 'manual', 'event_driven'
    status VARCHAR(20) NOT NULL, -- 'started', 'completed', 'failed', 'cancelled'
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    conversation_thread_id VARCHAR(100),
    actions_executed INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for automation logs
CREATE INDEX IF NOT EXISTS idx_trigger_logs_trigger_id ON trigger_automation_logs(trigger_id);
CREATE INDEX IF NOT EXISTS idx_trigger_logs_portfolio_id ON trigger_automation_logs(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_trigger_logs_type ON trigger_automation_logs(trigger_type);
CREATE INDEX IF NOT EXISTS idx_trigger_logs_status ON trigger_automation_logs(status);
CREATE INDEX IF NOT EXISTS idx_trigger_logs_created_at ON trigger_automation_logs(created_at);

-- Create conversation context summary view
CREATE OR REPLACE VIEW portfolio_conversation_summary AS
SELECT
    portfolio_id,
    COUNT(*) as total_conversations,
    COUNT(DISTINCT DATE(created_at)) as active_days,
    MAX(created_at) as last_conversation,
    COUNT(CASE WHEN conversation_type = 'daily_analysis' THEN 1 END) as daily_analyses,
    COUNT(CASE WHEN conversation_type = 'trading_decision' THEN 1 END) as trading_decisions,
    COUNT(CASE WHEN conversation_type = 'risk_check' THEN 1 END) as risk_checks,
    COUNT(CASE WHEN conversation_type = 'market_event' THEN 1 END) as market_events,
    COUNT(CASE WHEN actions_taken IS NOT NULL AND actions_taken != '[]' THEN 1 END) as conversations_with_actions
FROM portfolio_conversation_threads
GROUP BY portfolio_id;

-- Create portfolio performance summary view
CREATE OR REPLACE VIEW portfolio_performance_summary AS
SELECT
    p.portfolio_id,
    p.total_value as current_value,
    p.daily_return as current_daily_return,
    LAG(p.total_value, 7) OVER (PARTITION BY p.portfolio_id ORDER BY p.date) as value_7_days_ago,
    LAG(p.total_value, 30) OVER (PARTITION BY p.portfolio_id ORDER BY p.date) as value_30_days_ago,
    COUNT(t.id) as total_decisions,
    COUNT(CASE WHEN t.executed = TRUE THEN 1 END) as executed_decisions,
    COUNT(CASE WHEN t.outcome = 'success' THEN 1 END) as successful_decisions,
    AVG(CASE WHEN t.executed = TRUE THEN t.confidence END) as avg_confidence,
    SUM(CASE WHEN t.executed = TRUE THEN t.performance_impact END) as total_performance_impact
FROM portfolio_performance_tracking p
LEFT JOIN trading_decisions_tracking t ON p.portfolio_id = t.portfolio_id
    AND t.created_at >= p.date - INTERVAL '1 day'
    AND t.created_at < p.date + INTERVAL '1 day'
WHERE p.date = (SELECT MAX(date) FROM portfolio_performance_tracking WHERE portfolio_id = p.portfolio_id)
GROUP BY p.portfolio_id, p.total_value, p.daily_return;

-- Create function to update conversation thread timestamps
CREATE OR REPLACE FUNCTION update_conversation_thread_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
DROP TRIGGER IF EXISTS trigger_update_conversation_thread_timestamp ON portfolio_conversation_threads;
CREATE TRIGGER trigger_update_conversation_thread_timestamp
    BEFORE UPDATE ON portfolio_conversation_threads
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_thread_timestamp();

-- Create function to update portfolio config timestamps
CREATE OR REPLACE FUNCTION update_portfolio_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for portfolio config updates
DROP TRIGGER IF EXISTS trigger_update_portfolio_config_timestamp ON portfolio_trigger_configs;
CREATE TRIGGER trigger_update_portfolio_config_timestamp
    BEFORE UPDATE ON portfolio_trigger_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolio_config_timestamp();

-- Create function to update trading decisions timestamps
CREATE OR REPLACE FUNCTION update_trading_decision_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for trading decisions updates
DROP TRIGGER IF EXISTS trigger_update_trading_decision_timestamp ON trading_decisions_tracking;
CREATE TRIGGER trigger_update_trading_decision_timestamp
    BEFORE UPDATE ON trading_decisions_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_trading_decision_timestamp();

-- Insert default portfolio configurations for existing portfolios
INSERT INTO portfolio_trigger_configs (portfolio_id, automation_level, risk_tolerance)
SELECT DISTINCT 'portfolio_' || id::text, 'monitor_only', 'moderate'
FROM (SELECT 1 as id UNION SELECT 2 UNION SELECT 3) as default_portfolios
ON CONFLICT (portfolio_id) DO NOTHING;

-- Insert sample market context
INSERT INTO market_context_history (market_regime, volatility_level, recent_events, sector_performance, economic_indicators)
VALUES (
    'sideways',
    'medium',
    '[]'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
);

COMMENT ON TABLE portfolio_conversation_threads IS 'Enhanced conversation threading for portfolio-specific AI interactions';
COMMENT ON TABLE portfolio_trigger_configs IS 'Configuration settings for portfolio-specific trigger automation';
COMMENT ON TABLE market_context_history IS 'Historical market context data for AI decision making';
COMMENT ON TABLE portfolio_performance_tracking IS 'Daily portfolio performance tracking for context';
COMMENT ON TABLE trading_decisions_tracking IS 'Detailed tracking of AI trading decisions and outcomes';
COMMENT ON TABLE trigger_automation_logs IS 'Comprehensive logging of trigger automation execution';
