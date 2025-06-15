import { describe, it, expect } from 'vitest';
import {
  AIAgentSchema,
  SimplePortfolioSchema,
  AnalysisResultSchema,
} from '../../src/database/models';

describe('Database Models', () => {
  it('should validate AI Agent schema', () => {
    const validAgent = {
      name: 'Test Agent',
      system_prompt: 'You are a test trading agent.',
      model: 'deepseek-chat',
      temperature: 0.1,
      max_tokens: 2000,
      status: 'active' as const,
    };

    const result = AIAgentSchema.safeParse(validAgent);
    expect(result.success).toBe(true);
  });

  it('should validate Simple Portfolio schema', () => {
    const validPortfolio = {
      name: 'Test Portfolio',
      description: 'A test portfolio',
      agent_id: 1,
      status: 'active' as const,
    };

    const result = SimplePortfolioSchema.safeParse(validPortfolio);
    expect(result.success).toBe(true);
  });

  it('should validate Analysis Result schema', () => {
    const validAnalysis = {
      portfolio_id: 1,
      agent_id: 1,
      analysis_type: 'market_opening' as const,
      symbol: 'AAPL',
      analysis_data: { test: 'data' },
      recommendations: { action: 'hold' },
      status: 'completed' as const,
    };

    const result = AnalysisResultSchema.safeParse(validAnalysis);
    expect(result.success).toBe(true);
  });

  it('should reject invalid AI Agent data', () => {
    const invalidAgent = {
      name: '', // Invalid: empty name
      system_prompt: 'Test prompt',
    };

    const result = AIAgentSchema.safeParse(invalidAgent);
    expect(result.success).toBe(false);
  });
});
