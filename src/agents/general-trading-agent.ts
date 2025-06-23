/**
 * General Trading Agent - Market Open Workflow
 *
 * A concrete agent that extends BaseAgent with Firecrawl MCP integration
 * for web scraping and market research capabilities.
 */

import { run } from '@openai/agents';
import {
  BaseAgent,
  type BaseAgentConfig,
  type AnalysisRequest,
  type AnalysisResponse,
} from '@/agents/base/base-agent';
import { AgentError } from '@/types/errors';

/**
 * General Trading Agent with Firecrawl MCP Integration
 *
 * Provides comprehensive market analysis with web scraping capabilities
 * for real-time market data and news analysis.
 */
export class GeneralTradingAgent extends BaseAgent {
  constructor(config?: Partial<BaseAgentConfig>) {
    super({
      name: 'GeneralTradingAgent',
      instructions: `You are a general trading assistant focused on market analysis and trading insights.

Your primary responsibilities:
- Analyze market conditions at market open
- Provide trading insights and recommendations  
- Track market sentiment and key events
- Help with portfolio analysis and decision making
- Use web scraping tools to gather real-time market data and news

Available Firecrawl MCP Tools:
- firecrawl_scrape: Scrape content from individual URLs
- firecrawl_batch_scrape: Scrape multiple URLs efficiently
- firecrawl_search: Search the web for market news and data
- firecrawl_crawl: Crawl websites for comprehensive data gathering
- firecrawl_extract: Extract structured data from financial websites
- firecrawl_deep_research: Conduct deep research on market topics

When analyzing markets or stocks:
1. Use firecrawl_search to find recent news and market data
2. Use firecrawl_scrape to get detailed information from financial websites
3. Use firecrawl_extract to pull structured data from earnings reports, SEC filings, etc.
4. Use firecrawl_deep_research for comprehensive analysis of market trends

Keep responses concise but informative. Focus on actionable insights backed by current data.`,
      model: 'gpt-4o',
      portfolioId: 'default-portfolio',
      enableFirecrawl: true,
      firecrawlMode: 'hosted', // Use hosted MCP for reliability
      ...config,
    });
  }

