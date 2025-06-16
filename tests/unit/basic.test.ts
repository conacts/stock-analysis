import { describe, it, expect } from 'vitest';
import { type Advisor, type Portfolio, type AnalysisResult } from '@/db/schema';

describe('Database Types', () => {
  it('should have proper Advisor type structure', () => {
    const validAdvisor: Partial<Advisor> = {
      name: 'Test Advisor',
      systemPrompt: 'You are a test trading advisor.',
      model: 'deepseek-chat',
      temperature: 0.1,
      maxTokens: 2000,
      status: 'active',
    };

    expect(validAdvisor.name).toBe('Test Advisor');
    expect(validAdvisor.systemPrompt).toBe('You are a test trading advisor.');
    expect(validAdvisor.status).toBe('active');
  });

  it('should have proper Portfolio type structure', () => {
    const validPortfolio: Partial<Portfolio> = {
      name: 'Test Portfolio',
      description: 'A test portfolio',
      advisorId: 1,
      status: 'active',
    };

    expect(validPortfolio.name).toBe('Test Portfolio');
    expect(validPortfolio.advisorId).toBe(1);
    expect(validPortfolio.status).toBe('active');
  });

  it('should have proper AnalysisResult type structure', () => {
    const validAnalysis: Partial<AnalysisResult> = {
      portfolioId: 1,
      advisorId: 1,
      analysisType: 'market_opening',
      symbol: 'AAPL',
      analysisData: { test: 'data' },
      recommendations: { action: 'hold' },
      status: 'completed',
    };

    expect(validAnalysis.portfolioId).toBe(1);
    expect(validAnalysis.advisorId).toBe(1);
    expect(validAnalysis.symbol).toBe('AAPL');
    expect(validAnalysis.status).toBe('completed');
  });

  it('should demonstrate type safety', () => {
    // These tests show that TypeScript will catch type errors at compile time
    // rather than runtime validation with Zod schemas

    const advisor: Partial<Advisor> = {
      name: 'Test Advisor',
      status: 'active',
    };

    expect(typeof advisor.name).toBe('string');
    expect(advisor.status).toBe('active');
  });
});
