/**
 * Research Data Type Definitions
 *
 * Structured schemas for different types of market research data
 * that will be extracted using Firecrawl and stored in the database.
 *
 * Uses database schema as source of truth for all types.
 */

import { z } from 'zod';

// Import database types as source of truth
import type {
  ResearchType,
  SessionType,
  Sentiment,
  ImpactLevel,
  Momentum,
  MarketPhase,
  ResearchData,
  ResearchSession as DbResearchSession,
} from '@/db/schema';

// ============================================================================
// ZOD SCHEMAS - For strict type validation and Firecrawl extraction
// ============================================================================

// Database enum schemas
export const SentimentSchema = z.enum(['bullish', 'bearish', 'neutral']);
export const ImpactLevelSchema = z.enum(['high', 'medium', 'low']);
export const MomentumSchema = z.enum([
  'strong_positive',
  'positive',
  'neutral',
  'negative',
  'strong_negative',
]);
export const MarketPhaseSchema = z.enum([
  'pre_market',
  'market_open',
  'market_close',
  'after_hours',
]);
export const ResearchTypeSchema = z.enum([
  'market_news',
  'earnings',
  'economic_indicators',
  'sector_analysis',
  'options_flow',
  'insider_trading',
  'analyst_ratings',
]);

// Market News Schema
export const MarketNewsSchema = z.object({
  headline: z.string().min(1, 'Headline is required'),
  summary: z.string().min(10, 'Summary must be at least 10 characters'),
  sentiment: SentimentSchema,
  impact: ImpactLevelSchema,
  symbols: z.array(z.string()).optional(),
  sectors: z.array(z.string()).optional(),
  timestamp: z.string().datetime('Invalid timestamp format'),
  author: z.string().optional(),
  source: z.string().min(1, 'Source is required'),
});

// Earnings Schema
export const EarningsSchema = z.object({
  symbol: z.string().min(1, 'Symbol is required'),
  companyName: z.string().min(1, 'Company name is required'),
  reportDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD format'),
  earningsTime: z.enum(['before_market', 'after_market', 'during_market']),
  estimates: z.object({
    eps: z.number(),
    revenue: z.number(),
  }),
  actuals: z
    .object({
      eps: z.number(),
      revenue: z.number(),
    })
    .optional(),
  guidance: z
    .object({
      nextQuarterEps: z.number().optional(),
      nextQuarterRevenue: z.number().optional(),
      fullYearEps: z.number().optional(),
      fullYearRevenue: z.number().optional(),
    })
    .optional(),
  keyMetrics: z
    .object({
      marginTrends: z.string().optional(),
      growthDrivers: z.array(z.string()).optional(),
      headwinds: z.array(z.string()).optional(),
    })
    .optional(),
});

// Economic Indicators Schema
export const EconomicIndicatorSchema = z.object({
  indicator: z.string().min(1, 'Indicator name is required'),
  value: z.number(),
  previousValue: z.number().optional(),
  forecast: z.number().optional(),
  releaseDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD format'),
  frequency: z.enum(['monthly', 'quarterly', 'annual']),
  impact: ImpactLevelSchema,
  marketImplication: z.string().min(10, 'Market implication must be descriptive'),
  affectedSectors: z.array(z.string()).optional(),
});

// Sector Analysis Schema
export const SectorAnalysisSchema = z.object({
  sector: z.string().min(1, 'Sector name is required'),
  performance: z.object({
    oneDay: z.number(),
    oneWeek: z.number(),
    oneMonth: z.number(),
    ytd: z.number(),
  }),
  momentum: MomentumSchema,
  topPerformers: z
    .array(
      z.object({
        symbol: z.string(),
        change: z.number(),
      })
    )
    .min(1, 'At least one top performer required'),
  bottomPerformers: z
    .array(
      z.object({
        symbol: z.string(),
        change: z.number(),
      })
    )
    .min(1, 'At least one bottom performer required'),
  catalysts: z.array(z.string()).optional(),
  headwinds: z.array(z.string()).optional(),
});

