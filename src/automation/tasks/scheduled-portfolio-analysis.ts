import { schedules } from "@trigger.dev/sdk/v3";
import { getValidatedEnv, createApiClient } from "../shared/env-validation";
import {
	PortfolioPayload,
	PortfolioAnalysisResult,
	PortfolioLlmMessage,
	LlmConversationContext,
	PortfolioPosition,
	PortfolioSummary
} from "../shared/types";

// Extended interface for our scheduled analysis results
interface ExtendedPortfolioAnalysisResult extends PortfolioAnalysisResult {
	alertsGenerated?: number;
	weeklyReturn?: number;
	rebalanceRecommendations?: string[];
}

// Daily Portfolio Analysis - Runs every weekday at 9:45 AM EST (15 minutes after market open)
export const dailyPortfolioAnalysisScheduled = schedules.task({
	id: "daily-portfolio-analysis-scheduled",
	cron: {
		pattern: "45 9 * * 1-5", // 9:45 AM Monday-Friday
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`📊 Starting scheduled daily portfolio analysis at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			// Get all active portfolios
			const activePortfolios = await getActivePortfolios();
			console.log(`📋 Found ${activePortfolios.length} active portfolios to analyze`);

			const results: Array<{
				portfolioId: number;
				portfolioName: string;
				status: "success" | "error";
				totalValue?: number;
				alertsGenerated?: number;
				error?: string;
			}> = [];

			// Analyze each portfolio
			for (const portfolio of activePortfolios) {
				try {
					console.log(`🔍 Analyzing portfolio ${portfolio.id}: ${portfolio.name}`);

					const portfolioPayload: PortfolioPayload = {
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						analysisType: "daily",
						includeLLMHistory: true,
						maxHistoryDays: 7
					};

					const analysisResult = await runPortfolioAnalysis(portfolioPayload);

					results.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						status: "success",
						totalValue: analysisResult.totalValue,
						alertsGenerated: analysisResult.alertsGenerated
					});

				} catch (error: any) {
					console.error(`❌ Failed to analyze portfolio ${portfolio.id}:`, error);
					results.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						status: "error",
						error: error.message
					});
				}
			}

			const successCount = results.filter(r => r.status === "success").length;
			console.log(`✅ Daily portfolio analysis completed: ${successCount}/${activePortfolios.length} portfolios analyzed successfully`);

			return {
				success: true,
				portfoliosAnalyzed: activePortfolios.length,
				successfulAnalyses: successCount,
				results: results,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Scheduled daily portfolio analysis failed:", error);
			throw error;
		}
	},
});

// Weekly Deep Portfolio Analysis - Runs every Sunday at 8:00 PM EST
export const weeklyPortfolioAnalysisScheduled = schedules.task({
	id: "weekly-portfolio-analysis-scheduled",
	cron: {
		pattern: "0 20 * * 0", // 8:00 PM on Sundays
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`📊 Starting scheduled weekly deep portfolio analysis at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			// Get all active portfolios
			const activePortfolios = await getActivePortfolios();
			console.log(`📋 Found ${activePortfolios.length} active portfolios for deep analysis`);

			const results: Array<{
				portfolioId: number;
				portfolioName: string;
				status: "success" | "error";
				weeklyReturn?: number;
				riskScore?: number;
				rebalanceRecommendations?: number;
				error?: string;
			}> = [];

			// Perform deep analysis for each portfolio
			for (const portfolio of activePortfolios) {
				try {
					console.log(`🔍 Deep analyzing portfolio ${portfolio.id}: ${portfolio.name}`);

					const portfolioPayload: PortfolioPayload = {
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						analysisType: "weekly",
						includeLLMHistory: true,
						maxHistoryDays: 30
					};

					const analysisResult = await runPortfolioAnalysis(portfolioPayload);

					// Generate weekly report
					await generateWeeklyPortfolioReport(portfolio.id, analysisResult);

					results.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						status: "success",
						weeklyReturn: analysisResult.weeklyReturn,
						riskScore: analysisResult.riskScore,
						rebalanceRecommendations: analysisResult.rebalanceRecommendations?.length || 0
					});

				} catch (error: any) {
					console.error(`❌ Failed deep analysis for portfolio ${portfolio.id}:`, error);
					results.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						status: "error",
						error: error.message
					});
				}
			}

			const successCount = results.filter(r => r.status === "success").length;
			console.log(`✅ Weekly deep portfolio analysis completed: ${successCount}/${activePortfolios.length} portfolios analyzed successfully`);

			return {
				success: true,
				portfoliosAnalyzed: activePortfolios.length,
				successfulAnalyses: successCount,
				results: results,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Scheduled weekly portfolio analysis failed:", error);
			throw error;
		}
	},
});

