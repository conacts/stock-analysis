import { task } from "@trigger.dev/sdk/v3";
import { DeepSeekClient } from "../../clients/deepseek";
import { AlpacaClient } from "../../clients/alpaca";
import { db } from "../../database/connection";
import { DailyAnalysisSchema } from "../../database/models";

export const aiTradingAnalysis = task({
	id: "ai-trading-analysis",
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
					summary: "Recent market developments and analysis",
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
				market_trend: "bullish",
				sector_performance: "positive",
				economic_indicators: "stable",
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

			// Save analysis to database
			const analysisData = {
				symbol: payload.symbol,
				date: new Date().toISOString(),
				composite_score: analysis.confidence / 10, // Convert to 0-10 scale
				rating: analysis.recommendation,
				confidence: analysis.confidence.toString(),
				analysis_data: {
					analysis: analysis.analysis,
					key_points: analysis.key_points,
					risk_assessment: analysis.risk_assessment,
					price_target: analysis.price_target,
					stop_loss: analysis.stop_loss,
				},
				created_at: new Date().toISOString(),
			};

			// Validate and save to database
			const validatedData = DailyAnalysisSchema.parse(analysisData);

			const insertQuery = `
				INSERT INTO daily_analysis (
					symbol, date, composite_score, rating, 
					confidence, analysis_data, created_at
				) VALUES ($1, $2, $3, $4, $5, $6, $7)
				RETURNING id
			`;

			const result = await db.queryOne(insertQuery, [
				validatedData.symbol,
				validatedData.date,
				validatedData.composite_score,
				validatedData.rating,
				validatedData.confidence,
				JSON.stringify(validatedData.analysis_data),
				validatedData.created_at,
			]);

			// Get cost summary
			const costSummary = deepseek.getCostSummary();

			console.log(`✅ Analysis complete for ${payload.symbol}`);
			console.log(`💰 DeepSeek cost: $${costSummary.total_cost_usd.toFixed(4)}`);
			console.log(`📈 Recommendation: ${analysis.recommendation} (${analysis.confidence}% confidence)`);

			return {
				success: true,
				symbol: payload.symbol,
				analysis: {
					recommendation: analysis.recommendation,
					confidence: analysis.confidence,
					price_target: analysis.price_target,
					key_points: analysis.key_points,
				},
				database_id: result.success ? result.data?.id : null,
				cost_summary: costSummary,
				execution_time: new Date().toISOString(),
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