  /**
   * Implement the abstract analyze method
   */
  async analyze(request: AnalysisRequest): Promise<AnalysisResponse> {
    const startTime = Date.now();

    try {
      console.log(`🧠 Running ${request.analysisType} analysis...`);

      // Build the analysis prompt
      const prompt = this.buildAnalysisPrompt(request);

      // Save user request to conversation history
      await this.saveMessage(
        'user',
        `Analysis Request: ${request.analysisType} ${request.symbol ? `for ${request.symbol}` : ''}`
      );

      // Execute the analysis using the OpenAI Agent with MCP tools
      const result = await run(this.agent, prompt);

      if (!result.finalOutput) {
        throw new Error('No analysis output received');
      }

      // Save assistant response to conversation history
      await this.saveMessage('assistant', result.finalOutput);

      const executionTime = Date.now() - startTime;
      console.log(`✅ Analysis complete (${executionTime}ms)`);

      return {
        success: true,
        result: result.finalOutput,
        executionTime,
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      console.error(`❌ Analysis failed: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        executionTime,
      };
    }
  }

  /**
   * Pre-analysis - gather context and prepare for market analysis
   */
  async preAnalysis(): Promise<{ marketStatus: string; timestamp: Date }> {
    try {
      console.log('📊 Running pre-analysis...');

      const now = new Date();
      const marketHours = this.getMarketStatus(now);

      // Save pre-analysis context to conversation
      await this.saveMessage(
        'system',
        `Pre-analysis at ${now.toISOString()}: Market is ${marketHours}`
      );

      console.log(`📈 Market Status: ${marketHours}`);

      return {
        marketStatus: marketHours,
        timestamp: now,
      };
    } catch (error) {
      throw new AgentError(
        `Pre-analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'PRE_ANALYSIS_ERROR'
      );
    }
  }

  /**
   * Post-analysis - cleanup and summary
   */
  async postAnalysis(analysisResult: string): Promise<{ summary: string; nextSteps: string[] }> {
    try {
      console.log('📝 Running post-analysis...');

      // Generate summary and next steps
      const summary = `Analysis completed at ${new Date().toISOString()}. Generated ${analysisResult.length} characters of insights.`;

      const nextSteps = [
        'Monitor market conditions',
        'Review analysis recommendations',
        'Update portfolio positions if needed',
        'Schedule next analysis',
      ];

      // Save post-analysis summary
      await this.saveMessage('system', `Post-analysis: ${summary}`);

      console.log('✅ Post-analysis complete');

      return {
        summary,
        nextSteps,
      };
    } catch (error) {
      throw new AgentError(
        `Post-analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'POST_ANALYSIS_ERROR'
      );
    }
  }

  /**
   * Complete market open workflow - the main entry point
   */
  async runMarketOpenWorkflow(userPrompt?: string): Promise<{
    preAnalysis: any;
    analysis: string;
    postAnalysis: any;
  }> {
    try {
      console.log('🚀 Starting Market Open Workflow...');

      // Initialize agent with conversation history
      await this.initializeWithHistory();

      // Connect to MCP servers
      await this.connect();

      try {
        // Step 1: Pre-analysis
        const preAnalysis = await this.preAnalysis();

        // Step 2: Main analysis
        const prompt =
          userPrompt ||
          'Analyze current market conditions and provide trading insights for market open.';
        const analysisResult = await this.analyze({
          analysisType: 'market_open',
          parameters: { prompt },
        });

        if (!analysisResult.success) {
          throw new Error(analysisResult.error || 'Analysis failed');
        }

        // Step 3: Post-analysis
        const postAnalysis = await this.postAnalysis(analysisResult.result || '');

        console.log('🎉 Market Open Workflow Complete!');

        return {
          preAnalysis,
          analysis: analysisResult.result || '',
          postAnalysis,
        };
      } finally {
        // Always disconnect from MCP servers
        await this.disconnect();
      }
    } catch (error) {
      throw new AgentError(
        `Market open workflow failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'WORKFLOW_ERROR'
      );
    }
  }

  /**
   * Build analysis prompt with context
   */
  private buildAnalysisPrompt(request: AnalysisRequest): string {
    const context = this.buildAnalysisContext();
    const basePrompt = `Analysis Type: ${request.analysisType}${request.symbol ? `\nSymbol: ${request.symbol}` : ''}`;

    if (request.parameters?.['prompt']) {
      return `${context}\n\n${basePrompt}\n\nUser Request: ${request.parameters['prompt']}`;
    }

    return `${context}\n\n${basePrompt}\n\nPlease provide a comprehensive analysis using available web scraping tools to gather current market data.`;
  }

  /**
   * Build analysis context from conversation history
   */
  private buildAnalysisContext(): string {
    const recentMessages = this.conversationHistory.slice(0, 5); // Last 5 messages
    if (recentMessages.length === 0) {
      return 'Context: Starting fresh analysis session.';
    }

    const contextLines = recentMessages.map(msg => `${msg.role}: ${msg.content.slice(0, 200)}...`);
    return `Recent Context:\n${contextLines.join('\n')}`;
  }

  /**
   * Determine market status based on current time
   */
  private getMarketStatus(now: Date): string {
    const hour = now.getHours();
    const day = now.getDay(); // 0 = Sunday, 6 = Saturday

    // Weekend
    if (day === 0 || day === 6) {
      return 'closed (weekend)';
    }

    // Market hours: 9:30 AM - 4:00 PM ET (14:30 - 21:00 UTC)
    if (hour >= 9 && hour < 16) {
      return 'open';
    } else if (hour >= 4 && hour < 9) {
      return 'pre-market';
    } else {
      return 'after-hours';
    }
  }

  /**
   * Get agent status information
   */
  getStatus() {
    return {
      name: this.config.name,
      initialized: !!this.agentId,
      conversationId: this.conversationId,
      historyLength: this.conversationHistory.length,
      firecrawlEnabled: this.config.enableFirecrawl,
      mcpServersConnected: this.mcpServers.length,
    };
  }
}

// ============================================================================
// CONVENIENCE FUNCTIONS - For backward compatibility
// ============================================================================

// Create a default instance for simple usage
let defaultAgent: GeneralTradingAgent | null = null;

/**
 * Get or create the default agent instance
 */
export function getDefaultAgent(): GeneralTradingAgent {
  if (!defaultAgent) {
    defaultAgent = new GeneralTradingAgent();
  }
  return defaultAgent;
}

/**
 * Initialize the default agent
 */
export async function initializeAgent(): Promise<void> {
  const agent = getDefaultAgent();
  await agent.initializeWithHistory();
}

/**
 * Run market open workflow with the default agent
 */
export async function runMarketOpenWorkflow(userPrompt?: string): Promise<{
  preAnalysis: any;
  analysis: string;
  postAnalysis: any;
}> {
  const agent = getDefaultAgent();
  return agent.runMarketOpenWorkflow(userPrompt);
}

/**
 * Get agent status
 */
export function getAgentStatus() {
  if (!defaultAgent) {
    return { initialized: false };
  }
  return defaultAgent.getStatus();
}
