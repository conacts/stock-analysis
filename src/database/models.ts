import { z } from 'zod';

// ============================================================================
// CORE TRADING MODELS
// ============================================================================

export const DailyAnalysisSchema = z.object({
	id: z.number().optional(),
	date: z.string(), // ISO date string
	symbol: z.string().max(10),
	analysis_data: z.record(z.any()), // JSONB equivalent
	composite_score: z.number().optional(),
	rating: z.string().max(20).optional(),
	confidence: z.string().max(20).optional(),
	created_at: z.string().optional(), // ISO datetime string
});

export const DailyDecisionSchema = z.object({
	id: z.number().optional(),
	date: z.string(), // ISO date string
	decision_type: z.string().max(50),
	reasoning: z.string(),
	selected_stocks: z.record(z.any()).optional(),
	market_context: z.record(z.any()).optional(),
	created_at: z.string().optional(),
});

export const PerformanceTrackingSchema = z.object({
	id: z.number().optional(),
	symbol: z.string().max(10),
	recommendation_date: z.string(),
	entry_price: z.number().optional(),
	current_price: z.number().optional(),
	target_price: z.number().optional(),
	rating: z.string().max(20).optional(),
	days_held: z.number().optional(),
	return_pct: z.number().optional(),
	status: z.string().max(20).optional(), // active, closed
	updated_at: z.string().optional(),
});

export const MarketContextSchema = z.object({
	id: z.number().optional(),
	date: z.string(),
	market_sentiment: z.string().max(50).optional(),
	vix_level: z.number().optional(),
	sector_rotation: z.record(z.any()).optional(),
	economic_indicators: z.record(z.any()).optional(),
	news_themes: z.record(z.any()).optional(),
	created_at: z.string().optional(),
});

// ============================================================================
// PORTFOLIO MODELS
// ============================================================================

export const PortfolioSchema = z.object({
	id: z.number().optional(),
	name: z.string(),
	description: z.string().optional(),
	portfolio_type: z.string().default('personal'), // personal, ira, 401k, etc.
	base_currency: z.string().default('USD'),
	created_at: z.string().optional(),
	updated_at: z.string().optional(),
	is_active: z.boolean().default(true),
});

export const PortfolioPositionSchema = z.object({
	id: z.number().optional(),
	portfolio_id: z.number(),
	symbol: z.string(),
	quantity: z.number(),
	average_cost: z.number(),
	current_price: z.number(),
	market_value: z.number(),
	unrealized_pnl: z.number(),
	unrealized_pnl_pct: z.number(),
	sector: z.string().optional(),
	last_updated: z.string().optional(),
});

export const PortfolioTransactionSchema = z.object({
	id: z.number().optional(),
	portfolio_id: z.number(),
	symbol: z.string(),
	transaction_type: z.string(), // buy, sell, dividend, split
	quantity: z.number(),
	price: z.number(),
	total_amount: z.number(),
	fees: z.number().default(0),
	transaction_date: z.string(),
	notes: z.string().optional(),
	created_at: z.string().optional(),
});

export const PortfolioSnapshotSchema = z.object({
	id: z.number().optional(),
	portfolio_id: z.number(),
	snapshot_date: z.string(),
	total_value: z.number(),
	cash_balance: z.number(),
	invested_amount: z.number(),
	unrealized_pnl: z.number(),
	unrealized_pnl_pct: z.number(),
	day_change: z.number(),
	day_change_pct: z.number(),
	positions_count: z.number(),
	top_holdings: z.string().optional(), // JSON string
	sector_allocation: z.string().optional(), // JSON string
	created_at: z.string().optional(),
});

// ============================================================================
// SWARM AI TRADING MODELS
// ============================================================================

export const SwarmAgentPromptSchema = z.object({
	id: z.number().optional(),
	agent_name: z.string().max(100),
	prompt_version: z.string().max(50),
	system_prompt: z.string(),
	is_active: z.boolean().default(true),
	created_at: z.string().optional(),
	updated_at: z.string().optional(),
	created_by: z.string().max(100).optional(),
	description: z.string().optional(),
});

