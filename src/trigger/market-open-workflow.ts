/**
 * Market Open Workflow - Enhanced with Firecrawl Research Pipeline
 *
 * This workflow collects structured market data using Firecrawl,
 * stores it in the database, and uses it as context for comprehensive market analysis.
 */

import { task } from '@trigger.dev/sdk/v3';
import { run } from '@openai/agents';
import { GeneralTradingAgent } from '@/agents/general-trading-agent';
import { ResearchService } from '@/services/research-service';
import { db } from '@/db/connection';
import { agents, analysisResults } from '@/db/schema';
import { eq } from 'drizzle-orm';

export const marketOpenWorkflow = task({
  id: 'market-open-workflow',
  run: async (payload: { agentName?: string; customPrompt?: string }) => {
    const startTime = Date.now();

    try {
      console.log('🌅 Starting Market Open Workflow with Enhanced Research Pipeline');
      console.log('=================================================================');

      // Step 1: Get or create agent
      const agent = await getOrCreateAgent(payload.agentName || 'MarketOpenAgent');
      if (!agent) {
        throw new Error('Failed to get or create agent');
      }
      const agentId = agent.id;

      console.log(`📊 Using agent: ${agent.name} (ID: ${agentId})`);

      // Step 2: Execute Research Phase
      console.log('\n🔬 PHASE 1: RESEARCH DATA COLLECTION');
      console.log('───────────────────────────────────────');

      const researchService = new ResearchService();
      const researchSession = ResearchService.createMarketOpenResearchSession();

      const sessionId = await researchService.startResearchSession(
        agentId,
        researchSession.sessionType,
        researchSession.requests
      );

      console.log(`✅ Research session ${sessionId} completed`);

      // Step 3: Build Context from Research
      console.log('\n📋 PHASE 2: CONTEXT PREPARATION');
      console.log('──────────────────────────────────────');

      const marketContext = await researchService.buildMarketContext(sessionId);
      console.log(`📄 Built market context (${marketContext.length} characters)`);

      // Step 4: Market Analysis with OpenAI Agents run()
      console.log('\n🧠 PHASE 3: AI MARKET ANALYSIS');
      console.log('─────────────────────────────────────');

      const tradingAgent = new GeneralTradingAgent({
        enableFirecrawl: true,
        firecrawlMode: 'hosted',
      });

      // Initialize agent with conversation history
      await tradingAgent.initializeWithHistory();

      const analysisPrompt = buildAnalysisPrompt(marketContext, payload.customPrompt);

      // Use OpenAI Agents run() function for proper trace context
      console.log('🚀 Starting market analysis with OpenAI Agents run()...');

      const agentResult = await run(tradingAgent.getAgent(), analysisPrompt, {
        stream: false, // We'll add streaming later
      });

      const analysis = agentResult.finalOutput || 'Analysis completed but no output received';

      console.log(`✅ Analysis completed (${analysis.length} characters)`);

      // Step 5: Store Results
      console.log('\n💾 PHASE 4: STORING RESULTS');
      console.log('───────────────────────────────────');

      await db.insert(analysisResults).values({
        agentId: agentId,
        analysisType: 'market_open_comprehensive',
        result: analysis,
        success: true,
      });

      console.log('✅ Results stored to database');

      // Step 6: Summary and Metrics
      const executionTime = Date.now() - startTime;
      const researchResults = await researchService.getSessionResults(sessionId);

      console.log('\n📊 WORKFLOW SUMMARY');
      console.log('══════════════════════════════════════');
      console.log(`⏱️  Execution Time: ${(executionTime / 1000).toFixed(2)}s`);
      console.log(`🔬 Research Items: ${researchResults.length}`);
      console.log(`📄 Context Length: ${marketContext.length} chars`);
      console.log(`📝 Analysis Length: ${analysis.length} chars`);
      console.log(`💾 Session ID: ${sessionId}`);

      return {
        success: true,
        sessionId,
        agentId,
        analysis,
        researchItemsCount: researchResults.length,
        executionTime,
        contextLength: marketContext.length,
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      console.error('❌ Market Open Workflow failed:', error);

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        executionTime,
      };
    }
  },
});

/**
 * Get existing agent or create new one
 */
