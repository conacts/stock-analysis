/**
 * Research Service - Enhanced with Zod Validation
 *
 * Manages research data collection using Firecrawl with strict type validation,
 * structured data extraction, and database storage.
 * Uses database schema as source of truth for all types.
 */

import { GeneralTradingAgent } from '@/agents/general-trading-agent';
import { db } from '@/db/connection';
import { researchSessions, researchData, marketOpenContexts } from '@/db/schema';
import type {
  ResearchType,
  SessionType,
  ResearchData as DbResearchData,
  ResearchSession as DbResearchSession,
} from '@/db/schema';
import type {
  ResearchRequest,
  ResearchSession,
  ExtractedData,
  ResearchResult,
} from '@/types/research';
import {
  FIRECRAWL_EXTRACTION_SCHEMAS,
  RESEARCH_EXTRACTION_SCHEMAS, // Legacy fallback
  MarketNewsSchema,
  EarningsSchema,
  EconomicIndicatorSchema,
  SectorAnalysisSchema,
} from '@/types/research';
import { eq, and, desc } from 'drizzle-orm';
import { z } from 'zod';

export class ResearchService {
  private agent: GeneralTradingAgent;

  constructor() {
    this.agent = new GeneralTradingAgent({
      enableFirecrawl: true,
      firecrawlMode: 'hosted',
    });
  }

  /**
   * Start a new research session and execute research requests
   */
  async startResearchSession(
    agentId: number,
    sessionType: SessionType,
    requests: ResearchRequest[]
  ): Promise<number> {
    try {
      console.log(`🔬 Starting research session: ${sessionType}`);

      // Create research session
      const [session] = await db
        .insert(researchSessions)
        .values({
          agentId,
          sessionType,
          status: 'in_progress',
        })
        .returning();

      const sessionId = session!.id;

      // Initialize agent
      await this.agent.initializeWithHistory();
      await this.agent.connect();

      try {
        // Execute research requests
        await this.executeResearchRequests(sessionId, requests);

        // Mark session as completed
        await db
          .update(researchSessions)
          .set({
            status: 'completed',
            completedAt: new Date(),
          })
          .where(eq(researchSessions.id, sessionId));

        console.log(`✅ Research session ${sessionId} completed`);
        return sessionId;
      } finally {
        await this.agent.disconnect();
      }
    } catch (error) {
      console.error('❌ Research session failed:', error);
      throw error;
    }
  }

