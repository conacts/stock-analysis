import { schedules } from '@trigger.dev/sdk/v3';
import { AlpacaClient } from '../../clients/alpaca';
// import { DeepSeekClient } from "../../clients/deepseek"; // TODO: Will use this for AI analysis

export const marketOpeningAnalysis = schedules.task({
  id: 'market-opening-analysis',
  // Run every weekday at 9:30am ET (markets open)
  // 13:30 UTC = 9:30am EDT / 8:30am EST
  cron: '30 13 * * 1-5',
  maxDuration: 300, // 5 minutes
  run: async () => {
    console.log('🔔 Market Opening Analysis Started');
    console.log(`📅 Timestamp: ${new Date().toISOString()}`);
    console.log(`🌍 Timezone: ${Intl.DateTimeFormat().resolvedOptions().timeZone}`);

    const analysis = {
      timestamp: new Date().toISOString(),
      market_session: 'market_open',
      status: 'started',
      symbols_analyzed: [] as string[],
      recommendations: [] as string[],
      errors: [] as string[],
    };

    try {
      // Initialize clients
      const alpaca = new AlpacaClient();
      // const deepseek = new DeepSeekClient(); // TODO: Will use this for analysis

      // Check market clock (closest thing to market status)
      const marketClock = await alpaca.getMarketClock();
      console.log(`📊 Market Status: ${marketClock.is_open ? 'OPEN' : 'CLOSED'}`);
      console.log(`⏰ Next Open: ${marketClock.next_open}`);
      console.log(`⏰ Next Close: ${marketClock.next_close}`);

      if (!marketClock.is_open) {
        console.log('⚠️ Markets are closed - skipping analysis');
        return {
          success: true,
          message: 'Markets closed - analysis skipped',
          market_clock: marketClock,
          analysis,
        };
      }

      // Get account info
      const account = await alpaca.getAccount();
      console.log(`💰 Portfolio Value: $${Number(account.portfolio_value).toLocaleString()}`);
      console.log(`💵 Buying Power: $${Number(account.buying_power).toLocaleString()}`);

      // TODO: Add pre-market analysis logic here
      console.log('🚀 Market opening analysis framework ready!');
      console.log('📈 Next: Add stock screening, news analysis, and trading signals');

      analysis.status = 'completed';

      return {
        success: true,
        message: 'Market opening analysis completed successfully',
        market_clock: marketClock,
        account_info: {
          portfolio_value: account.portfolio_value,
          buying_power: account.buying_power,
        },
        analysis,
      };
    } catch (error) {
      console.error('❌ Market opening analysis failed:', error);
      analysis.status = 'failed';
      analysis.errors.push(error instanceof Error ? error.message : 'Unknown error');

      return {
        success: false,
        message: 'Market opening analysis failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        analysis,
      };
    }
  },
});
