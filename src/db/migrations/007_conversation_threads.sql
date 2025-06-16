-- Conversation Threads Migration
-- Migration: 007_conversation_threads.sql
-- Description: Track conversation threads and action chains for portfolio management

-- Conversation threads - track chains of analysis and actions
CREATE TABLE IF NOT EXISTS conversation_threads (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    agent_id INTEGER NOT NULL REFERENCES ai_agents(id),
    thread_type VARCHAR(50) NOT NULL, -- 'analysis', 'trading', 'rebalancing', 'risk_management'
    title VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'failed', 'cancelled'
    parent_thread_id INTEGER REFERENCES conversation_threads(id), -- For nested/sub-threads
    trigger_execution_id INTEGER REFERENCES trigger_executions(id), -- What triggered this thread
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Thread messages - individual messages in a conversation thread
CREATE TABLE IF NOT EXISTS thread_messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER NOT NULL REFERENCES conversation_threads(id),
    message_type VARCHAR(20) NOT NULL, -- 'user_input', 'agent_response', 'system_action', 'function_call'
    content TEXT NOT NULL,
    metadata JSONB, -- Store function call results, confidence scores, etc.
    analysis_result_id INTEGER REFERENCES analysis_results(id),
    transaction_id INTEGER REFERENCES transactions(id),
    sequence_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Function calls - track AI agent function calls and their results
CREATE TABLE IF NOT EXISTS agent_function_calls (
    id SERIAL PRIMARY KEY,
    thread_message_id INTEGER NOT NULL REFERENCES thread_messages(id),
    function_name VARCHAR(100) NOT NULL,
    parameters JSONB NOT NULL,
    result JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_conversation_threads_portfolio_id ON conversation_threads(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_conversation_threads_agent_id ON conversation_threads(agent_id);
CREATE INDEX IF NOT EXISTS idx_conversation_threads_status ON conversation_threads(status);
CREATE INDEX IF NOT EXISTS idx_thread_messages_thread_id ON thread_messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_messages_sequence ON thread_messages(thread_id, sequence_order);
CREATE INDEX IF NOT EXISTS idx_agent_function_calls_thread_message_id ON agent_function_calls(thread_message_id);
CREATE INDEX IF NOT EXISTS idx_agent_function_calls_status ON agent_function_calls(status); 