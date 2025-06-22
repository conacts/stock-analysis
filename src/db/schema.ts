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

// ============================================================================
// TYPESCRIPT TYPES - Auto-generated from Drizzle schemas
// ============================================================================

export type Agent = typeof agents.$inferSelect;
export type AgentInsert = typeof agents.$inferInsert;

export type AnalysisResult = typeof analysisResults.$inferSelect;
export type AnalysisResultInsert = typeof analysisResults.$inferInsert;

export type HealthCheck = typeof healthChecks.$inferSelect;
export type HealthCheckInsert = typeof healthChecks.$inferInsert;
