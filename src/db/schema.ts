import {
  boolean,
  integer,
  pgTable,
  serial,
  text,
  timestamp,
  varchar,
  jsonb,
  pgEnum,
} from 'drizzle-orm/pg-core';

// ============================================================================
// POSTGRESQL ENUMS - Source of truth for all type constraints
// ============================================================================

// Research and Analysis Enums
export const researchTypeEnum = pgEnum('research_type', [
  'market_news',
  'earnings',
  'economic_indicators',
  'sector_analysis',
  'options_flow',
  'insider_trading',
  'analyst_ratings',
]);

export const sessionTypeEnum = pgEnum('session_type', [
  'market_open',
  'earnings_season',
  'portfolio_review',
  'risk_assessment',
]);

export const sessionStatusEnum = pgEnum('session_status', ['in_progress', 'completed', 'failed']);

// Market Context Enums
export const marketPhaseEnum = pgEnum('market_phase', [
  'pre_market',
  'market_open',
  'market_close',
  'after_hours',
]);

export const sentimentEnum = pgEnum('sentiment', ['bullish', 'bearish', 'neutral']);

export const impactLevelEnum = pgEnum('impact_level', ['high', 'medium', 'low']);

export const momentumEnum = pgEnum('momentum', [
  'strong_positive',
  'positive',
  'neutral',
  'negative',
  'strong_negative',
]);

// Trading and Risk Enums
export const riskToleranceEnum = pgEnum('risk_tolerance', ['low', 'medium', 'high']);

export const timeHorizonEnum = pgEnum('time_horizon', ['short_term', 'medium_term', 'long_term']);

export const tradingStyleEnum = pgEnum('trading_style', ['conservative', 'moderate', 'aggressive']);

// ============================================================================
// CORE TABLES - Build types-first approach
// ============================================================================

// Basic agent configuration storage
export const agents = pgTable('agents', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  instructions: text('instructions').notNull(),
  model: varchar('model', { length: 50 }).default('gpt-4o'),
  portfolioId: varchar('portfolio_id', { length: 100 }), // One agent per portfolio
  riskTolerance: riskToleranceEnum('risk_tolerance').default('medium'),
  tradingStyle: tradingStyleEnum('trading_style').default('moderate'),
  createdAt: timestamp('created_at').defaultNow(),
});

// Enhanced analysis results with market context
export const analysisResults = pgTable('analysis_results', {
  id: serial('id').primaryKey(),
  agentId: integer('agent_id').references(() => agents.id),
  analysisType: varchar('analysis_type', { length: 50 }).notNull(),
  symbol: varchar('symbol', { length: 20 }),
  marketPhase: marketPhaseEnum('market_phase'),
  sentiment: sentimentEnum('sentiment'),
  confidence: integer('confidence'), // 1-100 confidence score
  result: text('result'),
  success: boolean('success').default(true),
  createdAt: timestamp('created_at').defaultNow(),
});

// Health check logs - since that's our working workflow
export const healthChecks = pgTable('health_checks', {
  id: serial('id').primaryKey(),
  status: varchar('status', { length: 20 }).notNull(), // 'healthy', 'unhealthy', 'degraded'
  details: text('details'),
  createdAt: timestamp('created_at').defaultNow(),
});

