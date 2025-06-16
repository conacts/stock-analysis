-- Enhanced AI Agents Migration
-- Migration: 008_enhanced_agents.sql
-- Description: Enhance AI agents with profiles, motivations, and advanced configurations

-- Add additional columns to ai_agents table for more sophisticated agent configurations
ALTER TABLE ai_agents 
ADD COLUMN IF NOT EXISTS agent_type VARCHAR(50) DEFAULT 'trading', -- 'trading', 'research', 'risk_management', 'rebalancing'
ADD COLUMN IF NOT EXISTS risk_tolerance VARCHAR(20) DEFAULT 'moderate', -- 'conservative', 'moderate', 'aggressive'
ADD COLUMN IF NOT EXISTS trading_style VARCHAR(30) DEFAULT 'balanced', -- 'conservative', 'balanced', 'growth', 'day_trader', 'swing_trader'
ADD COLUMN IF NOT EXISTS motivations JSONB DEFAULT '[]', -- Array of motivations like ["profit", "risk_management", "diversification"]
ADD COLUMN IF NOT EXISTS constraints JSONB DEFAULT '{}', -- Trading constraints and limits
ADD COLUMN IF NOT EXISTS performance_metrics JSONB DEFAULT '{}', -- Track agent performance over time
ADD COLUMN IF NOT EXISTS learning_enabled BOOLEAN DEFAULT true;

-- Agent performance tracking
CREATE TABLE IF NOT EXISTS agent_performance (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES ai_agents(id),
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    total_return DECIMAL(10,4) DEFAULT 0,
    sharpe_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    win_rate DECIMAL(5,4),
    average_hold_time INTERVAL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(agent_id, portfolio_id, period_start, period_end)
);



-- Create indexes
CREATE INDEX IF NOT EXISTS idx_agent_performance_agent_id ON agent_performance(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_performance_portfolio_id ON agent_performance(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_agent_performance_period ON agent_performance(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_ai_agents_type ON ai_agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_ai_agents_risk_tolerance ON ai_agents(risk_tolerance); 