// Options Flow Schema
export const OptionsFlowSchema = z.object({
  symbol: z.string().min(1, 'Symbol is required'),
  optionType: z.enum(['call', 'put']),
  volume: z.number().min(0),
  openInterest: z.number().min(0),
  strike: z.number().min(0),
  expiry: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD format'),
  premium: z.number().min(0),
  impliedVolatility: z.number().optional(),
  delta: z.number().optional(),
  gamma: z.number().optional(),
  unusual: z.boolean(),
  sentiment: SentimentSchema,
});

// Insider Trading Schema
export const InsiderTradingSchema = z.object({
  symbol: z.string().min(1, 'Symbol is required'),
  companyName: z.string().min(1, 'Company name is required'),
  insiderName: z.string().min(1, 'Insider name is required'),
  title: z.string().min(1, 'Title is required'),
  transactionType: z.enum(['buy', 'sell']),
  shares: z.number().min(1),
  pricePerShare: z.number().min(0),
  totalValue: z.number().min(0),
  transactionDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD format'),
  filingDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD format'),
  significance: ImpactLevelSchema,
});

// Analyst Rating Schema
export const AnalystRatingSchema = z.object({
  symbol: z.string().min(1, 'Symbol is required'),
  companyName: z.string().min(1, 'Company name is required'),
  analystFirm: z.string().min(1, 'Analyst firm is required'),
  rating: z.enum(['strong_buy', 'buy', 'hold', 'sell', 'strong_sell']),
  previousRating: z.string().optional(),
  priceTarget: z.number().min(0),
  previousPriceTarget: z.number().optional(),
  dateIssued: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD format'),
  reasoning: z.string().min(10, 'Reasoning must be descriptive'),
  keyPoints: z.array(z.string()).optional(),
});

// ============================================================================
// FIRECRAWL SCHEMA MAPPING - For direct use with Firecrawl
// ============================================================================

export const FIRECRAWL_EXTRACTION_SCHEMAS = {
  market_news: MarketNewsSchema,
  earnings: EarningsSchema,
  economic_indicators: EconomicIndicatorSchema,
  sector_analysis: SectorAnalysisSchema,
  options_flow: OptionsFlowSchema,
  insider_trading: InsiderTradingSchema,
  analyst_ratings: AnalystRatingSchema,
} as const;

// ============================================================================
// TYPESCRIPT TYPES - Inferred from Zod schemas
// ============================================================================

export type MarketNewsData = z.infer<typeof MarketNewsSchema>;
export type EarningsData = z.infer<typeof EarningsSchema>;
export type EconomicIndicatorData = z.infer<typeof EconomicIndicatorSchema>;
export type SectorAnalysisData = z.infer<typeof SectorAnalysisSchema>;
export type OptionsFlowData = z.infer<typeof OptionsFlowSchema>;
export type InsiderTradingData = z.infer<typeof InsiderTradingSchema>;
export type AnalystRatingData = z.infer<typeof AnalystRatingSchema>;

// ============================================================================
// RESEARCH REQUEST CONFIGURATION
// ============================================================================

export interface ResearchRequest {
  type: ResearchType;
  symbol?: string;
  sector?: string;
  timeframe?: string;
  priority: ImpactLevel; // Reuse impact level enum for priority
  maxResults?: number;
}

export interface ResearchSession {
  sessionType: SessionType;
  requests: ResearchRequest[];
  maxConcurrency?: number;
  timeoutMs?: number;
}

// ============================================================================
// LEGACY JSON SCHEMAS - For backward compatibility
// ============================================================================

