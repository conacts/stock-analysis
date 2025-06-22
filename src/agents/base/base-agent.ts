/**
 * Base Trading Agent Class
 *
 * Simple foundation for trading agents wrapping OpenAI Agents SDK.
 * Type safety ensures valid configurations.
 */

import { Agent, run } from '@openai/agents';
import type { MarketContext, PortfolioContext, UserPreferences } from '@/types/context';
import { AgentError } from '@/types/errors';

export interface BaseAgentConfig {
  name: string;
  instructions: string;
  model?: string;
  temperature?: number;
}

export interface AnalysisRequest {
  analysisType: string;
  symbol?: string;
  parameters?: Record<string, any>;
}

export interface AnalysisResponse {
  success: boolean;
  result?: string;
  error?: string;
  executionTime: number;
}

export abstract class BaseTradingAgent {
  protected agent: Agent;
  protected config: BaseAgentConfig;

  // Optional context
  protected marketContext?: MarketContext;
  protected portfolioContext?: PortfolioContext;
  protected userPreferences?: UserPreferences;

  constructor(config: BaseAgentConfig) {
    this.config = config;

    // Initialize OpenAI Agent
    this.agent = new Agent({
      name: config.name,
      instructions: config.instructions,
      model: config.model || 'gpt-4o',
    });
  }

  // ============================================================================
  // ABSTRACT METHODS - Must be implemented by specific agent types
  // ============================================================================

  /**
   * Primary analysis method - each agent implements their specialty
   */
  abstract analyze(request: AnalysisRequest): Promise<AnalysisResponse>;

  // ============================================================================
  // CONTEXT MANAGEMENT
  // ============================================================================

  public updateMarketContext(context: MarketContext): void {
    this.marketContext = context;
  }

  public updatePortfolioContext(context: PortfolioContext): void {
    this.portfolioContext = context;
  }

  public updateUserPreferences(preferences: UserPreferences): void {
    this.userPreferences = preferences;
  }

  // ============================================================================
  // ANALYSIS EXECUTION
  // ============================================================================

  protected async executeAnalysis(prompt: string): Promise<string> {
    try {
      const result = await run(this.agent, prompt);
      return result.finalOutput || 'No analysis output received';
    } catch (error) {
      throw new AgentError(
        `Analysis execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'ANALYSIS_EXECUTION_ERROR'
      );
    }
  }

  // ============================================================================
  // HEALTH CHECK
  // ============================================================================

  public async healthCheck(): Promise<{ healthy: boolean; message: string }> {
    try {
      const testResult = await run(
        this.agent,
        'Please respond with "Agent healthy" if you are functioning correctly.'
      );
      return {
        healthy: testResult.finalOutput?.includes('healthy') || false,
        message: testResult.finalOutput || 'No response received',
      };
    } catch (error) {
      return {
        healthy: false,
        message: `Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      };
    }
  }
}
