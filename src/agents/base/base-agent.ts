/**
 * Base Trading Agent Class
 *
 * Simple foundation for trading agents wrapping OpenAI Agents SDK.
 * Type safety ensures valid configurations.
 */

import { Agent, run, MCPServerStdio, MCPServerStreamableHttp, hostedMcpTool } from '@openai/agents';
import type { MarketContext, PortfolioContext, UserPreferences } from '@/types/context';
import { AgentError } from '@/types/errors';
import { db } from '@/db/connection';
import { agents, conversations, conversationMessages } from '@/db/schema';
import type { ConversationMessage } from '@/db/schema';
import { eq, desc } from 'drizzle-orm';
import { FIRECRAWL_API_KEY } from '@/config/environment';

export interface BaseAgentConfig {
  name: string;
  instructions: string;
  model?: string;
  temperature?: number;
  portfolioId?: string; // For agent-portfolio relationship
  enableFirecrawl?: boolean;
  firecrawlMode?: 'hosted' | 'streamable' | 'stdio';
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

export interface ErrorContext {
  agentName: string;
  operation: string;
  timestamp: Date;
  request?: AnalysisRequest;
  context?: {
    market?: boolean;
    portfolio?: boolean;
    preferences?: boolean;
  };
}

export abstract class BaseAgent {
  protected agent: Agent;
  protected mcpServers: (MCPServerStdio | MCPServerStreamableHttp)[] = [];
  protected config: BaseAgentConfig;

  // Database IDs for persistence
  protected agentId?: number;
  protected conversationId?: number;

  // Optional context
  protected marketContext?: MarketContext;
  protected portfolioContext?: PortfolioContext;
  protected userPreferences?: UserPreferences;

  // Conversation history
  protected conversationHistory: ConversationMessage[] = [];

  constructor(config: BaseAgentConfig) {
    this.config = config;

    const tools = [];
    const mcpServers = [];

    // Add Firecrawl MCP integration if enabled
    if (config.enableFirecrawl && FIRECRAWL_API_KEY) {
      const mode = config.firecrawlMode || 'hosted';

      switch (mode) {
        case 'hosted':
          // Use remote hosted Firecrawl MCP server (recommended for production)
          tools.push(
            hostedMcpTool({
              serverLabel: 'firecrawl',
              serverUrl: `https://mcp.firecrawl.dev/${FIRECRAWL_API_KEY}/sse`,
            })
          );
          break;
      }
    }

    this.agent = new Agent({
      name: config.name,
      instructions: config.instructions,
      model: config.model || 'gpt-4o',
      tools,
      mcpServers,
    });

    this.mcpServers = mcpServers;

    try {
      // Initialize OpenAI Agent with validation
      this.validateConfig(config);
    } catch (error) {
      throw new AgentError(
        `Agent initialization failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        config.name,
        'AGENT_INITIALIZATION_ERROR'
      );
    }
  }

  // ============================================================================
  // CONFIGURATION VALIDATION
  // ============================================================================

  private validateConfig(config: BaseAgentConfig): void {
    if (!config.name || config.name.trim().length === 0)
      throw new Error('Agent name is required and cannot be empty');
    if (!config.instructions || config.instructions.trim().length === 0)
      throw new Error('Agent instructions are required and cannot be empty');
    if (config.temperature !== undefined && (config.temperature < 0 || config.temperature > 2))
      throw new Error('Temperature must be between 0 and 2');
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
    try {
      this.validateMarketContext(context);
      this.marketContext = context;
    } catch (error) {
      throw new AgentError(
        `Failed to update market context: ${error instanceof Error ? error.message : 'Invalid context'}`,
        this.config.name,
        'CONTEXT_UPDATE_ERROR'
      );
    }
  }

  public updatePortfolioContext(context: PortfolioContext): void {
    try {
      this.validatePortfolioContext(context);
      this.portfolioContext = context;
    } catch (error) {
      throw new AgentError(
        `Failed to update portfolio context: ${error instanceof Error ? error.message : 'Invalid context'}`,
        this.config.name,
        'CONTEXT_UPDATE_ERROR'
      );
    }
  }

  public updateUserPreferences(preferences: UserPreferences): void {
    try {
      this.validateUserPreferences(preferences);
      this.userPreferences = preferences;
    } catch (error) {
      throw new AgentError(
        `Failed to update user preferences: ${error instanceof Error ? error.message : 'Invalid preferences'}`,
        this.config.name,
        'CONTEXT_UPDATE_ERROR'
      );
    }
  }

  // ============================================================================
  // CONTEXT VALIDATION
  // ============================================================================

  private validateMarketContext(context: MarketContext): void {
    if (!context || typeof context !== 'object')
      throw new Error('Market context must be a valid object');
  }

  private validatePortfolioContext(context: PortfolioContext): void {
    if (!context || typeof context !== 'object')
      throw new Error('Portfolio context must be a valid object');
  }

  private validateUserPreferences(preferences: UserPreferences): void {
    if (!preferences || typeof preferences !== 'object')
      throw new Error('User preferences must be a valid object');
  }

  // ============================================================================
  // CONVERSATION HISTORY MANAGEMENT
  // ============================================================================

  /**
   * Initialize or load agent from database with conversation history
   */
  public async initializeWithHistory(): Promise<void> {
    try {
      // Try to find existing agent by name and portfolio
      const existingAgent = await db
        .select()
        .from(agents)
        .where(eq(agents.name, this.config.name))
        .limit(1);

      if (existingAgent.length > 0) {
        // Load existing agent
        this.agentId = existingAgent[0]!.id;
        await this.loadConversationHistory();
      } else {
        // Create new agent
        await this.createAgentInDatabase();
        await this.initializeConversation();
      }
    } catch (error) {
      throw new AgentError(
        `Failed to initialize agent with history: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'INITIALIZATION_ERROR'
      );
    }
  }