export const RESEARCH_EXTRACTION_SCHEMAS = {
  market_news: {
    type: 'object',
    properties: {
      headline: { type: 'string' },
      summary: { type: 'string' },
      sentiment: { type: 'string', enum: ['bullish', 'bearish', 'neutral'] },
      impact: { type: 'string', enum: ['high', 'medium', 'low'] },
      symbols: { type: 'array', items: { type: 'string' } },
      sectors: { type: 'array', items: { type: 'string' } },
      timestamp: { type: 'string' },
      author: { type: 'string' },
      source: { type: 'string' },
    },
    required: ['headline', 'summary', 'sentiment', 'impact', 'timestamp', 'source'],
  },

  earnings: {
    type: 'object',
    properties: {
      symbol: { type: 'string' },
      companyName: { type: 'string' },
      reportDate: { type: 'string' },
      earningsTime: { type: 'string', enum: ['before_market', 'after_market', 'during_market'] },
      estimates: {
        type: 'object',
        properties: {
          eps: { type: 'number' },
          revenue: { type: 'number' },
        },
        required: ['eps', 'revenue'],
      },
      actuals: {
        type: 'object',
        properties: {
          eps: { type: 'number' },
          revenue: { type: 'number' },
        },
      },
    },
    required: ['symbol', 'companyName', 'reportDate', 'earningsTime', 'estimates'],
  },

  economic_indicators: {
    type: 'object',
    properties: {
      indicator: { type: 'string' },
      value: { type: 'number' },
      previousValue: { type: 'number' },
      forecast: { type: 'number' },
      releaseDate: { type: 'string' },
      frequency: { type: 'string', enum: ['monthly', 'quarterly', 'annual'] },
      impact: { type: 'string', enum: ['high', 'medium', 'low'] },
      marketImplication: { type: 'string' },
      affectedSectors: { type: 'array', items: { type: 'string' } },
    },
    required: ['indicator', 'value', 'releaseDate', 'frequency', 'impact', 'marketImplication'],
  },

  sector_analysis: {
    type: 'object',
    properties: {
      sector: { type: 'string' },
      performance: {
        type: 'object',
        properties: {
          oneDay: { type: 'number' },
          oneWeek: { type: 'number' },
          oneMonth: { type: 'number' },
          ytd: { type: 'number' },
        },
        required: ['oneDay', 'oneWeek', 'oneMonth', 'ytd'],
      },
      momentum: {
        type: 'string',
        enum: ['strong_positive', 'positive', 'neutral', 'negative', 'strong_negative'],
      },
      topPerformers: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            symbol: { type: 'string' },
            change: { type: 'number' },
          },
          required: ['symbol', 'change'],
        },
      },
      bottomPerformers: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            symbol: { type: 'string' },
            change: { type: 'number' },
          },
          required: ['symbol', 'change'],
        },
      },
    },
    required: ['sector', 'performance', 'momentum', 'topPerformers', 'bottomPerformers'],
  },
} as const;

// ============================================================================
// UTILITY TYPES - Based on database schema
// ============================================================================

export type ExtractedData =
  | MarketNewsData
  | EarningsData
  | EconomicIndicatorData
  | SectorAnalysisData
  | OptionsFlowData
  | InsiderTradingData
  | AnalystRatingData;

// Use database type as base, but make some fields optional for API responses
export interface ResearchResult {
  id?: number;
  sessionId: number;
  researchType: ResearchType;
  symbol?: string;
  sourceUrl?: string;
  extractedData: ExtractedData;
  confidence?: number;
  sentiment?: Sentiment;
  impact?: ImpactLevel;
  createdAt?: Date;
}

// Re-export database types for convenience
export type { ResearchType, SessionType, Sentiment, ImpactLevel, Momentum, MarketPhase };
export type { ResearchData, DbResearchSession };

// ============================================================================
// MARKET CONTEXT TYPES - Enhanced from database schema
// ============================================================================

export interface MarketContext {
  marketPhase: MarketPhase;
  vix?: number; // Volatility index
  majorIndices?: {
    sp500: {
      change: number;
      changePercent: number;
    };
  };
  sentiment: Sentiment;
  keyEvents?: string[];
  researchSummary?: string;
}
