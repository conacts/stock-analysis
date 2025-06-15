import { z } from 'zod';

// ============================================================================
// CORE TRADING MODELS
// ============================================================================

export const DailyAnalysisSchema = z.object({
  id: z.number().optional(),
  symbol: z.string().min(1).max(10),
  analysis_date: z.string().datetime().optional(),
  opening_price: z.number().positive().optional(),
  closing_price: z.number().positive().optional(),
  volume: z.number().int().nonnegative().optional(),
  market_cap: z.number().positive().optional(),
  pe_ratio: z.number().positive().optional(),
  analysis_data: z.record(z.any()).optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
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
  user_id: z.string().min(1).max(50),
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  cash_balance: z.number().nonnegative().default(0),
  total_value: z.number().nonnegative().default(0),
  positions: z.record(z.any()).optional(),
  performance_metrics: z.record(z.any()).optional(),
  risk_metrics: z.record(z.any()).optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
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
  portfolio_name: z.string().min(1).max(100),
  target_allocation: z.record(z.number().min(0).max(1)),
  risk_tolerance: z.enum(['low', 'medium', 'high']).default('medium'),
  max_position_size: z.number().min(0).max(1).default(0.1),
  rebalancing_threshold: z.number().min(0).max(1).default(0.05),
  active: z.boolean().default(true),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
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

// ============================================================================
// NEW CORE MODELS FOR SIMPLIFIED SCHEMA
// ============================================================================

export const AIAgentSchema = z.object({
  id: z.number().optional(),
  name: z.string().min(1).max(100),
  system_prompt: z.string().min(1),
  model: z.string().max(50).default('deepseek-chat'),
  temperature: z.number().min(0).max(2).default(0.1),
  max_tokens: z.number().int().positive().default(2000),
  status: z.enum(['active', 'inactive']).default('active'),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

export const SimplePortfolioSchema = z.object({
  id: z.number().optional(),
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  agent_id: z.number().optional(),
  status: z.enum(['active', 'paused', 'archived']).default('active'),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

export const AnalysisResultSchema = z.object({
  id: z.number().optional(),
  portfolio_id: z.number(),
  agent_id: z.number(),
  analysis_type: z.enum(['market_opening', 'daily_check', 'manual']),
  symbol: z.string().max(20).optional(),
  analysis_data: z.record(z.any()).optional(),
  recommendations: z.record(z.any()).optional(),
  status: z.enum(['pending', 'completed', 'failed']).default('completed'),
  created_at: z.string().datetime().optional(),
});

// ============================================================================
// NEW TYPE EXPORTS
// ============================================================================

export type AIAgent = z.infer<typeof AIAgentSchema>;
export type SimplePortfolio = z.infer<typeof SimplePortfolioSchema>;
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;

// ============================================================================
// DATABASE OPERATIONS INTERFACE
// ============================================================================

export interface DatabaseOperations {
  // Generic operations
  query<T = any>(sql: string, params?: any[]): Promise<DatabaseResult<T[]>>;
  insert<T = any>(table: string, data: Record<string, any>): Promise<DatabaseResult<T>>;
  update<T = any>(
    table: string,
    data: Record<string, any>,
    where: Record<string, any>
  ): Promise<DatabaseResult<T>>;
  delete(table: string, where: Record<string, any>): Promise<DatabaseResult<void>>;

  // Core model operations
  getPortfolios(options?: QueryOptions): Promise<DatabaseResult<SimplePortfolio[]>>;
  getPortfolioById(id: number): Promise<DatabaseResult<SimplePortfolio>>;
  getActivePortfolios(): Promise<DatabaseResult<SimplePortfolio[]>>;

  getAIAgents(options?: QueryOptions): Promise<DatabaseResult<AIAgent[]>>;
  getAIAgentById(id: number): Promise<DatabaseResult<AIAgent>>;
  getActiveAIAgents(): Promise<DatabaseResult<AIAgent[]>>;

  getAnalysisResults(
    portfolioId?: number,
    options?: QueryOptions
  ): Promise<DatabaseResult<AnalysisResult[]>>;
  createAnalysisResult(
    data: Omit<AnalysisResult, 'id' | 'created_at'>
  ): Promise<DatabaseResult<AnalysisResult>>;
}
