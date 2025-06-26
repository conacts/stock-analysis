/**
 * Context Types
 *
 * Enhanced context types using database schema as source of truth.
 * These provide environmental information for agents.
 */

// Import database types as source of truth
import type { MarketPhase, RiskTolerance, TimeHorizon, TradingStyle, Sentiment } from '@/db/schema';

// ============================================================================
// MARKET CONTEXT
// ============================================================================

export interface MarketContext {
  marketPhase: MarketPhase;
  vix?: number; // Volatility index
  majorIndices?: {
    sp500: {
      change: number;
      changePercent: number;
      current?: number;
    };
    nasdaq: {
      change: number;
      changePercent: number;
      current?: number;
    };
    dowJones: {
      change: number;
      changePercent: number;
      current?: number;
    };
  };
  sentiment: Sentiment;
  keyEvents?: string[];
  researchSummary?: string;
  volumeProfile?: 'high' | 'normal' | 'low';
  marketCondition?: 'trending' | 'ranging' | 'volatile';
}

// ============================================================================
// PORTFOLIO CONTEXT
// ============================================================================

export interface PortfolioContext {
  totalValue: number;
  availableCash: number;
  positions: Array<{
    symbol: string;
    quantity: number;
    currentPrice: number;
    unrealizedPnL?: number;
    marketValue?: number;
  }>;
  riskProfile: {
    riskTolerance: RiskTolerance;
    timeHorizon: TimeHorizon;
    tradingStyle: TradingStyle;
  };
  performance?: {
    todayPnL: number;
    weekPnL: number;
    monthPnL: number;
    ytdPnL: number;
  };
}

// ============================================================================
// USER PREFERENCES
// ============================================================================

export interface UserPreferences {
  riskTolerance: RiskTolerance;
  timeHorizon: TimeHorizon;
  tradingStyle: TradingStyle;
  maxPositionSize: number;
  maxDailyLoss?: number;
  preferredSectors?: string[];
  excludedSymbols?: string[];
}

// ============================================================================
// TRADING CONTEXT - For agent decision making
// ============================================================================

export interface TradingContext {
  marketContext: MarketContext;
  portfolioContext: PortfolioContext;
  userPreferences: UserPreferences;
  riskMetrics?: {
    portfolioRisk: number; // 0-100 score
    concentrationRisk: number; // 0-100 score
    liquidityRisk: number; // 0-100 score
  };
  tradingSession?: {
    tradesExecuted: number;
    pnlToday: number;
    riskBudgetUsed: number; // percentage of daily risk budget used
  };
}

// Re-export database types for convenience
export type { MarketPhase, RiskTolerance, TimeHorizon, TradingStyle, Sentiment };