export const SwarmPortfolioConfigSchema = z.object({
	id: z.number().optional(),
	portfolio_id: z.string().max(100),
	name: z.string().max(200),
	symbols: z.record(z.any()), // JSONB
	risk_tolerance: z.string().max(50),
	max_position_size_pct: z.number().default(5.0),
	max_sector_exposure_pct: z.number().default(20.0),
	cash_reserve_pct: z.number().default(10.0),
	trading_enabled: z.boolean().default(true),
	rebalance_frequency: z.string().max(50).default('weekly'),
	created_at: z.string().optional(),
	updated_at: z.string().optional(),
	is_active: z.boolean().default(true),
});

export const SwarmConversationHistorySchema = z.object({
	id: z.number().optional(),
	portfolio_id: z.string().max(100),
	conversation_id: z.string().max(100),
	user_message: z.string(),
	agent_responses: z.record(z.any()), // JSONB
	final_agent: z.string().max(100),
	turns_used: z.number(),
	success: z.boolean(),
	error_message: z.string().optional(),
	created_at: z.string().optional(),
	conversation_metadata: z.record(z.any()).optional(), // JSONB
});

export const SwarmTradingDecisionSchema = z.object({
	id: z.number().optional(),
	conversation_id: z.string().max(100),
	portfolio_id: z.string().max(100),
	decision_type: z.string().max(50),
	symbol: z.string().max(20).optional(),
	quantity: z.number().optional(),
	price: z.number().optional(),
	reasoning: z.string(),
	confidence_score: z.number().optional(),
	risk_assessment: z.string().optional(),
	executed: z.boolean().default(false),
	execution_result: z.record(z.any()).optional(), // JSONB
	created_at: z.string().optional(),
	executed_at: z.string().optional(),
});

export const SwarmMarketContextSchema = z.object({
	id: z.number().optional(),
	portfolio_id: z.string().max(100),
	context_type: z.string().max(100),
	symbol: z.string().max(20).optional(),
	data: z.record(z.any()), // JSONB
	relevance_score: z.number().optional(),
	created_at: z.string().optional(),
	expires_at: z.string().optional(),
});

// ============================================================================
// TYPE EXPORTS
// ============================================================================

export type DailyAnalysis = z.infer<typeof DailyAnalysisSchema>;
export type DailyDecision = z.infer<typeof DailyDecisionSchema>;
export type PerformanceTracking = z.infer<typeof PerformanceTrackingSchema>;
export type MarketContext = z.infer<typeof MarketContextSchema>;

export type Portfolio = z.infer<typeof PortfolioSchema>;
export type PortfolioPosition = z.infer<typeof PortfolioPositionSchema>;
export type PortfolioTransaction = z.infer<typeof PortfolioTransactionSchema>;
export type PortfolioSnapshot = z.infer<typeof PortfolioSnapshotSchema>;

export type SwarmAgentPrompt = z.infer<typeof SwarmAgentPromptSchema>;
export type SwarmPortfolioConfig = z.infer<typeof SwarmPortfolioConfigSchema>;
export type SwarmConversationHistory = z.infer<typeof SwarmConversationHistorySchema>;
export type SwarmTradingDecision = z.infer<typeof SwarmTradingDecisionSchema>;
export type SwarmMarketContext = z.infer<typeof SwarmMarketContextSchema>;

// ============================================================================
// DATABASE RESULT TYPES
// ============================================================================

export interface DatabaseResult<T> {
	success: boolean;
	data?: T;
	error?: string;
	rowCount?: number;
}

export interface QueryOptions {
	limit?: number;
	offset?: number;
	orderBy?: string;
	orderDirection?: 'ASC' | 'DESC';
	where?: Record<string, any>;
} 