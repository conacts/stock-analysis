import { boolean, integer, pgTable, serial, text, timestamp, varchar } from 'drizzle-orm/pg-core';

// ============================================================================
// MINIMAL SCHEMA - Build types-first approach
// ============================================================================

// Basic agent configuration storage
export const agents = pgTable('agents', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  instructions: text('instructions').notNull(),
  model: varchar('model', { length: 50 }).default('gpt-4o'),
  portfolioId: varchar('portfolio_id', { length: 100 }), // One agent per portfolio
  createdAt: timestamp('created_at').defaultNow(),
});

// Simple analysis results - we'll expand as we learn what we need
export const analysisResults = pgTable('analysis_results', {
  id: serial('id').primaryKey(),
  agentId: integer('agent_id').references(() => agents.id),
  analysisType: varchar('analysis_type', { length: 50 }).notNull(),
  symbol: varchar('symbol', { length: 20 }),
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
// TYPESCRIPT TYPES - Auto-generated from Drizzle schemas
// ============================================================================

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
