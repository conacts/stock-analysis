import { task } from '@trigger.dev/sdk/v3';
import { DeepSeekClient } from '../../clients/deepseek';
import { AlpacaClient } from '../../clients/alpaca';
import { DailyAnalysisSchema } from '../../database/models';
import { DailyAnalysis } from '../../database/models';

export const aiTradingAnalysis = task({
  id: 'ai-trading-analysis',
  maxDuration: 300, // 5 minutes - no more timeout issues!
  run: async (payload: { symbol: string; portfolioId?: string }) => {
    console.log(`🤖 Starting AI analysis for ${payload.symbol}`);

    try {
      // Initialize clients
      const deepseek = new DeepSeekClient();
      const alpaca = new AlpacaClient();

      // Get market data
      console.log(`📊 Fetching market data for ${payload.symbol}`);
      const bars = await alpaca.getLatestBars([payload.symbol]);
      const marketData = bars.bars[payload.symbol] || { c: 0, v: 0 }; // fallback data

      // Get recent news (mock for now - you can integrate a real news API)
      const newsData = [
        {
          title: `${payload.symbol} Market Update`,
          summary: 'Recent market developments and analysis',
          date: new Date().toISOString(),
        },
      ];

      // Prepare analysis data
      const financialData = {
        symbol: payload.symbol,
        current_price: marketData.c || 0, // close price
        volume: marketData.v || 0, // volume
        market_cap: 0, // Would come from financial data API
      };

      const technicalData = {
        rsi: 65.5, // Would come from technical analysis
        moving_averages: {
          sma_20: 150.0,
          sma_50: 145.0,
        },
      };

      const marketContext = {
        market_trend: 'bullish',
        sector_performance: 'positive',
        economic_indicators: 'stable',
      };

      // Perform AI analysis using our TypeScript DeepSeek client
      console.log(`🧠 Running DeepSeek analysis for ${payload.symbol}`);
      const analysis = await deepseek.analyzeStockComprehensive(
        payload.symbol,
        financialData,
        newsData,
        technicalData,
        marketContext
      );

      // Store analysis in database
      const analysisData: DailyAnalysis = {
        symbol: payload.symbol,
        analysis_date: new Date().toISOString(),
        analysis_data: {
          news_sentiment: analysis.key_points,
          ai_recommendation: analysis,
          timestamp: new Date().toISOString(),
          confidence: analysis.confidence || 0.5,
          reasoning: analysis.analysis || 'AI analysis completed',
        },
      };

      // Validate the analysis data
      const validatedData = DailyAnalysisSchema.parse(analysisData);

      console.log('✅ Analysis completed successfully:');
      console.log(`🎯 Symbol: ${payload.symbol}`);
      console.log(`📊 Analysis Data: ${JSON.stringify(validatedData.analysis_data, null, 2)}`);

      return {
        success: true,
        symbol: payload.symbol,
        analysis: validatedData,
        ai_cost: deepseek.getCostSummary().total_cost_usd,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error(`❌ Error in AI analysis for ${payload.symbol}:`, error);

      return {
        success: false,
        symbol: payload.symbol,
        error: error instanceof Error ? error.message : 'Unknown error',
        execution_time: new Date().toISOString(),
      };
    }
  },
});