  /**
   * Execute individual research requests with proper Firecrawl integration
   */
  private async executeResearchRequests(
    sessionId: number,
    requests: ResearchRequest[]
  ): Promise<void> {
    // Sort requests by priority (using ImpactLevel enum)
    const sortedRequests = requests.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });

    for (const request of sortedRequests) {
      await this.executeResearchRequest(sessionId, request);
    }
  }

  /**
   * Execute a single research request using Firecrawl with Zod validation
   */
  private async executeResearchRequest(sessionId: number, request: ResearchRequest): Promise<void> {
    try {
      console.log(`🔍 Executing research: ${request.type} ${request.symbol || ''}`);

      const zodSchema =
        FIRECRAWL_EXTRACTION_SCHEMAS[request.type as keyof typeof FIRECRAWL_EXTRACTION_SCHEMAS];
      if (!zodSchema) {
        throw new Error(`No Zod schema defined for research type: ${request.type}`);
      }

      // Build research prompt for Firecrawl with schema extraction
      const prompt = this.buildFirecrawlPrompt(request, zodSchema);

      // Execute research using the agent with MCP tools
      const result = await this.agent.analyze({
        analysisType: `firecrawl_research_${request.type}`,
        ...(request.symbol && { symbol: request.symbol }),
        parameters: {
          prompt,
          useFirecrawl: true,
          extractionSchema: zodSchema,
        },
      });

      if (!result.success) {
        throw new Error(result.error || 'Firecrawl research failed');
      }

      // Parse and validate extracted data using Zod
      const extractedData = this.parseAndValidateData(result.result!, request.type, zodSchema);

      // Store research result with enhanced metadata
      await this.storeResearchResult(sessionId, request, extractedData);

      console.log(`✅ Research completed: ${request.type}`);
    } catch (error) {
      console.error(`❌ Research failed for ${request.type}:`, error);

      // Store failed research with error info
      await this.storeResearchResult(
        sessionId,
        request,
        {
          error: error instanceof Error ? error.message : 'Unknown error',
          type: request.type,
        } as any,
        0
      );
    }
  }

  /**
   * Build Firecrawl-specific research prompt with Zod schema
   */
  private buildFirecrawlPrompt(request: ResearchRequest, zodSchema: z.ZodSchema): string {
    const basePrompt = `FIRECRAWL RESEARCH TASK: ${request.type.replace('_', ' ').toUpperCase()}

Use Firecrawl MCP tools to gather structured data for ${request.type.replace('_', ' ')}.

INSTRUCTIONS:
1. Use firecrawl_search to find relevant, recent sources
2. Use firecrawl_extract with the provided schema for structured data extraction
3. Focus on authoritative financial sources (Bloomberg, Reuters, SEC, company IR)
4. Extract data that strictly matches the required schema format

TARGET SEARCH CRITERIA:`;

    let specificCriteria = '';
    let searchQueries: string[] = [];

    switch (request.type) {
      case 'market_news':
        specificCriteria = `
- Recent market news from last 24 hours
- Major market-moving events and announcements
- Include sentiment and impact analysis
- Sources: Bloomberg, Reuters, CNBC, MarketWatch, WSJ`;
        searchQueries = [
          'breaking market news today',
          'stock market news today',
          'financial markets latest news',
        ];
        break;

      case 'earnings':
        specificCriteria = `
- Recent earnings reports and upcoming earnings
- Actual vs expected results with guidance updates
- Key metrics and management commentary
- Sources: company investor relations, SEC filings, earnings calls`;
        searchQueries = [
          `${request.symbol || 'major companies'} earnings report`,
          'quarterly earnings results',
          'earnings guidance updates',
        ];
        break;

      case 'economic_indicators':
        specificCriteria = `
- Latest economic data releases (CPI, GDP, employment, Fed statements)
- Market impact analysis and forecasts
- Federal Reserve policy implications
- Sources: Federal Reserve, BLS, Commerce Department, Treasury`;
        searchQueries = [
          'latest economic indicators',
          'Federal Reserve news',
          'CPI GDP employment data',
        ];
        break;

      case 'sector_analysis':
        specificCriteria = `
- Current sector performance and rotation signals
- Top/bottom performers with momentum analysis
- Sector-specific catalysts and headwinds
- Sources: sector ETFs, financial analysis, market data`;
        searchQueries = [
          'sector rotation analysis',
          'sector performance today',
          'industry momentum analysis',
        ];
        break;
    }

    const suggestedQueries = searchQueries.map(q => `- "${q}"`).join('\n');

    return `${basePrompt}${specificCriteria}

SUGGESTED SEARCH QUERIES:
${suggestedQueries}

EXTRACTION SCHEMA (ZOD):
${this.zodSchemaToJsonSchema(zodSchema)}

WORKFLOW:
1. Start with firecrawl_search using one of the suggested queries
2. Review search results and select 2-3 most relevant, recent sources
3. Use firecrawl_extract on selected sources with the schema above
4. Return ONLY the extracted structured data in the exact schema format
5. Ensure all required fields are populated with accurate data

CRITICAL: Your response must contain valid JSON that matches the schema exactly. Do not include analysis or commentary - only the structured data.`;
  }

  /**
   * Convert Zod schema to JSON schema for prompt
   */
  private zodSchemaToJsonSchema(zodSchema: z.ZodSchema): string {
    try {
      // This is a simplified conversion - in production, you might want to use a library like zod-to-json-schema
      const shape = (zodSchema as any)._def?.shape;
      if (!shape) return JSON.stringify({ type: 'object' }, null, 2);

      const properties: Record<string, any> = {};
      const required: string[] = [];

      for (const [key, value] of Object.entries(shape)) {
        const field = value as any;
        properties[key] = this.zodTypeToJsonType(field);

        if (!field.isOptional?.()) {
          required.push(key);
        }
      }

      return JSON.stringify(
        {
          type: 'object',
          properties,
          required,
        },
        null,
        2
      );
    } catch (error) {
      console.warn('Failed to convert Zod schema to JSON:', error);
      return JSON.stringify({ type: 'object' }, null, 2);
    }
  }

  /**
   * Convert individual Zod type to JSON schema type
   */
  private zodTypeToJsonType(zodType: any): any {
    const typeName = zodType._def?.typeName;

    switch (typeName) {
      case 'ZodString':
        return { type: 'string' };
      case 'ZodNumber':
        return { type: 'number' };
      case 'ZodBoolean':
        return { type: 'boolean' };
      case 'ZodArray':
        return {
          type: 'array',
          items: this.zodTypeToJsonType(zodType._def.type),
        };
      case 'ZodObject':
        return { type: 'object' };
      case 'ZodEnum':
        return {
          type: 'string',
          enum: zodType._def.values,
        };
      default:
        return { type: 'string' };
    }
  }

  /**
   * Parse and validate extracted data using Zod schemas
   */
  private parseAndValidateData(
    response: string,
    type: ResearchType,
    zodSchema: z.ZodSchema
  ): ExtractedData {
    try {
      // Try to find JSON in the response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('No JSON data found in response');
      }

      const rawData = JSON.parse(jsonMatch[0]);

      // Validate using Zod schema
      const validatedData = zodSchema.parse(rawData);

      console.log(`✅ Data validation successful for ${type}`);
      return validatedData as ExtractedData;
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error(`❌ Zod validation failed for ${type}:`, error.errors);
        throw new Error(
          `Data validation failed: ${error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')}`
        );
      }

      console.error('Failed to parse extracted data:', error);
      throw new Error(
        `Failed to parse ${type} data: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * Store research result in database with enhanced metadata
   */
  private async storeResearchResult(
    sessionId: number,
    request: ResearchRequest,
    extractedData: ExtractedData,
    confidence: number = 85
  ): Promise<void> {
    // Extract sentiment and impact from the data if available
    const sentiment = (extractedData as any).sentiment || null;
    const impact = (extractedData as any).impact || request.priority;

    await db.insert(researchData).values({
      sessionId,
      researchType: request.type,
      symbol: request.symbol,
      extractedData: extractedData as any, // JSONB storage
      confidence,
      sentiment,
      impact,
    });
  }

  /**
   * Get research results for a session
   */
  async getSessionResults(sessionId: number): Promise<ResearchResult[]> {
    const results = await db
      .select()
      .from(researchData)
      .where(eq(researchData.sessionId, sessionId))
      .orderBy(desc(researchData.createdAt));

    return results.map(result => ({
      id: result.id,
      sessionId: result.sessionId,
      researchType: result.researchType as ResearchType,
      ...(result.symbol && { symbol: result.symbol }),
      ...(result.sourceUrl && { sourceUrl: result.sourceUrl }),
      extractedData: result.extractedData as ExtractedData,
      ...(result.confidence && { confidence: result.confidence }),
      ...(result.sentiment && { sentiment: result.sentiment }),
      ...(result.impact && { impact: result.impact }),
      ...(result.createdAt && { createdAt: result.createdAt }),
    }));
  }

  /**
   * Build market context from research session
   */
  async buildMarketContext(sessionId: number): Promise<string> {
    const results = await this.getSessionResults(sessionId);

    if (results.length === 0) {
      return 'No research data available for market context.';
    }

    const contextSections: string[] = [];

    // Group results by type
    const groupedResults = results.reduce(
      (acc, result) => {
        if (!acc[result.researchType]) acc[result.researchType] = [];
        acc[result.researchType].push(result);
        return acc;
      },
      {} as Record<ResearchType, ResearchResult[]>
    );

    // Build context sections
    Object.entries(groupedResults).forEach(([type, typeResults]) => {
      const section = this.buildContextSection(type as ResearchType, typeResults);
      if (section) contextSections.push(section);
    });

    return `MARKET RESEARCH CONTEXT (Session ${sessionId}):

${contextSections.join('\n\n')}

Total Research Items: ${results.length}
Research Session Completed: ${new Date().toISOString()}`;
  }

  /**
   * Build context section for specific research type
   */
  private buildContextSection(type: ResearchType, results: ResearchResult[]): string {
    if (results.length === 0) return '';

    const title = type.replace('_', ' ').toUpperCase();
    const items = results
      .map(result => {
        const data = result.extractedData;

        switch (type) {
          case 'market_news':
            const news = data as any;
            return `• ${news.headline || 'No headline'} (${news.sentiment || 'unknown'}) - ${news.impact || 'unknown'} impact`;
          case 'earnings':
            const earnings = data as any;
            return `• ${earnings.symbol || 'Unknown'}: ${earnings.companyName || 'Unknown'} reporting ${earnings.reportDate || 'N/A'}`;
          case 'economic_indicators':
            const indicator = data as any;
            return `• ${indicator.indicator || 'Unknown'}: ${indicator.value || 'N/A'} (${indicator.impact || 'unknown'} impact)`;
          case 'sector_analysis':
            const sector = data as any;
            const performance = sector.performance?.oneDay || 'N/A';
            return `• ${sector.sector || 'Unknown'}: ${sector.momentum || 'unknown'} momentum (${performance}% today)`;
          default:
            return `• ${JSON.stringify(data).slice(0, 100)}...`;
        }
      })
      .join('\n');

    return `${title}:\n${items}`;
  }

  /**
   * Create default market open research session
   */
  static createMarketOpenResearchSession(): ResearchSession {
    return {
      sessionType: 'market_open',
      requests: [
        {
          type: 'market_news',
          priority: 'high',
          maxResults: 10,
        },
        {
          type: 'economic_indicators',
          priority: 'high',
          maxResults: 5,
        },
        {
          type: 'sector_analysis',
          priority: 'medium',
          maxResults: 11, // All major sectors
        },
      ],
      maxConcurrency: 3,
      timeoutMs: 300000, // 5 minutes
    };
  }
}
