-- Analysis Results Migration
-- Migration: 003_analysis_results.sql
-- Description: Store analysis results from portfolio and stock analysis

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

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_analysis_results_portfolio_id ON analysis_results(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_type ON analysis_results(analysis_type); 