  /**
   * Load conversation history for this agent
   */
  protected async loadConversationHistory(): Promise<void> {
    if (!this.agentId) {
      throw new Error('Agent ID is required to load conversation history');
    }

    try {
      // Find the conversation for this agent
      const conversation = await db
        .select()
        .from(conversations)
        .where(eq(conversations.agentId, this.agentId))
        .limit(1);

      if (conversation.length === 0) {
        // No conversation exists, create one
        await this.initializeConversation();
        return;
      }

      this.conversationId = conversation[0]!.id;

      // Load all messages for this conversation
      this.conversationHistory = await db
        .select()
        .from(conversationMessages)
        .where(eq(conversationMessages.conversationId, this.conversationId))
        .orderBy(desc(conversationMessages.timestamp));

      console.log(
        `Loaded ${this.conversationHistory.length} messages for agent ${this.config.name}`
      );
    } catch (error) {
      throw new AgentError(
        `Failed to load conversation history: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'HISTORY_LOAD_ERROR'
      );
    }
  }

  /**
   * Save a message to the conversation history
   */
  protected async saveMessage(
    role: 'user' | 'assistant' | 'system',
    content: string
  ): Promise<void> {
    if (!this.conversationId) {
      throw new Error('Conversation ID is required to save messages');
    }

    try {
      const [savedMessage] = await db
        .insert(conversationMessages)
        .values({
          conversationId: this.conversationId,
          role,
          content,
        })
        .returning();

      // Add to local history
      if (savedMessage) {
        this.conversationHistory.unshift(savedMessage);
      }
    } catch (error) {
      throw new AgentError(
        `Failed to save message: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'MESSAGE_SAVE_ERROR'
      );
    }
  }

  /**
   * Create agent record in database
   */
  private async createAgentInDatabase(): Promise<void> {
    try {
      const [newAgent] = await db
        .insert(agents)
        .values({
          name: this.config.name,
          instructions: this.config.instructions,
          model: this.config.model || 'o3',
          portfolioId: this.config.portfolioId,
        })
        .returning();

      this.agentId = newAgent!.id;
    } catch (error) {
      throw new AgentError(
        `Failed to create agent in database: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'AGENT_CREATION_ERROR'
      );
    }
  }

  /**
   * Initialize conversation for this agent
   */
  private async initializeConversation(): Promise<void> {
    if (!this.agentId) {
      throw new Error('Agent ID is required to initialize conversation');
    }

    try {
      const [newConversation] = await db
        .insert(conversations)
        .values({
          agentId: this.agentId,
        })
        .returning();

      this.conversationId = newConversation!.id;
      this.conversationHistory = [];

      // Add initial system message
      await this.saveMessage('system', this.config.instructions);
    } catch (error) {
      throw new AgentError(
        `Failed to initialize conversation: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'CONVERSATION_INIT_ERROR'
      );
    }
  }

  /**
   * Get conversation history formatted for OpenAI
   */
  protected getFormattedHistory(): Array<{ role: string; content: string }> {
    return this.conversationHistory
      .slice()
      .reverse() // Reverse to get chronological order
      .map(msg => ({
        role: msg.role,
        content: msg.content,
      }));
  }

  // ============================================================================
  // ANALYSIS EXECUTION WITH ERROR HANDLING
  // ============================================================================

  protected async executeAnalysis(prompt: string): Promise<string> {
    try {
      this.validatePrompt(prompt);

      // Save user message to conversation history
      await this.saveMessage('user', prompt);

      // Build prompt with conversation history
      const conversationHistory = this.getFormattedHistory();
      const fullPrompt =
        conversationHistory.length > 1
          ? `${conversationHistory.map(msg => `${msg.role}: ${msg.content}`).join('\n\n')}\n\nuser: ${prompt}`
          : prompt;

      const result = await run(this.agent, fullPrompt);

      if (!result.finalOutput) {
        throw new Error('No analysis output received from agent');
      }

      // Save assistant response to conversation history
      await this.saveMessage('assistant', result.finalOutput);

      return result.finalOutput;
    } catch (error) {
      throw new AgentError(
        `Analysis execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        this.config.name,
        'ANALYSIS_EXECUTION_ERROR'
      );
    }
  }

  // ============================================================================
  // ERROR HANDLING UTILITIES
  // ============================================================================

  private validatePrompt(prompt: string): void {
    if (!prompt || prompt.trim().length === 0) throw new Error('Prompt cannot be empty');
    if (prompt.length > 32000) throw new Error('Prompt exceeds maximum length limit');
  }

  /**
   * Connect to all MCP servers
   */
  async connect(): Promise<void> {
    await Promise.all(this.mcpServers.map(server => server.connect()));
  }

  /**
   * Disconnect from all MCP servers
   */
  async disconnect(): Promise<void> {
    await Promise.all(this.mcpServers.map(server => server.close()));
  }

  /**
   * Get the underlying OpenAI Agent instance
   */
  getAgent(): Agent {
    return this.agent;
  }

  /**
   * Invalidate MCP tools cache (useful when tools might have changed)
   */
  invalidateToolsCache(): void {
    this.mcpServers.forEach(server => {
      if ('invalidateToolsCache' in server && typeof server.invalidateToolsCache === 'function') {
        (server as any).invalidateToolsCache();
      }
    });
  }
}