// End-of-Day Portfolio Summary - Runs every weekday at 4:30 PM EST (after market close)
export const endOfDayPortfolioSummaryScheduled = schedules.task({
	id: "end-of-day-portfolio-summary-scheduled",
	cron: {
		pattern: "30 16 * * 1-5", // 4:30 PM Monday-Friday
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`🌆 Starting scheduled end-of-day portfolio summary at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			// Get all active portfolios
			const activePortfolios = await getActivePortfolios();
			console.log(`📋 Generating end-of-day summaries for ${activePortfolios.length} portfolios`);

			const summaries: Array<{
				portfolioId: number;
				portfolioName: string;
				dailyReturn: number;
				totalValue: number;
				topPerformers: string[];
				topLosers: string[];
				alertsGenerated: number;
			}> = [];

			// Generate summary for each portfolio
			for (const portfolio of activePortfolios) {
				try {
					const summary = await generateEndOfDaySummary(portfolio.id);
					summaries.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						...summary
					});

				} catch (error: any) {
					console.error(`❌ Failed to generate summary for portfolio ${portfolio.id}:`, error);
				}
			}

			// Send consolidated daily report
			await sendDailyPortfolioReport(summaries);

			console.log(`✅ End-of-day portfolio summaries completed for ${summaries.length} portfolios`);

			return {
				success: true,
				portfoliosSummarized: summaries.length,
				totalPortfolioValue: summaries.reduce((sum, s) => sum + s.totalValue, 0),
				totalAlertsGenerated: summaries.reduce((sum, s) => sum + s.alertsGenerated, 0),
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Scheduled end-of-day portfolio summary failed:", error);
			throw error;
		}
	},
});

// Helper functions

async function getActivePortfolios(): Promise<Array<{ id: number, name: string }>> {
	try {
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		const response = await apiClient.get('/portfolios/active');
		return response.portfolios || [];
	} catch (error: any) {
		console.error("❌ Failed to get active portfolios:", error);
		return [];
	}
}

async function runPortfolioAnalysis(payload: PortfolioPayload): Promise<ExtendedPortfolioAnalysisResult> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	// Extract portfolio data
	const portfolioData = await extractPortfolioData(payload.portfolioId, apiClient);

	// Get LLM conversation history if requested
	let conversationContext: LlmConversationContext | null = null;
	if (payload.includeLLMHistory) {
		conversationContext = await getLlmConversationHistory(
			payload.portfolioId,
			payload.maxHistoryDays || 30,
			apiClient
		);
	}

	// Run comprehensive analysis with DeepSeek
	const analysisResult = await runPortfolioAnalysisWithLLM(
		portfolioData,
		payload.analysisType,
		conversationContext,
		apiClient
	);

	// Store analysis results
	await storeAnalysisResults(analysisResult, apiClient);

	// Generate alerts if needed
	const alerts = await generatePortfolioAlerts(analysisResult, apiClient);

	return {
		...analysisResult,
		alertsGenerated: alerts.length
	};
}

async function extractPortfolioData(portfolioId: number, apiClient: any): Promise<PortfolioSummary> {
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), 30000);

	try {
		const response = await apiClient.get(`/portfolio/${portfolioId}/summary`, {
			signal: controller.signal
		});
		return response;
	} finally {
		clearTimeout(timeoutId);
	}
}

async function getLlmConversationHistory(
	portfolioId: number,
	maxDays: number,
	apiClient: any
): Promise<LlmConversationContext> {
	const response = await apiClient.post(`/portfolio/${portfolioId}/llm-history`, {
		max_days: maxDays,
		include_market_context: true
	});
	return response;
}

async function runPortfolioAnalysisWithLLM(
	portfolioData: PortfolioSummary,
	analysisType: string,
	conversationContext: LlmConversationContext | null,
	apiClient: any
): Promise<PortfolioAnalysisResult> {
	const analysisPayload = {
		portfolio_data: portfolioData,
		analysis_type: analysisType,
		conversation_context: conversationContext,
		include_recommendations: true,
		include_risk_analysis: true,
		include_opportunities: true,
		store_conversation: true
	};

	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), 30000);

	try {
		const response = await apiClient.post('/portfolio/analyze-with-llm', analysisPayload, {
			signal: controller.signal
		});
		return response;
	} finally {
		clearTimeout(timeoutId);
	}
}

async function storeAnalysisResults(analysisResult: PortfolioAnalysisResult, apiClient: any): Promise<void> {
	await apiClient.post('/portfolio/store-analysis', analysisResult);
}

async function generatePortfolioAlerts(analysisResult: PortfolioAnalysisResult, apiClient: any): Promise<string[]> {
	const alerts: string[] = [];

	// Risk-based alerts
	if (analysisResult.riskScore && analysisResult.riskScore > 0.8) {
		alerts.push(`🚨 HIGH RISK: Portfolio ${analysisResult.portfolioId} risk score is ${(analysisResult.riskScore * 100).toFixed(1)}%`);
	}

	// Performance alerts
	if (analysisResult.dailyReturn && analysisResult.dailyReturn < -0.05) {
		alerts.push(`📉 PERFORMANCE: Portfolio down ${(analysisResult.dailyReturn * 100).toFixed(2)}% today`);
	}

	// Opportunity alerts
	if (analysisResult.opportunities && analysisResult.opportunities.length > 0) {
		alerts.push(`💡 OPPORTUNITIES: ${analysisResult.opportunities.length} new opportunities identified`);
	}

	// Send alerts to notification channels
	if (alerts.length > 0) {
		await sendPortfolioAlerts(analysisResult.portfolioId, alerts, apiClient);
	}

	return alerts;
}

async function sendPortfolioAlerts(portfolioId: number, alerts: string[], apiClient: any): Promise<void> {
	await apiClient.post('/alerts/send', {
		portfolio_id: portfolioId,
		alerts: alerts,
		channels: ['slack', 'email']
	});
}

async function generateWeeklyPortfolioReport(portfolioId: number, analysisResult: PortfolioAnalysisResult): Promise<void> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	await apiClient.post('/reports/weekly-portfolio', {
		portfolio_id: portfolioId,
		analysis_result: analysisResult,
		report_type: 'weekly_deep_analysis'
	});
}

async function generateEndOfDaySummary(portfolioId: number): Promise<{
	dailyReturn: number;
	totalValue: number;
	topPerformers: string[];
	topLosers: string[];
	alertsGenerated: number;
}> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	const response = await apiClient.get(`/portfolio/${portfolioId}/end-of-day-summary`);
	return response;
}

async function sendDailyPortfolioReport(summaries: any[]): Promise<void> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	await apiClient.post('/reports/daily-consolidated', {
		portfolio_summaries: summaries,
		report_date: new Date().toISOString().split('T')[0]
	});
}