async function getOrCreateAgent(name: string) {
  // Try to find existing agent
  const existingAgent = await db.select().from(agents).where(eq(agents.name, name)).limit(1);

  if (existingAgent.length > 0) {
    return existingAgent[0];
  }

  // Create new agent
  const [newAgent] = await db
    .insert(agents)
    .values({
      name,
      instructions: `You are a sophisticated market analysis agent specializing in pre-market and market open analysis. 

You have access to comprehensive research data collected through Firecrawl including:
- Real-time market news with sentiment analysis
- Economic indicators and their market impact
- Sector performance and rotation signals
- Earnings data and corporate events

Your analysis should be:
1. Data-driven using the provided research context
2. Actionable with specific insights and implications
3. Risk-aware highlighting potential market risks
4. Forward-looking with trading considerations

Always reference specific data points from the research context to support your analysis.`,
      model: 'gpt-4o',
    })
    .returning();

  return newAgent!;
}

/**
 * Build comprehensive analysis prompt with research context
 */
function buildAnalysisPrompt(marketContext: string, customPrompt?: string): string {
  const basePrompt = `MARKET OPEN ANALYSIS REQUEST

You are conducting a comprehensive market open analysis based on fresh research data collected through Firecrawl.

RESEARCH CONTEXT:
${marketContext}

ANALYSIS REQUIREMENTS:
1. **Market Sentiment Assessment**
   - Overall market direction and sentiment
   - Key sentiment drivers from the research data
   - Sector rotation signals

2. **Economic Impact Analysis** 
   - Impact of economic indicators on market outlook
   - Federal Reserve policy implications
   - Economic headwinds and tailwinds

3. **News Impact Assessment**
   - Market-moving news events and their implications
   - Earnings results and guidance impact
   - Geopolitical or macro events

4. **Sector Analysis**
   - Strongest and weakest performing sectors
   - Sector rotation opportunities
   - Key sector-specific catalysts

5. **Trading Considerations**
   - Key levels to watch (support/resistance)
   - Risk factors to monitor
   - Potential trading opportunities

6. **Risk Assessment**
   - Current market risks
   - Volatility expectations
   - Defensive considerations

Please provide a comprehensive, structured analysis that references specific data points from the research context. Be specific and actionable in your recommendations.`;

  if (customPrompt) {
    return `${basePrompt}

ADDITIONAL CONTEXT OR FOCUS:
${customPrompt}`;
  }

  return basePrompt;
}

/**
 * Test function for development - manually calls the task logic
 */
export async function testMarketOpenWorkflow(customPrompt?: string) {
  console.log('🧪 Testing Market Open Workflow...');

  try {
    // Manually call the task run function instead of using .run()
    const startTime = Date.now();

    console.log('🌅 Starting Market Open Workflow with Enhanced Research Pipeline');
    console.log('=================================================================');

    // Step 1: Get or create agent
    const agent = await getOrCreateAgent('TestMarketAgent');
    if (!agent) {
      throw new Error('Failed to get or create agent');
    }
    const agentId = agent.id;

    console.log(`📊 Using agent: ${agent.name} (ID: ${agentId})`);

    // Step 2: Execute Research Phase
    console.log('\n🔬 PHASE 1: RESEARCH DATA COLLECTION');
    console.log('───────────────────────────────────────');

    const researchService = new ResearchService();
    const researchSession = ResearchService.createMarketOpenResearchSession();

    const sessionId = await researchService.startResearchSession(
      agentId,
      researchSession.sessionType,
      researchSession.requests
    );

    console.log(`✅ Research session ${sessionId} completed`);

    // Step 3: Build Context from Research
    console.log('\n📋 PHASE 2: CONTEXT PREPARATION');
    console.log('──────────────────────────────────────');

    const marketContext = await researchService.buildMarketContext(sessionId);
    console.log(`📄 Built market context (${marketContext.length} characters)`);

    const result = {
      success: true,
      sessionId,
      agentId,
      analysis: 'Test analysis completed - research phase working',
      researchItemsCount: (await researchService.getSessionResults(sessionId)).length,
      executionTime: Date.now() - startTime,
      contextLength: marketContext.length,
    };

    console.log('✅ Test completed:', result);
    return result;
  } catch (error) {
    console.error('❌ Test failed:', error);
    throw error;
  }
}
