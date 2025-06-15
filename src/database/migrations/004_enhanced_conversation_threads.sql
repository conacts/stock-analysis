-- Core Portfolio and Agent Management
-- Migration: 004_core_portfolio_and_agents.sql

-- AI Agents table - agent configurations with system prompts
CREATE TABLE IF NOT EXISTS ai_agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    system_prompt TEXT NOT NULL,
    model VARCHAR(50) DEFAULT 'deepseek-chat',
    temperature DECIMAL(3,2) DEFAULT 0.1,
    max_tokens INTEGER DEFAULT 2000,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Portfolios table - basic portfolio information
CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    agent_id INTEGER REFERENCES ai_agents(id),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'archived'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add missing columns to existing portfolios table
ALTER TABLE portfolios 
ADD COLUMN IF NOT EXISTS agent_id INTEGER,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';

-- Add foreign key constraint for agent_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_portfolios_agent_id'
    ) THEN
        ALTER TABLE portfolios 
        ADD CONSTRAINT fk_portfolios_agent_id 
        FOREIGN KEY (agent_id) REFERENCES ai_agents(id);
    END IF;
END $$;

-- Analysis results table - store results from portfolio analysis
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    analysis_type VARCHAR(50) NOT NULL, -- 'market_opening', 'daily_check', 'manual'
    symbol VARCHAR(20),
    analysis_data JSONB,
    recommendations JSONB,
    status VARCHAR(20) DEFAULT 'completed', -- 'pending', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
    FOREIGN KEY (agent_id) REFERENCES ai_agents(id)
);

-- Drop existing indexes if they exist to avoid conflicts
DROP INDEX IF EXISTS idx_portfolios_status;
DROP INDEX IF EXISTS idx_portfolios_agent_id;
DROP INDEX IF EXISTS idx_analysis_results_portfolio_id;
DROP INDEX IF EXISTS idx_analysis_results_created_at;
DROP INDEX IF EXISTS idx_analysis_results_analysis_type;

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_portfolios_status ON portfolios(status);
CREATE INDEX IF NOT EXISTS idx_portfolios_agent_id ON portfolios(agent_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_portfolio_id ON analysis_results(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_type ON analysis_results(analysis_type);

-- Update timestamp triggers
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS portfolios_update_timestamp ON portfolios;
DROP TRIGGER IF EXISTS agents_update_timestamp ON ai_agents;

CREATE TRIGGER portfolios_update_timestamp
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER agents_update_timestamp
    BEFORE UPDATE ON ai_agents
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Insert default AI agent
INSERT INTO ai_agents (id, name, system_prompt, model) VALUES (
    1,
    'Default Trading Agent',
    'You are an expert financial analyst and trading advisor. Analyze market data and provide clear, actionable trading recommendations. Always consider risk management and provide confidence levels for your recommendations.',
    'deepseek-chat'
) ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    system_prompt = EXCLUDED.system_prompt,
    model = EXCLUDED.model;

-- Update existing portfolios to have agent_id and status
UPDATE portfolios 
SET agent_id = 1, status = 'active' 
WHERE agent_id IS NULL OR status IS NULL;
