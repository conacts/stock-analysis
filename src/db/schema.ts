import {
  boolean,
  decimal,
  integer,
  jsonb,
  pgTable,
  serial,
  text,
  timestamp,
  varchar,
  unique,
  index,
  interval,
  date,
  real,
} from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

// ============================================================================
// ADVISORS (simplified)
// ============================================================================

export const advisors = pgTable('advisors', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  systemPrompt: text('system_prompt').notNull(),
  model: varchar('model', { length: 50 }).default('deepseek/r1'),
  temperature: real('temperature').default(0.1),
  maxTokens: integer('max_tokens').default(2000),
  status: varchar('status', { length: 20 }).default('active'), // 'active', 'inactive'
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

export const performance = pgTable(
  'performance',
  {
    id: serial('id').primaryKey(),
    advisorId: integer('advisor_id')
      .notNull()
      .references(() => advisors.id),
    portfolioId: integer('portfolio_id')
      .notNull()
      .references(() => portfolios.id),
    periodStart: date('period_start').notNull(),
    periodEnd: date('period_end').notNull(),
    totalTrades: integer('total_trades').default(0),
    successfulTrades: integer('successful_trades').default(0),
    totalReturn: decimal('total_return', { precision: 10, scale: 4 }).default('0'),
    sharpeRatio: decimal('sharpe_ratio', { precision: 10, scale: 4 }),
    maxDrawdown: decimal('max_drawdown', { precision: 10, scale: 4 }),
    winRate: decimal('win_rate', { precision: 5, scale: 4 }),
    averageHoldTime: interval('average_hold_time'),
    createdAt: timestamp('created_at').defaultNow(),
  },
  table => ({
    advisorIndex: index('idx_performance_advisor_id').on(table.advisorId),
    portfolioIndex: index('idx_performance_portfolio_id').on(table.portfolioId),
    periodIndex: index('idx_performance_period').on(table.periodStart, table.periodEnd),
    uniquePeriod: unique().on(
      table.advisorId,
      table.portfolioId,
      table.periodStart,
      table.periodEnd
    ),
  })
);

// ============================================================================
// PORTFOLIOS
// ============================================================================

export const portfolios = pgTable(
  'portfolios',
  {
    id: serial('id').primaryKey(),
    name: varchar('name', { length: 100 }).notNull(),
    description: text('description'),
    advisorId: integer('advisor_id').references(() => advisors.id),
    status: varchar('status', { length: 20 }).default('active'), // 'active', 'paused', 'archived'
    createdAt: timestamp('created_at').defaultNow(),
    updatedAt: timestamp('updated_at').defaultNow(),
  },
  table => ({
    statusIndex: index('idx_portfolios_status').on(table.status),
    advisorIndex: index('idx_portfolios_advisor_id').on(table.advisorId),
  })
);

export const portfolioHoldings = pgTable(
  'portfolio_holdings',
  {
    id: serial('id').primaryKey(),
    portfolioId: integer('portfolio_id')
      .notNull()
      .references(() => portfolios.id),
    symbol: varchar('symbol', { length: 20 }).notNull(),
    quantity: decimal('quantity', { precision: 15, scale: 6 }).notNull(),
    averageCost: decimal('average_cost', { precision: 15, scale: 4 }).notNull(),
    currentPrice: decimal('current_price', { precision: 15, scale: 4 }),
    lastPriceUpdate: timestamp('last_price_update'),
    createdAt: timestamp('created_at').defaultNow(),
    updatedAt: timestamp('updated_at').defaultNow(),
  },
  table => ({
    portfolioIndex: index('idx_portfolio_holdings_portfolio_id').on(table.portfolioId),
    symbolIndex: index('idx_portfolio_holdings_symbol').on(table.symbol),
    uniquePortfolioSymbol: unique().on(table.portfolioId, table.symbol),
  })
);

export const transactions = pgTable(
  'transactions',
  {
    id: serial('id').primaryKey(),
    portfolioId: integer('portfolio_id')
      .notNull()
      .references(() => portfolios.id),
    symbol: varchar('symbol', { length: 20 }).notNull(),
    transactionType: varchar('transaction_type', { length: 10 }).notNull(), // 'buy', 'sell'
    quantity: decimal('quantity', { precision: 15, scale: 6 }).notNull(),
    price: decimal('price', { precision: 15, scale: 4 }).notNull(),
    totalAmount: decimal('total_amount', { precision: 15, scale: 4 }).notNull(),
    fees: decimal('fees', { precision: 15, scale: 4 }).default('0'),
    analysisResultId: integer('analysis_result_id').references(() => analysisResults.id),
    executedByAdvisor: boolean('executed_by_advisor').default(false),
    executionStatus: varchar('execution_status', { length: 20 }).default('pending'),
    executionNotes: text('execution_notes'),
    createdAt: timestamp('created_at').defaultNow(),
    executedAt: timestamp('executed_at'),
  },
  table => ({
    portfolioIndex: index('idx_transactions_portfolio_id').on(table.portfolioId),
    symbolIndex: index('idx_transactions_symbol').on(table.symbol),
    createdAtIndex: index('idx_transactions_created_at').on(table.createdAt),
  })
);

export const portfolioBalances = pgTable(
  'portfolio_balances',
  {
    id: serial('id').primaryKey(),
    portfolioId: integer('portfolio_id')
      .notNull()
      .references(() => portfolios.id),
    cashBalance: decimal('cash_balance', { precision: 15, scale: 4 }).notNull(),
    totalHoldingsValue: decimal('total_holdings_value', { precision: 15, scale: 4 }).notNull(),
    totalPortfolioValue: decimal('total_portfolio_value', { precision: 15, scale: 4 }).notNull(),
    recordedAt: timestamp('recorded_at').defaultNow(),
  },
  table => ({
    portfolioIndex: index('idx_portfolio_balances_portfolio_id').on(table.portfolioId),
    recordedAtIndex: index('idx_portfolio_balances_recorded_at').on(table.recordedAt),
  })
);

// ============================================================================
// ANALYSIS RESULTS
// ============================================================================

export const analysisResults = pgTable(
  'analysis_results',
  {
    id: serial('id').primaryKey(),
    portfolioId: integer('portfolio_id')
      .notNull()
      .references(() => portfolios.id),
    advisorId: integer('advisor_id')
      .notNull()
      .references(() => advisors.id),
    analysisType: varchar('analysis_type', { length: 50 }).notNull(),
    symbol: varchar('symbol', { length: 20 }),
    analysisData: jsonb('analysis_data'),
    recommendations: jsonb('recommendations'),
    status: varchar('status', { length: 20 }).default('completed'),
    createdAt: timestamp('created_at').defaultNow(),
  },
  table => ({
    portfolioIndex: index('idx_analysis_results_portfolio_id').on(table.portfolioId),
    createdAtIndex: index('idx_analysis_results_created_at').on(table.createdAt),
    analysisTypeIndex: index('idx_analysis_results_analysis_type').on(table.analysisType),
  })
);

// ============================================================================
// TRIGGERS AND EVENTS
// ============================================================================

export const marketTriggers = pgTable(
  'market_triggers',
  {
    id: serial('id').primaryKey(),
    name: varchar('name', { length: 100 }).notNull(),
    description: text('description'),
    triggerType: varchar('trigger_type', { length: 20 }).notNull(),
    triggerConfig: jsonb('trigger_config').notNull(),
    targetType: varchar('target_type', { length: 20 }).notNull(),
    targetId: integer('target_id'),
    advisorId: integer('advisor_id')
      .notNull()
      .references(() => advisors.id),
    isActive: boolean('is_active').default(true),
    createdAt: timestamp('created_at').defaultNow(),
    updatedAt: timestamp('updated_at').defaultNow(),
  },
  table => ({
    advisorIndex: index('idx_market_triggers_advisor_id').on(table.advisorId),
    typeIndex: index('idx_market_triggers_type').on(table.triggerType),
    activeIndex: index('idx_market_triggers_active').on(table.isActive),
  })
);

export const triggerExecutions = pgTable(
  'trigger_executions',
  {
    id: serial('id').primaryKey(),
    triggerId: integer('trigger_id')
      .notNull()
      .references(() => marketTriggers.id),
    executionTime: timestamp('execution_time').defaultNow(),
    status: varchar('status', { length: 20 }).default('pending'),
    resultData: jsonb('result_data'),
    errorMessage: text('error_message'),
    analysisResultId: integer('analysis_result_id').references(() => analysisResults.id),
    createdAt: timestamp('created_at').defaultNow(),
  },
  table => ({
    triggerIndex: index('idx_trigger_executions_trigger_id').on(table.triggerId),
    executionTimeIndex: index('idx_trigger_executions_execution_time').on(table.executionTime),
    statusIndex: index('idx_trigger_executions_status').on(table.status),
  })
);

// ============================================================================
// CONVERSATION THREADS
// ============================================================================

export const conversationThreads = pgTable(
  'conversation_threads',
  {
    id: serial('id').primaryKey(),
    portfolioId: integer('portfolio_id')
      .notNull()
      .references(() => portfolios.id),
    advisorId: integer('advisor_id')
      .notNull()
      .references(() => advisors.id),
    threadType: varchar('thread_type', { length: 20 }).notNull(),
    title: varchar('title', { length: 200 }),
    status: varchar('status', { length: 20 }).default('active'),
    parentThreadId: integer('parent_thread_id'),
    triggerExecutionId: integer('trigger_execution_id').references(() => triggerExecutions.id),
    createdAt: timestamp('created_at').defaultNow(),
    updatedAt: timestamp('updated_at').defaultNow(),
  },
  table => ({
    portfolioIndex: index('idx_conversation_threads_portfolio_id').on(table.portfolioId),
    advisorIndex: index('idx_conversation_threads_advisor_id').on(table.advisorId),
    statusIndex: index('idx_conversation_threads_status').on(table.status),
    createdAtIndex: index('idx_conversation_threads_created_at').on(table.createdAt),
  })
);

export const threadMessages = pgTable(
  'thread_messages',
  {
    id: serial('id').primaryKey(),
    threadId: integer('thread_id')
      .notNull()
      .references(() => conversationThreads.id),
    messageType: varchar('message_type', { length: 20 }).notNull(),
    content: text('content').notNull(),
    metadata: jsonb('metadata'),
    analysisResultId: integer('analysis_result_id').references(() => analysisResults.id),
    transactionId: integer('transaction_id').references(() => transactions.id),
    sequenceOrder: integer('sequence_order').notNull(),
    createdAt: timestamp('created_at').defaultNow(),
  },
  table => ({
    threadIndex: index('idx_thread_messages_thread_id').on(table.threadId),
    sequenceIndex: index('idx_thread_messages_sequence').on(table.threadId, table.sequenceOrder),
  })
);

export const advisorFunctionCalls = pgTable(
  'advisor_function_calls',
  {
    id: serial('id').primaryKey(),
    threadMessageId: integer('thread_message_id')
      .notNull()
      .references(() => threadMessages.id),
    functionName: varchar('function_name', { length: 100 }).notNull(),
    parameters: jsonb('parameters').notNull(),
    result: jsonb('result'),
    status: varchar('status', { length: 20 }).default('pending'),
    errorMessage: text('error_message'),
    executionTimeMs: integer('execution_time_ms'),
    createdAt: timestamp('created_at').defaultNow(),
    completedAt: timestamp('completed_at'),
  },
  table => ({
    messageIndex: index('idx_advisor_function_calls_message_id').on(table.threadMessageId),
    statusIndex: index('idx_advisor_function_calls_status').on(table.status),
  })
);

// ============================================================================
// SIMPLIFIED RELATIONS
// ============================================================================

export const advisorsRelations = relations(advisors, ({ many }) => ({
  portfolios: many(portfolios),
  analysisResults: many(analysisResults),
  marketTriggers: many(marketTriggers),
  conversationThreads: many(conversationThreads),
  performance: many(performance),
}));

export const portfoliosRelations = relations(portfolios, ({ one, many }) => ({
  advisor: one(advisors, {
    fields: [portfolios.advisorId],
    references: [advisors.id],
  }),
  holdings: many(portfolioHoldings),
  transactions: many(transactions),
  balances: many(portfolioBalances),
  analysisResults: many(analysisResults),
  conversationThreads: many(conversationThreads),
}));

export const transactionsRelations = relations(transactions, ({ one }) => ({
  portfolio: one(portfolios, {
    fields: [transactions.portfolioId],
    references: [portfolios.id],
  }),
  analysisResult: one(analysisResults, {
    fields: [transactions.analysisResultId],
    references: [analysisResults.id],
  }),
}));

export const conversationThreadsRelations = relations(conversationThreads, ({ one, many }) => ({
  portfolio: one(portfolios, {
    fields: [conversationThreads.portfolioId],
    references: [portfolios.id],
  }),
  advisor: one(advisors, {
    fields: [conversationThreads.advisorId],
    references: [advisors.id],
  }),
  triggerExecution: one(triggerExecutions, {
    fields: [conversationThreads.triggerExecutionId],
    references: [triggerExecutions.id],
  }),
  messages: many(threadMessages),
}));

export const threadMessagesRelations = relations(threadMessages, ({ one, many }) => ({
  thread: one(conversationThreads, {
    fields: [threadMessages.threadId],
    references: [conversationThreads.id],
  }),
  analysisResult: one(analysisResults, {
    fields: [threadMessages.analysisResultId],
    references: [analysisResults.id],
  }),
  transaction: one(transactions, {
    fields: [threadMessages.transactionId],
    references: [transactions.id],
  }),
  functionCalls: many(advisorFunctionCalls),
}));

// ============================================================================
// TYPESCRIPT TYPES (Auto-generated from Drizzle schemas)
// ============================================================================

export type Advisor = typeof advisors.$inferSelect;
export type AdvisorInsert = typeof advisors.$inferInsert;

export type Performance = typeof performance.$inferSelect;
export type PerformanceInsert = typeof performance.$inferInsert;

export type Portfolio = typeof portfolios.$inferSelect;
export type PortfolioInsert = typeof portfolios.$inferInsert;

export type PortfolioHolding = typeof portfolioHoldings.$inferSelect;
export type PortfolioHoldingInsert = typeof portfolioHoldings.$inferInsert;

export type Transaction = typeof transactions.$inferSelect;
export type TransactionInsert = typeof transactions.$inferInsert;

export type PortfolioBalance = typeof portfolioBalances.$inferSelect;
export type PortfolioBalanceInsert = typeof portfolioBalances.$inferInsert;

export type AnalysisResult = typeof analysisResults.$inferSelect;
export type AnalysisResultInsert = typeof analysisResults.$inferInsert;

export type MarketTrigger = typeof marketTriggers.$inferSelect;
export type MarketTriggerInsert = typeof marketTriggers.$inferInsert;

export type TriggerExecution = typeof triggerExecutions.$inferSelect;
export type TriggerExecutionInsert = typeof triggerExecutions.$inferInsert;

export type ConversationThread = typeof conversationThreads.$inferSelect;
export type ConversationThreadInsert = typeof conversationThreads.$inferInsert;

export type ThreadMessage = typeof threadMessages.$inferSelect;
export type ThreadMessageInsert = typeof threadMessages.$inferInsert;

export type AdvisorFunctionCall = typeof advisorFunctionCalls.$inferSelect;
export type AdvisorFunctionCallInsert = typeof advisorFunctionCalls.$inferInsert;

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface DatabaseResult<T> {
  success: boolean;
  data?: T;
  error?: string;
  rowCount?: number;
}
