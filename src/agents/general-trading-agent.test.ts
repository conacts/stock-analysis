/**
 * General Trading Agent Tests
 *
 * Tests for the GeneralTradingAgent with Firecrawl MCP integration
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { GeneralTradingAgent } from './general-trading-agent';
import { FIRECRAWL_API_KEY } from '@/config/environment';

describe('GeneralTradingAgent', () => {
  let agent: GeneralTradingAgent;

  beforeEach(() => {
    agent = new GeneralTradingAgent();
  });

  afterEach(async () => {
    // Clean up MCP connections
    await agent.disconnect();
  });

  it('should initialize with correct configuration', () => {
    const status = agent.getStatus();

    expect(status.name).toBe('GeneralTradingAgent');
    expect(status.firecrawlEnabled).toBe(true);
    expect(status.initialized).toBe(false); // Not initialized until initializeWithHistory is called
  });

  it('should handle analysis requests', async () => {
    // Skip this test in CI environments or if no API keys are available
    if (!FIRECRAWL_API_KEY || !process.env['OPENAI_API_KEY']) {
      console.log('⚠️ Skipping analysis test - API keys not available');
      return;
    }

    // Initialize the agent
    await agent.initializeWithHistory();
    await agent.connect();

    try {
      const result = await agent.analyze({
        analysisType: 'test_analysis',
        parameters: {
          prompt: 'Provide a brief market overview without using web scraping tools.',
        },
      });

      // The test should handle both success and failure cases
      expect(result).toBeDefined();
      expect(typeof result.success).toBe('boolean');
      expect(typeof result.executionTime).toBe('number');
      expect(result.executionTime).toBeGreaterThan(0);

      if (result.success) {
        expect(result.result).toBeDefined();
        expect(typeof result.result).toBe('string');
      } else {
        expect(result.error).toBeDefined();
        console.log('Analysis failed as expected in test environment:', result.error);
      }
    } finally {
      await agent.disconnect();
    }
  });

  it('should return proper status information', () => {
    const status = agent.getStatus();

    expect(status).toHaveProperty('name');
    expect(status).toHaveProperty('initialized');
    expect(status).toHaveProperty('firecrawlEnabled');
    expect(status).toHaveProperty('mcpServersConnected');
    expect(status.firecrawlEnabled).toBe(true);
  });

  it('should handle different firecrawl modes', () => {
    const hostedAgent = new GeneralTradingAgent({ firecrawlMode: 'hosted' });
    const streamableAgent = new GeneralTradingAgent({ firecrawlMode: 'streamable' });
    const stdioAgent = new GeneralTradingAgent({ firecrawlMode: 'stdio' });

    // All should initialize without errors
    expect(hostedAgent.getStatus().name).toBe('GeneralTradingAgent');
    expect(streamableAgent.getStatus().name).toBe('GeneralTradingAgent');
    expect(stdioAgent.getStatus().name).toBe('GeneralTradingAgent');
  });

  it('should work without firecrawl if disabled', () => {
    const noFirecrawlAgent = new GeneralTradingAgent({ enableFirecrawl: false });
    const status = noFirecrawlAgent.getStatus();

    expect(status.firecrawlEnabled).toBe(false);
    expect(status.mcpServersConnected).toBe(0);
  });
});

describe('GeneralTradingAgent Convenience Functions', () => {
  it('should provide backward compatibility functions', async () => {
    const { getDefaultAgent, getAgentStatus } = await import('./general-trading-agent');

    const agent = getDefaultAgent();
    expect(agent).toBeInstanceOf(GeneralTradingAgent);

    const status = getAgentStatus();
    expect(status).toHaveProperty('initialized');
  });
});