// Conversation history - one continuous conversation per agent
export const conversations = pgTable('conversations', {
  id: serial('id').primaryKey(),
  agentId: integer('agent_id')
    .references(() => agents.id)
    .notNull(),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

// Individual messages within conversations
export const conversationMessages = pgTable('conversation_messages', {
  id: serial('id').primaryKey(),
  conversationId: integer('conversation_id')
    .references(() => conversations.id)
    .notNull(),
  role: varchar('role', { length: 20 }).notNull(), // 'user' | 'assistant' | 'system'
  content: text('content').notNull(),
  timestamp: timestamp('timestamp').defaultNow(),
});

// ============================================================================
// RESEARCH DATA STORAGE - Enhanced with proper enums
// ============================================================================

// Research sessions - groups related research items
export const researchSessions = pgTable('research_sessions', {
  id: serial('id').primaryKey(),
  agentId: integer('agent_id')
    .references(() => agents.id)
    .notNull(),
  sessionType: sessionTypeEnum('session_type').notNull(),
  status: sessionStatusEnum('status').notNull().default('in_progress'),
  marketPhase: marketPhaseEnum('market_phase'),
  createdAt: timestamp('created_at').defaultNow(),
  completedAt: timestamp('completed_at'),
});

// Individual research items with structured data
export const researchData = pgTable('research_data', {
  id: serial('id').primaryKey(),
  sessionId: integer('session_id')
    .references(() => researchSessions.id)
    .notNull(),
  researchType: researchTypeEnum('research_type').notNull(),
  symbol: varchar('symbol', { length: 20 }),
  sourceUrl: text('source_url'),
  extractedData: jsonb('extracted_data').notNull(), // Structured data based on research type schema
  confidence: integer('confidence'), // 1-100 confidence score from extraction
  sentiment: sentimentEnum('sentiment'),
  impact: impactLevelEnum('impact'),
  createdAt: timestamp('created_at').defaultNow(),
});

// Market open context - aggregated research for market open analysis
export const marketOpenContexts = pgTable('market_open_contexts', {
  id: serial('id').primaryKey(),
  sessionId: integer('session_id')
    .references(() => researchSessions.id)
    .notNull(),
  marketDate: varchar('market_date', { length: 10 }).notNull(), // YYYY-MM-DD
  marketPhase: marketPhaseEnum('market_phase').notNull(),
  preMarketSentiment: sentimentEnum('pre_market_sentiment'),
  keyEvents: jsonb('key_events'), // Array of key events from research
  sectorRotation: jsonb('sector_rotation'), // Sector performance data
  economicIndicators: jsonb('economic_indicators'), // Economic data
  newsImpact: jsonb('news_impact'), // News impact analysis
  overallConfidence: integer('overall_confidence'), // 1-100 overall confidence
  createdAt: timestamp('created_at').defaultNow(),
});

// ============================================================================
// TYPESCRIPT TYPES - Auto-generated from Drizzle schemas (Source of Truth)
// ============================================================================

// Core Entity Types
export type Agent = typeof agents.$inferSelect;
export type AgentInsert = typeof agents.$inferInsert;

export type AnalysisResult = typeof analysisResults.$inferSelect;
export type AnalysisResultInsert = typeof analysisResults.$inferInsert;

export type HealthCheck = typeof healthChecks.$inferSelect;
export type HealthCheckInsert = typeof healthChecks.$inferInsert;

export type Conversation = typeof conversations.$inferSelect;
export type ConversationInsert = typeof conversations.$inferInsert;

export type ConversationMessage = typeof conversationMessages.$inferSelect;
export type ConversationMessageInsert = typeof conversationMessages.$inferInsert;

// Research Types
export type ResearchSession = typeof researchSessions.$inferSelect;
export type ResearchSessionInsert = typeof researchSessions.$inferInsert;

export type ResearchData = typeof researchData.$inferSelect;
export type ResearchDataInsert = typeof researchData.$inferInsert;

export type MarketOpenContext = typeof marketOpenContexts.$inferSelect;
export type MarketOpenContextInsert = typeof marketOpenContexts.$inferInsert;

// ============================================================================
// ENUM VALUE TYPES - Extracted from database enums
// ============================================================================

// Research Enums
export type ResearchType = (typeof researchTypeEnum.enumValues)[number];
export type SessionType = (typeof sessionTypeEnum.enumValues)[number];
export type SessionStatus = (typeof sessionStatusEnum.enumValues)[number];

// Market Context Enums
export type MarketPhase = (typeof marketPhaseEnum.enumValues)[number];
export type Sentiment = (typeof sentimentEnum.enumValues)[number];
export type ImpactLevel = (typeof impactLevelEnum.enumValues)[number];
export type Momentum = (typeof momentumEnum.enumValues)[number];

// Trading and Risk Enums
export type RiskTolerance = (typeof riskToleranceEnum.enumValues)[number];
export type TimeHorizon = (typeof timeHorizonEnum.enumValues)[number];
export type TradingStyle = (typeof tradingStyleEnum.enumValues)[number];
