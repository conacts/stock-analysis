-- Database Functions and Triggers Migration
-- Migration: 004_database_functions.sql
-- Description: Utility functions and triggers for timestamp management

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist to avoid conflicts
DROP TRIGGER IF EXISTS portfolios_update_timestamp ON portfolios;
DROP TRIGGER IF EXISTS agents_update_timestamp ON ai_agents;

-- Create timestamp update triggers
CREATE TRIGGER portfolios_update_timestamp
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER agents_update_timestamp
    BEFORE UPDATE ON ai_agents
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp(); 