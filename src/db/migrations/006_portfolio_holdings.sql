-- Portfolio Holdings and Transactions Migration
-- Migration: 006_portfolio_holdings.sql
-- Description: Track portfolio holdings, transactions, and balance history

-- Portfolio holdings - current positions
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15,6) NOT NULL,
    average_cost DECIMAL(15,4) NOT NULL,
    current_price DECIMAL(15,4),
    last_price_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(portfolio_id, symbol)
);

-- Transaction history - all buy/sell transactions
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    symbol VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL, -- 'buy', 'sell'
    quantity DECIMAL(15,6) NOT NULL,
    price DECIMAL(15,4) NOT NULL,
    total_amount DECIMAL(15,4) NOT NULL,
    fees DECIMAL(15,4) DEFAULT 0,
    analysis_result_id INTEGER REFERENCES analysis_results(id), -- Link to the analysis that triggered this
    executed_by_agent BOOLEAN DEFAULT false,
    execution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executed', 'failed', 'cancelled'
    execution_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP
);

-- Portfolio balance history - track cash and total value over time
CREATE TABLE IF NOT EXISTS portfolio_balances (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    cash_balance DECIMAL(15,4) NOT NULL,
    total_holdings_value DECIMAL(15,4) NOT NULL,
    total_portfolio_value DECIMAL(15,4) NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_portfolio_id ON portfolio_holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_symbol ON portfolio_holdings(symbol);
CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_id ON transactions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_portfolio_balances_portfolio_id ON portfolio_balances(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_balances_recorded_at ON portfolio_balances(recorded_at); 