/**
 * Context Types
 *
 * Simple context types for agent environmental information.
 * Type safety ensures valid configurations.
 */

// ============================================================================
// MARKET CONTEXT
// ============================================================================

export interface MarketContext {
  marketPhase: 'pre_market' | 'market_open' | 'market_close' | 'after_hours';
  vix: number; // Volatility index
  majorIndices: {
    sp500: {
      change: number;
      changePercent: number;
    };
  };
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
  }>;
  riskProfile: {
    riskTolerance: 'low' | 'medium' | 'high';
  };
}

// ============================================================================
// USER PREFERENCES
// ============================================================================

export interface UserPreferences {
  riskTolerance: 'low' | 'medium' | 'high';
  timeHorizon: 'short_term' | 'medium_term' | 'long_term';
  tradingStyle: 'conservative' | 'moderate' | 'aggressive';
  maxPositionSize: number;
}
