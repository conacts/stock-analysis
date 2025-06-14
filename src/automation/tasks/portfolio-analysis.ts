import { task } from "@trigger.dev/sdk/v3";
import {
	PortfolioPayload,
	PortfolioAnalysisResult,
	PortfolioLlmMessage,
	LlmConversationContext,
	PortfolioPosition,
	PortfolioSummary
} from "../shared/types";

export const portfolioAnalysisTask = task({
	id: "portfolio-analysis",
	run: async (payload: PortfolioPayload) => {
		console.log(`🔍 Starting portfolio analysis for Portfolio ${payload.portfolioId} (${payload.portfolioName})`);

		try {
			// Step 1: Extract portfolio data
			const portfolioData = await extractPortfolioData(payload.portfolioId);
			console.log(`📊 Extracted data for ${portfolioData.positions.length} positions, total value: $${portfolioData.totalValue.toLocaleString()}`);

			// Step 2: Get LLM conversation history if requested
			let conversationContext: LlmConversationContext | null = null;
			if (payload.includeLLMHistory) {
				conversationContext = await getLlmConversationHistory(
					payload.portfolioId,
					payload.maxHistoryDays || 30
				);
				console.log(`💬 Retrieved ${conversationContext.recentMessages.length} recent LLM messages`);
			}

			// Step 3: Run comprehensive analysis with DeepSeek
			const analysisResult = await runPortfolioAnalysisWithLLM(
				portfolioData,
				payload.analysisType,
				conversationContext
			);

			// Step 4: Store analysis results and LLM conversation
			await storeAnalysisResults(analysisResult);

			// Step 5: Generate alerts if needed
			const alerts = await generatePortfolioAlerts(analysisResult);

			console.log(`✅ Portfolio analysis completed. Generated ${alerts.length} alerts`);

			return {
				success: true,
				portfolioId: payload.portfolioId,
				analysisType: payload.analysisType,
				totalValue: analysisResult.totalValue,
				recommendations: analysisResult.recommendations,
				riskFactors: analysisResult.riskFactors,
				opportunities: analysisResult.opportunities,
				alertsGenerated: alerts.length,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error(`❌ Portfolio analysis failed:`, error);
			throw error;
		}
	},
});

// Extract comprehensive portfolio data
async function extractPortfolioData(portfolioId: number): Promise<PortfolioSummary> {
	// This would call your Python portfolio extraction script
	const result = await fetch(`${process.env.PYTHON_API_URL}/portfolio/${portfolioId}/summary`, {
		method: 'GET',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to extract portfolio data: ${result.statusText}`);
	}

	return await result.json();
}

// Get LLM conversation history for context
async function getLlmConversationHistory(
	portfolioId: number,
	maxDays: number
): Promise<LlmConversationContext> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/portfolio/${portfolioId}/llm-history`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			max_days: maxDays,
			include_market_context: true
		})
	});

	if (!result.ok) {
		throw new Error(`Failed to get LLM history: ${result.statusText}`);
	}

	return await result.json();
}

// Run comprehensive portfolio analysis with DeepSeek LLM
async function runPortfolioAnalysisWithLLM(
	portfolioData: PortfolioSummary,
	analysisType: string,
	conversationContext: LlmConversationContext | null
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

	const result = await fetch(`${process.env.PYTHON_API_URL}/portfolio/analyze-with-llm`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(analysisPayload)
	});

	if (!result.ok) {
		throw new Error(`Failed to run LLM analysis: ${result.statusText}`);
	}

	return await result.json();
}

// Store analysis results in database
async function storeAnalysisResults(analysisResult: PortfolioAnalysisResult): Promise<void> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/portfolio/store-analysis`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(analysisResult)
	});

	if (!result.ok) {
		throw new Error(`Failed to store analysis results: ${result.statusText}`);
	}
}

// Generate portfolio-specific alerts
async function generatePortfolioAlerts(analysisResult: PortfolioAnalysisResult): Promise<string[]> {
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
		await sendPortfolioAlerts(analysisResult.portfolioId, alerts);
	}

	return alerts;
}

// Send alerts to notification channels
async function sendPortfolioAlerts(portfolioId: number, alerts: string[]): Promise<void> {
	// This would integrate with your existing alert system
	const alertPayload = {
		portfolio_id: portfolioId,
		alerts: alerts,
		channels: ['slack', 'email'], // Configure based on preferences
		priority: 'high'
	};

	await fetch(`${process.env.PYTHON_API_URL}/alerts/send`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(alertPayload)
	});
}

// Scheduled portfolio analysis tasks
export const dailyPortfolioAnalysis = task({
	id: "daily-portfolio-analysis",
	run: async () => {
		console.log("🌅 Starting daily portfolio analysis for all portfolios");

		// Get all active portfolios
		const portfolios = await getActivePortfolios();
		console.log(`📋 Found ${portfolios.length} active portfolios to analyze`);

		const results = [];

		for (const portfolio of portfolios) {
			try {
				const result = await portfolioAnalysisTask.trigger({
					portfolioId: portfolio.id,
					portfolioName: portfolio.name,
					analysisType: "daily",
					includePositions: true,
					includeLLMHistory: true,
					maxHistoryDays: 7 // Last week of context
				});

				results.push({
					portfolioId: portfolio.id,
					status: 'completed',
					result: result
				});

			} catch (error) {
				console.error(`❌ Failed to analyze portfolio ${portfolio.id}:`, error);
				results.push({
					portfolioId: portfolio.id,
					status: 'failed',
					error: error.message
				});
			}
		}

		console.log(`✅ Daily portfolio analysis completed. ${results.filter(r => r.status === 'completed').length}/${results.length} successful`);

		return {
			success: true,
			portfoliosAnalyzed: results.length,
			successfulAnalyses: results.filter(r => r.status === 'completed').length,
			results: results,
			timestamp: new Date().toISOString()
		};
	}
});

// Get all active portfolios
async function getActivePortfolios(): Promise<Array<{ id: number, name: string }>> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/portfolios/active`, {
		method: 'GET',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to get active portfolios: ${result.statusText}`);
	}

	return await result.json();
}
