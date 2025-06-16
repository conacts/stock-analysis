-- Triggers and Events Migration
-- Migration: 005_triggers_and_events.sql
-- Description: System triggers that initiate market analysis and data collection

-- Market triggers table - defines what events trigger analysis
CREATE TABLE IF NOT EXISTS market_triggers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL, -- 'time_based', 'price_change', 'volume_spike', 'news_event', 'manual'
    trigger_config JSONB NOT NULL, -- Configuration for the trigger (schedule, thresholds, etc.)
    target_type VARCHAR(20) NOT NULL, -- 'portfolio', 'symbol', 'watchlist'
    target_id INTEGER, -- ID of the target (portfolio_id, symbol_id, etc.)
    agent_id INTEGER NOT NULL REFERENCES ai_agents(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trigger execution log - track when triggers fire
CREATE TABLE IF NOT EXISTS trigger_executions (
    id SERIAL PRIMARY KEY,
    trigger_id INTEGER NOT NULL REFERENCES market_triggers(id),
    execution_time TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    result_data JSONB,
    error_message TEXT,
    analysis_result_id INTEGER REFERENCES analysis_results(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_market_triggers_type ON market_triggers(trigger_type);
CREATE INDEX IF NOT EXISTS idx_market_triggers_active ON market_triggers(is_active);
CREATE INDEX IF NOT EXISTS idx_trigger_executions_trigger_id ON trigger_executions(trigger_id);
CREATE INDEX IF NOT EXISTS idx_trigger_executions_status ON trigger_executions(status);
CREATE INDEX IF NOT EXISTS idx_trigger_executions_time ON trigger_executions(execution_time); 