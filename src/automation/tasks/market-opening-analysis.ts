import { schedules } from '@trigger.dev/sdk/v3';
import { AlpacaClient } from '../../clients/alpaca';
import { db } from '../../database/connection';
import { SimplePortfolio, AIAgent } from '../../database/models';
// import { DeepSeekClient } from "../../clients/deepseek"; // TODO: Will use this for AI analysis
// import { portfolioAnalysisTask } from './portfolio-analysis'; // TODO: Create this task

export const marketOpeningAnalysis = schedules.task({
  id: 'market-opening-analysis',
  // Run at 9:30 AM ET (13:30 UTC) on weekdays when markets open
  cron: '30 13 * * 1-5',
  maxDuration: 300,
  run: async () => {
    console.log('🌅 Market Opening Analysis - Starting...');

    try {
      // Initialize Alpaca client to check market status
      const alpaca = new AlpacaClient();

      // Check if markets are open
      console.log('📊 Checking market status...');
      const marketClock = await alpaca.getMarketClock();

      if (!marketClock.is_open) {
        console.log('🔒 Markets are closed. Skipping analysis.');
        return {
          success: true,
          message: 'Markets closed - analysis skipped',
          timestamp: new Date().toISOString(),
        };
      }

      console.log('✅ Markets are open! Proceeding with portfolio analysis...');

      // Get all active portfolios from database
      console.log('📋 Fetching active portfolios...');
      const portfoliosResult = await db.query<SimplePortfolio>(
        'SELECT * FROM portfolios WHERE status = $1',
        ['active']
      );

      if (!portfoliosResult.success || !portfoliosResult.data?.length) {
        console.log('⚠️ No active portfolios found');
        return {
          success: true,
          message: 'No active portfolios to analyze',
          timestamp: new Date().toISOString(),
        };
      }

      const portfolios = portfoliosResult.data;
      console.log(`🎯 Found ${portfolios.length} active portfolios to analyze`);

      // TODO: Trigger individual portfolio analysis tasks for each portfolio
      for (const portfolio of portfolios) {
        console.log(`📈 Would analyze portfolio: ${portfolio.name} (ID: ${portfolio.id})`);

        // Get the AI agent for this portfolio
        if (portfolio.agent_id) {
          const agentResult = await db.query<AIAgent>(
            'SELECT * FROM ai_agents WHERE id = $1 AND status = $2',
            [portfolio.agent_id, 'active']
          );

          if (agentResult.success && agentResult.data?.length) {
            const agent = agentResult.data[0];
            console.log(`🤖 Using AI Agent: ${agent?.name} for portfolio ${portfolio.name}`);
          }
        }

        // TODO: Here we would trigger individual analysis tasks
        // await triggerPortfolioAnalysis({ portfolioId: portfolio.id, agentId: portfolio.agent_id });
      }

      console.log('✅ Market opening analysis completed successfully');

      return {
        success: true,
        message: 'Portfolio analyses triggered successfully',
        portfolios_count: portfolios.length,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('❌ Error in market opening analysis:', error);

      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      };
    }
  },
});
