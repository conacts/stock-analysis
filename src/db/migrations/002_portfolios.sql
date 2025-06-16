-- Portfolios Migration
-- Migration: 002_portfolios.sql
-- Description: Portfolio management with agent assignments and status tracking

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

-- Add missing columns to existing portfolios table (for existing installations)
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

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_portfolios_status ON portfolios(status);
CREATE INDEX IF NOT EXISTS idx_portfolios_agent_id ON portfolios(agent_id);

 