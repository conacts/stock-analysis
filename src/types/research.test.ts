/**
 * Research Types Tests - Zod Schema Validation
 *
 * Tests the Zod schemas for strict type validation without requiring database connectivity.
 * These tests ensure our Firecrawl extraction schemas work correctly.
 */

import { describe, it, expect } from 'vitest';
import {
  MarketNewsSchema,
  EarningsSchema,
  EconomicIndicatorSchema,
  SectorAnalysisSchema,
  OptionsFlowSchema,
  InsiderTradingSchema,
  AnalystRatingSchema,
  FIRECRAWL_EXTRACTION_SCHEMAS,
  type MarketNewsData,
  type EarningsData,
  type EconomicIndicatorData,
  type SectorAnalysisData,
} from './research';
import { z } from 'zod';

describe('Research Type Validation', () => {
  describe('MarketNewsSchema', () => {
    it('should validate complete valid market news data', () => {
      const validData: MarketNewsData = {
        headline: 'Markets Rally on Fed News',
        summary:
          'Stock markets surged today following positive Federal Reserve announcements regarding interest rates and economic outlook.',
        sentiment: 'bullish',
        impact: 'high',
        symbols: ['SPY', 'QQQ', 'DIA'],
        sectors: ['Technology', 'Financials', 'Healthcare'],
        timestamp: '2025-01-15T10:30:00Z',
        author: 'Jane Doe',
        source: 'Bloomberg',
      };

      const result = MarketNewsSchema.parse(validData);
      expect(result).toEqual(validData);
      expect(result.sentiment).toBe('bullish');
      expect(result.impact).toBe('high');
    });

    it('should validate minimal required market news data', () => {
      const minimalData = {
        headline: 'Minimal News Item',
        summary: 'This is a minimal news summary with just the required fields present.',
        sentiment: 'neutral' as const,
        impact: 'low' as const,
        timestamp: '2025-01-15T10:30:00Z',
        source: 'Test Source',
      };

      const result = MarketNewsSchema.parse(minimalData);
      expect(result.headline).toBe('Minimal News Item');
      expect(result.symbols).toBeUndefined();
      expect(result.author).toBeUndefined();
    });

    it('should reject invalid market news data', () => {
      const invalidCases = [
        {
          name: 'empty headline',
          data: {
            headline: '',
            summary: 'Valid summary with sufficient length',
            sentiment: 'bullish',
            impact: 'high',
            timestamp: '2025-01-15T10:30:00Z',
            source: 'Bloomberg',
          },
        },
        {
          name: 'too short summary',
          data: {
            headline: 'Valid Headline',
            summary: 'Short',
            sentiment: 'bullish',
            impact: 'high',
            timestamp: '2025-01-15T10:30:00Z',
            source: 'Bloomberg',
          },
        },
        {
          name: 'invalid sentiment',
          data: {
            headline: 'Valid Headline',
            summary: 'Valid summary with sufficient length',
            sentiment: 'unknown',
            impact: 'high',
            timestamp: '2025-01-15T10:30:00Z',
            source: 'Bloomberg',
          },
        },
        {
          name: 'invalid timestamp',
          data: {
            headline: 'Valid Headline',
            summary: 'Valid summary with sufficient length',
            sentiment: 'bullish',
            impact: 'high',
            timestamp: 'invalid-date',
            source: 'Bloomberg',
          },
        },
        {
          name: 'missing source',
          data: {
            headline: 'Valid Headline',
            summary: 'Valid summary with sufficient length',
            sentiment: 'bullish',
            impact: 'high',
            timestamp: '2025-01-15T10:30:00Z',
          },
        },
      ];

      invalidCases.forEach(({ name, data }) => {
        expect(() => MarketNewsSchema.parse(data), `Failed case: ${name}`).toThrow();
      });
    });
  });

  describe('EarningsSchema', () => {
    it('should validate complete earnings data', () => {
      const validData: EarningsData = {
        symbol: 'AAPL',
        companyName: 'Apple Inc.',
        reportDate: '2025-01-15',
        earningsTime: 'after_market',
        estimates: {
          eps: 1.25,
          revenue: 95000000000,
        },
        actuals: {
          eps: 1.3,
          revenue: 97000000000,
        },
        guidance: {
          nextQuarterEps: 1.35,
          nextQuarterRevenue: 98000000000,
          fullYearEps: 5.2,
          fullYearRevenue: 385000000000,
        },
        keyMetrics: {
          marginTrends: 'Improving gross margins due to product mix',
          growthDrivers: ['iPhone sales', 'Services growth', 'China recovery'],
          headwinds: ['Supply chain constraints', 'Currency headwinds'],
        },
      };

      const result = EarningsSchema.parse(validData);
      expect(result.symbol).toBe('AAPL');
      expect(result.estimates.eps).toBe(1.25);
      expect(result.actuals?.eps).toBe(1.3);
    });

    it('should validate minimal earnings data', () => {
      const minimalData = {
        symbol: 'MSFT',
        companyName: 'Microsoft Corporation',
        reportDate: '2025-01-15',
        earningsTime: 'before_market' as const,
        estimates: {
          eps: 2.15,
          revenue: 56000000000,
        },
      };

      const result = EarningsSchema.parse(minimalData);
      expect(result.actuals).toBeUndefined();
      expect(result.guidance).toBeUndefined();
    });

    it('should reject invalid earnings data', () => {
      const invalidCases = [
        {
          name: 'invalid date format',
          data: {
            symbol: 'AAPL',
            companyName: 'Apple Inc.',
            reportDate: '2025/01/15', // Wrong format
            earningsTime: 'after_market',
            estimates: { eps: 1.25, revenue: 95000000000 },
          },
        },
        {
          name: 'invalid earnings time',
          data: {
            symbol: 'AAPL',
            companyName: 'Apple Inc.',
            reportDate: '2025-01-15',
            earningsTime: 'invalid_time',
            estimates: { eps: 1.25, revenue: 95000000000 },
          },
        },
      ];

      invalidCases.forEach(({ name, data }) => {
        expect(() => EarningsSchema.parse(data), `Failed case: ${name}`).toThrow();
      });
    });
  });

  describe('EconomicIndicatorSchema', () => {
    it('should validate economic indicator data', () => {
      const validData: EconomicIndicatorData = {
        indicator: 'Consumer Price Index (CPI)',
        value: 3.2,
        previousValue: 3.1,
        forecast: 3.0,
        releaseDate: '2025-01-15',
        frequency: 'monthly',
        impact: 'high',
        marketImplication:
          'Higher than expected inflation reading suggests continued pressure on Federal Reserve policy decisions and potential for more aggressive rate measures.',
        affectedSectors: ['Real Estate', 'Financials', 'Consumer Discretionary'],
      };

      const result = EconomicIndicatorSchema.parse(validData);
      expect(result.indicator).toBe('Consumer Price Index (CPI)');
      expect(result.value).toBe(3.2);
      expect(result.frequency).toBe('monthly');
    });

    it('should reject short market implications', () => {
      const invalidData = {
        indicator: 'CPI',
        value: 3.2,
        releaseDate: '2025-01-15',
        frequency: 'monthly' as const,
        impact: 'high' as const,
        marketImplication: 'Short', // Too short
      };

      expect(() => EconomicIndicatorSchema.parse(invalidData)).toThrow();
    });
  });

  describe('SectorAnalysisSchema', () => {
    it('should validate sector analysis data', () => {
      const validData: SectorAnalysisData = {
        sector: 'Technology',
        performance: {
          oneDay: 2.5,
          oneWeek: 1.8,
          oneMonth: 4.2,
          ytd: 12.5,
        },
        momentum: 'positive',
        topPerformers: [
          { symbol: 'AAPL', change: 3.2 },
          { symbol: 'MSFT', change: 2.8 },
          { symbol: 'GOOGL', change: 2.1 },
        ],
        bottomPerformers: [
          { symbol: 'META', change: -1.5 },
          { symbol: 'NFLX', change: -0.8 },
        ],
        catalysts: ['AI adoption', 'Cloud growth', 'Earnings strength'],
        headwinds: ['Regulatory concerns', 'Valuation concerns'],
      };

      const result = SectorAnalysisSchema.parse(validData);
      expect(result.sector).toBe('Technology');
      expect(result.topPerformers).toHaveLength(3);
      expect(result.bottomPerformers).toHaveLength(2);
    });

    it('should require at least one top and bottom performer', () => {
      const invalidData = {
        sector: 'Technology',
        performance: { oneDay: 2.5, oneWeek: 1.8, oneMonth: 4.2, ytd: 12.5 },
        momentum: 'positive' as const,
        topPerformers: [], // Empty array should fail
        bottomPerformers: [{ symbol: 'META', change: -1.5 }],
      };

      expect(() => SectorAnalysisSchema.parse(invalidData)).toThrow();
    });
  });

  describe('FIRECRAWL_EXTRACTION_SCHEMAS', () => {
    it('should contain all expected research types', () => {
      const expectedTypes = [
        'market_news',
        'earnings',
        'economic_indicators',
        'sector_analysis',
        'options_flow',
        'insider_trading',
        'analyst_ratings',
      ];

      expectedTypes.forEach(type => {
        expect(FIRECRAWL_EXTRACTION_SCHEMAS).toHaveProperty(type);
        expect(
          FIRECRAWL_EXTRACTION_SCHEMAS[type as keyof typeof FIRECRAWL_EXTRACTION_SCHEMAS]
        ).toBeDefined();
      });
    });

    it('should have schemas that are Zod instances', () => {
      Object.values(FIRECRAWL_EXTRACTION_SCHEMAS).forEach(schema => {
        expect(schema).toBeInstanceOf(z.ZodObject);
      });
    });
  });

  describe('Real-world data examples', () => {
    it('should handle realistic market news example', () => {
      const realisticNews = {
        headline: 'Federal Reserve Holds Interest Rates Steady, Signals Potential Cuts Ahead',
        summary:
          'The Federal Reserve announced today that it will maintain current interest rates while indicating a potential shift toward easing monetary policy in response to cooling inflation data. The decision comes as economic indicators suggest a gradual slowdown in price pressures across key sectors.',
        sentiment: 'bullish' as const,
        impact: 'high' as const,
        symbols: ['SPY', 'TLT', 'XLF'],
        sectors: ['Financials', 'Real Estate', 'Utilities'],
        timestamp: '2025-01-15T14:00:00Z',
        author: 'Federal Reserve Communications',
        source: 'Federal Reserve Official Release',
      };

      expect(() => MarketNewsSchema.parse(realisticNews)).not.toThrow();
    });

    it('should handle realistic earnings example', () => {
      const realisticEarnings = {
        symbol: 'NVDA',
        companyName: 'NVIDIA Corporation',
        reportDate: '2025-01-15',
        earningsTime: 'after_market' as const,
        estimates: {
          eps: 4.12,
          revenue: 28500000000,
        },
        actuals: {
          eps: 4.28,
          revenue: 29200000000,
        },
        guidance: {
          nextQuarterRevenue: 30000000000,
        },
        keyMetrics: {
          marginTrends: 'Data center margins expanding due to AI demand',
          growthDrivers: ['AI chip demand', 'Data center growth', 'Enterprise adoption'],
          headwinds: ['China export restrictions', 'Competition from AMD'],
        },
      };

      expect(() => EarningsSchema.parse(realisticEarnings)).not.toThrow();
    });
  });

  describe('Error handling and validation messages', () => {
    it('should provide clear error messages for validation failures', () => {
      const invalidData = {
        headline: '',
        summary: 'Too short',
        sentiment: 'invalid',
        impact: 'high',
        timestamp: 'invalid',
        source: '',
      };

      try {
        MarketNewsSchema.parse(invalidData);
        expect.fail('Should have thrown validation error');
      } catch (error) {
        if (error instanceof z.ZodError) {
          expect(error.errors.length).toBeGreaterThan(0);
          expect(error.errors.some(e => e.path.includes('headline'))).toBe(true);
          expect(error.errors.some(e => e.path.includes('summary'))).toBe(true);
          expect(error.errors.some(e => e.path.includes('sentiment'))).toBe(true);
        } else {
          expect.fail('Should have thrown ZodError');
        }
      }
    });
  });
});
