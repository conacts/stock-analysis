/**
 * Research Service Tests - Enhanced with Database Integration
 *
 * Tests the research service with proper database isolation,
 * Zod schema validation, and mocked Firecrawl responses.
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { ResearchService } from './research-service';
import {
  setupTestEnvironment,
  createTestAgent,
  createTestResearchSession,
  getTestDb,
  cleanTestDb,
  closeTestDb,
} from '@/db/test-utils';
import {
  MarketNewsSchema,
  EarningsSchema,
  EconomicIndicatorSchema,
  SectorAnalysisSchema,
  type MarketNewsData,
  type EarningsData,
} from '@/types/research';
import { z } from 'zod';

// Mock the GeneralTradingAgent to avoid actual API calls
const mockAnalyzeResult = { success: true, result: '' };
const mockAgent = {
  initializeWithHistory: () => Promise.resolve(),
  connect: () => Promise.resolve(),
  disconnect: () => Promise.resolve(),
  analyze: () => Promise.resolve(mockAnalyzeResult),
};

// Mock the agent import
vi.mock('@/agents/general-trading-agent', () => ({
  GeneralTradingAgent: vi.fn().mockImplementation(() => mockAgent),
}));

describe('ResearchService', () => {
  let testEnv: any;
  let researchService: ResearchService;

  beforeAll(async () => {
    testEnv = await setupTestEnvironment();
    researchService = new ResearchService();
  });

  afterAll(async () => {
    await testEnv.cleanup();
  });

  beforeEach(async () => {
    await cleanTestDb();
  });

  describe('Zod Schema Validation', () => {
    it('should validate valid market news data', () => {
      const validData: MarketNewsData = {
        headline: 'Markets Rally on Fed News',
        summary:
          'Stock markets surged today following positive Federal Reserve announcements regarding interest rates.',
        sentiment: 'bullish',
        impact: 'high',
        symbols: ['SPY', 'QQQ'],
        sectors: ['Technology', 'Financials'],
        timestamp: '2025-01-15T10:30:00Z',
        author: 'Jane Doe',
        source: 'Bloomberg',
      };

      const result = MarketNewsSchema.parse(validData);
      expect(result).toEqual(validData);
    });

    it('should reject invalid market news data', () => {
      const invalidData = {
        headline: '', // Empty headline should fail
        summary: 'Short', // Too short summary should fail
        sentiment: 'unknown', // Invalid sentiment should fail
        impact: 'high',
        timestamp: 'invalid-date', // Invalid timestamp should fail
        source: 'Bloomberg',
      };

      expect(() => MarketNewsSchema.parse(invalidData)).toThrow();
    });

    it('should validate valid earnings data', () => {
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
      };

      const result = EarningsSchema.parse(validData);
      expect(result).toEqual(validData);
    });

    it('should validate economic indicator data', () => {
      const validData = {
        indicator: 'CPI',
        value: 3.2,
        previousValue: 3.1,
        releaseDate: '2025-01-15',
        frequency: 'monthly' as const,
        impact: 'high' as const,
        marketImplication:
          'Inflation continues to show upward pressure, likely affecting Fed policy decisions.',
      };

      const result = EconomicIndicatorSchema.parse(validData);
      expect(result).toEqual(validData);
    });

    it('should validate sector analysis data', () => {
      const validData = {
        sector: 'Technology',
        performance: {
          oneDay: 2.5,
          oneWeek: 1.8,
          oneMonth: 4.2,
          ytd: 12.5,
        },
        momentum: 'positive' as const,
        topPerformers: [
          { symbol: 'AAPL', change: 3.2 },
          { symbol: 'MSFT', change: 2.8 },
        ],
        bottomPerformers: [{ symbol: 'META', change: -1.5 }],
      };

      const result = SectorAnalysisSchema.parse(validData);
      expect(result).toEqual(validData);
    });
  });

  describe('Research Session Management', () => {
    it('should create and complete a research session', async () => {
      const agent = await createTestAgent('TestResearchAgent');

      // Mock successful research responses
      mockAnalyzeResult.success = true;
      mockAnalyzeResult.result = JSON.stringify({
        headline: 'Test Market News',
        summary: 'This is a test market news summary with sufficient length.',
        sentiment: 'bullish',
        impact: 'medium',
        timestamp: '2025-01-15T10:30:00Z',
        source: 'Test Source',
      });

      const sessionId = await researchService.startResearchSession(agent.id, 'market_open', [
        {
          type: 'market_news',
          priority: 'high',
          maxResults: 5,
        },
      ]);

      expect(sessionId).toBeGreaterThan(0);

      // Verify session was created in database
      const db = getTestDb();
      const sessions = await db.query.researchSessions.findMany({
        where: (sessions, { eq }) => eq(sessions.id, sessionId),
      });

      expect(sessions).toHaveLength(1);
      expect(sessions[0].status).toBe('completed');
      expect(sessions[0].sessionType).toBe('market_open');
    });

    it('should handle research failures gracefully', async () => {
      const agent = await createTestAgent('TestFailureAgent');

      // Mock failed research response
      mockAnalyzeResult.success = false;
      mockAnalyzeResult.result = '';

      const sessionId = await researchService.startResearchSession(agent.id, 'market_open', [
        {
          type: 'market_news',
          priority: 'high',
          maxResults: 5,
        },
      ]);

      expect(sessionId).toBeGreaterThan(0);

      // Verify research data contains error information
      const results = await researchService.getSessionResults(sessionId);
      expect(results).toHaveLength(1);
      expect((results[0].extractedData as any).error).toBeDefined();
    });

    it('should prioritize research requests correctly', async () => {
      const agent = await createTestAgent('TestPriorityAgent');

      const executionOrder: string[] = [];

      // Mock analyze to track execution order
      mockAgent.analyze = vi.fn().mockImplementation(params => {
        executionOrder.push(params.analysisType);
        return Promise.resolve({
          success: true,
          result: JSON.stringify({
            headline: 'Test News',
            summary: 'Test summary with sufficient length for validation.',
            sentiment: 'neutral',
            impact: 'low',
            timestamp: '2025-01-15T10:30:00Z',
            source: 'Test',
          }),
        });
      });

      await researchService.startResearchSession(agent.id, 'market_open', [
        { type: 'market_news', priority: 'low' },
        { type: 'economic_indicators', priority: 'high' },
        { type: 'sector_analysis', priority: 'medium' },
      ]);

      // Verify high priority executed first, then medium, then low
      expect(executionOrder).toEqual([
        'firecrawl_research_economic_indicators',
        'firecrawl_research_sector_analysis',
        'firecrawl_research_market_news',
      ]);
    });
  });

  describe('Data Validation and Storage', () => {
    it('should store validated data correctly', async () => {
      const agent = await createTestAgent('TestStorageAgent');

      const validMarketNews = {
        headline: 'Storage Test News',
        summary: 'This is a test news item for storage validation with sufficient length.',
        sentiment: 'bullish',
        impact: 'high',
        symbols: ['TEST'],
        timestamp: '2025-01-15T10:30:00Z',
        source: 'Test Storage',
      };

      mockAnalyzeResult.success = true;
      mockAnalyzeResult.result = JSON.stringify(validMarketNews);

      const sessionId = await researchService.startResearchSession(agent.id, 'market_open', [
        { type: 'market_news', priority: 'high' },
      ]);

      const results = await researchService.getSessionResults(sessionId);

      expect(results).toHaveLength(1);
      expect(results[0].researchType).toBe('market_news');
      expect(results[0].extractedData).toMatchObject(validMarketNews);
      expect(results[0].sentiment).toBe('bullish');
      expect(results[0].impact).toBe('high');
    });

    it('should reject invalid data and store error', async () => {
      const agent = await createTestAgent('TestValidationAgent');

      const invalidData = {
        headline: '', // Empty headline - should fail validation
        summary: 'Short', // Too short - should fail validation
        sentiment: 'invalid', // Invalid sentiment - should fail validation
        impact: 'high',
        timestamp: 'invalid-date', // Invalid timestamp - should fail validation
        source: 'Test',
      };

      mockAnalyzeResult.success = true;
      mockAnalyzeResult.result = JSON.stringify(invalidData);

      const sessionId = await researchService.startResearchSession(agent.id, 'market_open', [
        { type: 'market_news', priority: 'high' },
      ]);

      const results = await researchService.getSessionResults(sessionId);

      expect(results).toHaveLength(1);
      expect((results[0].extractedData as any).error).toContain('Data validation failed');
    });
  });

  describe('Market Context Building', () => {
    it('should build comprehensive market context', async () => {
      const agent = await createTestAgent('TestContextAgent');
      const session = await createTestResearchSession(agent.id, 'market_open');

      // Create test research data directly in database
      const db = getTestDb();

      await db.insert(db.schema.researchData).values([
        {
          sessionId: session.id,
          researchType: 'market_news',
          extractedData: {
            headline: 'Markets Rally Today',
            summary: 'Strong performance across all sectors',
            sentiment: 'bullish',
            impact: 'high',
            timestamp: '2025-01-15T10:30:00Z',
            source: 'Test News',
          },
          confidence: 90,
          sentiment: 'bullish',
          impact: 'high',
        },
        {
          sessionId: session.id,
          researchType: 'sector_analysis',
          extractedData: {
            sector: 'Technology',
            performance: { oneDay: 2.5, oneWeek: 1.8, oneMonth: 4.2, ytd: 12.5 },
            momentum: 'positive',
            topPerformers: [{ symbol: 'AAPL', change: 3.2 }],
            bottomPerformers: [{ symbol: 'META', change: -1.5 }],
          },
          confidence: 85,
          sentiment: 'bullish',
          impact: 'medium',
        },
      ]);

      const context = await researchService.buildMarketContext(session.id);

      expect(context).toContain('MARKET RESEARCH CONTEXT');
      expect(context).toContain('MARKET NEWS:');
      expect(context).toContain('Markets Rally Today');
      expect(context).toContain('SECTOR ANALYSIS:');
      expect(context).toContain('Technology');
      expect(context).toContain('Total Research Items: 2');
    });

    it('should handle empty research sessions', async () => {
      const agent = await createTestAgent('TestEmptyAgent');
      const session = await createTestResearchSession(agent.id, 'market_open');

      const context = await researchService.buildMarketContext(session.id);

      expect(context).toBe('No research data available for market context.');
    });
  });

  describe('Default Research Session Configuration', () => {
    it('should create proper market open configuration', () => {
      const config = ResearchService.createMarketOpenResearchSession();

      expect(config.sessionType).toBe('market_open');
      expect(config.requests).toHaveLength(3);

      const newsRequest = config.requests.find(r => r.type === 'market_news');
      const economicRequest = config.requests.find(r => r.type === 'economic_indicators');
      const sectorRequest = config.requests.find(r => r.type === 'sector_analysis');

      expect(newsRequest?.priority).toBe('high');
      expect(economicRequest?.priority).toBe('high');
      expect(sectorRequest?.priority).toBe('medium');
    });
  });
});
