import { schedules, task } from "@trigger.dev/sdk/v3";
import { getValidatedEnv, createApiClient } from "../shared/env-validation";

// Simplified conversation memory for portfolio analysis
interface SimpleConversationMemory {
	portfolio_id: string;
	last_analysis: string;
	recent_decisions: string[];
	performance_trend: string;
	risk_alerts: string[];
}

// Simple Enhanced Daily Portfolio Analysis
export const simplifiedEnhancedAnalysis = schedules.task({
	id: "simplified-enhanced-analysis",
	cron: {
		pattern: "50 9 * * 1-5", // 9:50 AM Monday-Friday (5 min after regular analysis)
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`🧠 Simplified Enhanced Analysis Started at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		try {
			// Get active portfolios using existing endpoint
			const activePortfolios = await getActivePortfolios(apiClient);
			console.log(`📋 Found ${activePortfolios.length} active portfolios`);

			const results = [];

			for (const portfolio of activePortfolios) {
				try {
					console.log(`🔍 Enhanced analysis for portfolio ${portfolio.portfolioId}: ${portfolio.name}`);

					// 1. Get existing conversation history (simplified)
					const conversationMemory = await getSimpleConversationMemory(apiClient, portfolio.portfolioId);

					// 2. Get current portfolio data using existing endpoint
					const portfolioData = await apiClient.get(`/portfolio/${portfolio.portfolioId}/summary`);

					// 3. Build context-aware analysis request
					const contextualPrompt = buildContextualPrompt(portfolioData, conversationMemory);

					// 4. Run AI analysis with context using existing endpoint
					const analysisRequest = {
						portfolio_data: portfolioData,
						analysis_type: "daily_enhanced",
						conversation_context: {
							previous_analysis: conversationMemory.last_analysis,
							recent_decisions: conversationMemory.recent_decisions,
							performance_trend: conversationMemory.performance_trend
						},
						include_recommendations: true,
						include_risk_analysis: true,
						store_conversation: true
					};

					const analysisResult = await apiClient.post("/portfolio/analyze-with-llm", analysisRequest);

					console.log(`🤖 Enhanced analysis completed for ${portfolio.name}`);

					// 5. Store simple conversation memory for next time
					await storeSimpleConversationMemory(apiClient, portfolio.portfolioId, {
						last_analysis: analysisResult.summary || "Analysis completed",
						recent_decisions: extractDecisions(analysisResult),
						performance_trend: calculatePerformanceTrend(portfolioData),
						risk_alerts: extractRiskAlerts(analysisResult)
					});

					// 6. Generate enhanced alerts if needed
					if (analysisResult.recommendations?.length > 0) {
						await generateEnhancedAlerts(apiClient, portfolio.portfolioId, analysisResult, conversationMemory);
					}

					results.push({
						portfolioId: portfolio.portfolioId,
						portfolioName: portfolio.name,
						status: "success",
						totalValue: portfolioData.totalValue,
						dailyReturn: portfolioData.performance?.dayChangePct || 0,
						recommendationsGenerated: analysisResult.recommendations?.length || 0,
						contextUsed: conversationMemory.recent_decisions.length > 0,
						enhancedAnalysis: true
					});

				} catch (error: any) {
					console.error(`❌ Enhanced analysis failed for portfolio ${portfolio.portfolioId}:`, error);
					results.push({
						portfolioId: portfolio.portfolioId,
						status: "error",
						error: error.message
					});
				}
			}

			const successCount = results.filter(r => r.status === "success").length;
			console.log(`✅ Enhanced analysis completed: ${successCount}/${results.length} portfolios successful`);

			return {
				success: true,
				timestamp: payload.timestamp.toISOString(),
				portfoliosAnalyzed: results.length,
				successfulAnalyses: successCount,
				results: results,
				enhancedFeatures: {
					conversationMemory: true,
					contextualAnalysis: true,
					performanceTrends: true
				}
			};

		} catch (error: any) {
			console.error("❌ Enhanced analysis task failed:", error);
			return {
				success: false,
				error: error.message,
				timestamp: payload.timestamp.toISOString()
			};
		}
	}
});

// Helper functions using existing infrastructure
async function getActivePortfolios(apiClient: any): Promise<Array<{ portfolioId: string, name: string }>> {
	const response = await apiClient.get("/portfolios/active");
	return response.portfolios || [];
}

async function getSimpleConversationMemory(apiClient: any, portfolioId: string): Promise<SimpleConversationMemory> {
	try {
		// Try to get existing conversation history using swarm endpoint
		const response = await apiClient.get(`/trading/swarm/conversation-history/${portfolioId}`);

		const conversations = response.conversations || [];
		const recentConversations = conversations.slice(-5); // Last 5 conversations

		return {
			portfolio_id: portfolioId,
			last_analysis: recentConversations.length > 0 ?
				recentConversations[recentConversations.length - 1].user_message :
				"No previous analysis",
			recent_decisions: recentConversations.map(c => c.user_message || "").filter(Boolean),
			performance_trend: "neutral", // Will be calculated from portfolio data
			risk_alerts: []
		};
	} catch (error) {
		console.log(`📝 No conversation history found for portfolio ${portfolioId}, starting fresh`);
		return {
			portfolio_id: portfolioId,
			last_analysis: "No previous analysis",
			recent_decisions: [],
			performance_trend: "neutral",
			risk_alerts: []
		};
	}
}

function buildContextualPrompt(portfolioData: any, memory: SimpleConversationMemory): string {
	let prompt = `Enhanced portfolio analysis with conversation memory:\n\n`;

	if (memory.recent_decisions.length > 0) {
		prompt += `Previous analysis context:\n${memory.recent_decisions.slice(-2).join('\n')}\n\n`;
	}

	prompt += `Current portfolio performance trend: ${memory.performance_trend}\n`;

	if (memory.risk_alerts.length > 0) {
		prompt += `Previous risk alerts: ${memory.risk_alerts.join(', ')}\n`;
	}

	prompt += `\nPlease provide analysis considering this historical context.`;

	return prompt;
}

async function storeSimpleConversationMemory(apiClient: any, portfolioId: string, memory: Partial<SimpleConversationMemory>): Promise<void> {
	// Store in existing analysis results endpoint
	const memoryData = {
		portfolio_id: portfolioId,
		analysis_type: "conversation_memory",
		timestamp: new Date().toISOString(),
		data: memory
	};

	try {
		await apiClient.post("/portfolio/store-analysis", memoryData);
		console.log(`💾 Stored conversation memory for portfolio ${portfolioId}`);
	} catch (error) {
		console.log(`⚠️ Failed to store conversation memory: ${error}`);
	}
}

function extractDecisions(analysisResult: any): string[] {
	const decisions = [];

	if (analysisResult.recommendations) {
		for (const rec of analysisResult.recommendations) {
			decisions.push(`${rec.action || 'analyze'} ${rec.symbol || 'portfolio'}: ${rec.reasoning || rec.summary || ''}`);
		}
	}

	return decisions.slice(0, 3); // Keep last 3 decisions
}

function calculatePerformanceTrend(portfolioData: any): string {
	const dayChange = portfolioData.performance?.dayChangePct || 0;

	if (dayChange > 2) return "strong_positive";
	if (dayChange > 0.5) return "positive";
	if (dayChange < -2) return "strong_negative";
	if (dayChange < -0.5) return "negative";
	return "neutral";
}

function extractRiskAlerts(analysisResult: any): string[] {
	const alerts = [];

	if (analysisResult.risk_analysis) {
		if (analysisResult.risk_analysis.high_risk_positions) {
			alerts.push("high_risk_positions_detected");
		}
		if (analysisResult.risk_analysis.concentration_risk) {
			alerts.push("concentration_risk");
		}
	}

	return alerts;
}

async function generateEnhancedAlerts(apiClient: any, portfolioId: string, analysisResult: any, memory: SimpleConversationMemory): Promise<void> {
	// Generate contextual alerts using existing alert system
	const alertData = {
		portfolio_id: portfolioId,
		alert_type: "enhanced_analysis",
		recommendations: analysisResult.recommendations,
		context: {
			previous_trend: memory.performance_trend,
			decision_history: memory.recent_decisions.length
		},
		timestamp: new Date().toISOString()
	};

	try {
		// Use existing alert endpoint
		await apiClient.post("/alerts/opening-bell", { gap_analysis: [alertData] });
		console.log(`🚨 Generated enhanced alerts for portfolio ${portfolioId}`);
	} catch (error) {
		console.log(`⚠️ Failed to generate enhanced alerts: ${error}`);
	}
}
