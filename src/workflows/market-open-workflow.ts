/**
 * Market Open Workflow
 *
 * Simple workflow that runs our GeneralTradingAgent for market open analysis.
 * This is concrete and testable - we learn what works by using it.
 */

import { logger, task } from '@trigger.dev/sdk/v3';
import { runMarketOpenWorkflow, getAgentStatus } from '@/agents/general-trading-agent';

export const marketOpenAnalysis = task({
  id: 'market-open-analysis',
  run: async (payload: { userPrompt?: string } = {}) => {
    logger.info('🚀 Starting Market Open Analysis Workflow');

    try {
      // Run the complete market open workflow
      const result = await runMarketOpenWorkflow(payload.userPrompt);

      // Get agent status for logging
      const agentStatus = getAgentStatus();

      logger.info('📊 Market Open Analysis Results', {
        agentStatus,
        preAnalysis: result.preAnalysis,
        analysisLength: result.analysis.length,
        postAnalysis: result.postAnalysis,
      });

      return {
        success: true,
        timestamp: new Date().toISOString(),
        agent: agentStatus,
        results: {
          marketStatus: result.preAnalysis.marketStatus,
          analysis: result.analysis,
          summary: result.postAnalysis.summary,
          nextSteps: result.postAnalysis.nextSteps,
        },
      };
    } catch (error) {
      logger.error('❌ Market Open Analysis Failed', {
        error: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
      });

      return {
        success: false,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  },
});

// Manual test function for development
export async function testMarketOpenWorkflow(userPrompt?: string) {
  console.log('🧪 Testing Market Open Workflow...');

  try {
    const result = await runMarketOpenWorkflow(userPrompt);

    console.log('\n📊 RESULTS:');
    console.log('Pre-Analysis:', result.preAnalysis);
    console.log('\nAnalysis:', result.analysis);
    console.log('\nPost-Analysis:', result.postAnalysis);

    const status = getAgentStatus();
    console.log('\n🤖 Agent Status:', status);

    return result;
  } catch (error) {
    console.error('❌ Test failed:', error);
    throw error;
  }
}
