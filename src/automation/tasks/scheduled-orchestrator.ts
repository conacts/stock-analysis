import { task, schedules } from "@trigger.dev/sdk/v3";
import { portfolioAnalysisTask, dailyPortfolioAnalysis } from "./portfolio-analysis";
import { stockPriceMonitorTask, setupPortfolioPriceAlertsTask } from "./stock-price-alerts";
import { healthCheckTask, systemHealthMonitor } from "./health-monitor";
import { MultiPortfolioPayload } from "../shared/types";
import { getValidatedEnv, createApiClient } from "../shared/env-validation";

// Market Hours Triggers
export const preMarketAnalysis = task({
	id: "pre-market-analysis",
	run: async () => {
		console.log("🌅 Starting pre-market analysis at 8:00 AM EST");

		try {
			// 1. Check overnight news and events
			const newsAnalysis = await analyzeOvernightNews();

			// 2. Update price alerts for market open
			await updatePreMarketAlerts();

			// 3. Generate pre-market portfolio insights
			const portfolioInsights = await generatePreMarketInsights();

			// 4. Send pre-market summary
			await sendPreMarketSummary(newsAnalysis, portfolioInsights);

			return {
				success: true,
				newsEventsAnalyzed: newsAnalysis.eventsCount,
				portfolioInsights: portfolioInsights.length,
				alertsUpdated: true,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Pre-market analysis failed:", error);
			throw error;
		}
	},
});

export const marketOpenAnalysis = task({
	id: "market-open-analysis",
	run: async () => {
		console.log("🔔 Starting market open analysis at 9:30 AM EST");

		try {
			// 1. Trigger daily portfolio analysis for all portfolios
			const portfolioResults = await dailyPortfolioAnalysis.trigger();

			// 2. Start continuous price monitoring
			const priceMonitoringResults = await stockPriceMonitorTask.trigger();

			// 3. Analyze market opening gaps
			const gapAnalysis = await analyzeMarketGaps();

			// 4. Generate opening bell alerts
			const openingAlerts = await generateOpeningBellAlerts(gapAnalysis);

			return {
				success: true,
				portfolioAnalysisTriggered: true,
				priceMonitoringActive: true,
				gapsAnalyzed: gapAnalysis.length,
				alertsGenerated: openingAlerts.length,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Market open analysis failed:", error);
			throw error;
		}
	},
});

export const midDayPortfolioCheck = task({
	id: "mid-day-portfolio-check",
	run: async () => {
		console.log("🕐 Starting mid-day portfolio check at 12:00 PM EST");

		try {
			// 1. Quick portfolio health check
			const healthChecks = await performPortfolioHealthChecks();

			// 2. Check for significant intraday moves
			const significantMoves = await checkSignificantIntradayMoves();

			// 3. Update position alerts if needed
			const alertUpdates = await updateIntradayAlerts(significantMoves);

			// 4. Generate mid-day summary for portfolios with significant changes
			const summaries = await generateMidDaySummaries(healthChecks, significantMoves);

			return {
				success: true,
				portfoliosChecked: healthChecks.length,
				significantMoves: significantMoves.length,
				alertsUpdated: alertUpdates.length,
				summariesGenerated: summaries.length,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Mid-day portfolio check failed:", error);
			throw error;
		}
	},
});

export const marketCloseAnalysis = task({
	id: "market-close-analysis",
	run: async () => {
		console.log("🌆 Starting market close analysis at 4:30 PM EST");

		try {
			// 1. Final portfolio monitoring for the day
			const finalPortfolioResults = await dailyPortfolioAnalysis.trigger();

			// 2. Analyze daily performance
			const performanceAnalysis = await analyzeDailyPerformance();

			// 3. Generate end-of-day portfolio summaries
			const eodSummaries = await generateEndOfDaySummaries();

			// 4. Prepare after-hours alerts
			const afterHoursAlerts = await setupAfterHoursAlerts();

			// 5. Send daily portfolio reports
			await sendDailyPortfolioReports(eodSummaries, performanceAnalysis);

			return {
				success: true,
				portfolioAnalysisCompleted: true,
				performanceAnalyzed: performanceAnalysis.portfoliosAnalyzed,
				summariesGenerated: eodSummaries.length,
				afterHoursAlertsSetup: afterHoursAlerts.length,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Market close analysis failed:", error);
			throw error;
		}
	},
});

// Weekly Deep Analysis
export const weeklyDeepAnalysis = task({
	id: "weekly-deep-analysis",
	run: async () => {
		console.log("📊 Starting weekly deep analysis on Sunday at 8:00 PM EST");

		try {
			// 1. Comprehensive portfolio analysis with full LLM context
			const deepPortfolioAnalysis = await performDeepPortfolioAnalysis();

			// 2. Sector and correlation analysis
			const sectorAnalysis = await performSectorAnalysis();

			// 3. Risk assessment and rebalancing recommendations
			const riskAssessment = await performWeeklyRiskAssessment();

			// 4. Performance attribution analysis
			const performanceAttribution = await performPerformanceAttribution();

			// 5. Generate comprehensive weekly reports
			const weeklyReports = await generateWeeklyReports({
				portfolioAnalysis: deepPortfolioAnalysis,
				sectorAnalysis: sectorAnalysis,
				riskAssessment: riskAssessment,
				performanceAttribution: performanceAttribution
			});

			// 6. Update price alerts for the coming week
			await updateWeeklyPriceAlerts();

			return {
				success: true,
				portfoliosAnalyzed: deepPortfolioAnalysis.length,
				sectorsAnalyzed: sectorAnalysis.sectorsCount,
				riskAssessmentsCompleted: riskAssessment.length,
				reportsGenerated: weeklyReports.length,
				alertsUpdated: true,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Weekly deep analysis failed:", error);
			throw error;
		}
	},
});

// Continuous Price Monitoring (Every 5 minutes during market hours)
export const continuousPriceMonitoring = task({
	id: "continuous-price-monitoring",
	run: async () => {
		console.log("📈 Running continuous price monitoring");

		try {
			// Check if market is open
			const isMarketOpen = await checkMarketHours();

			if (!isMarketOpen) {
				console.log("🔒 Market is closed, skipping price monitoring");
				return { success: true, skipped: true, reason: "market_closed" };
			}

			// Run price monitoring
			await stockPriceMonitorTask.trigger();

			return {
				success: true,
				marketOpen: true,
				monitoringTriggered: true,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Continuous price monitoring failed:", error);
			throw error;
		}
	},
});

// Multi-Portfolio Comparative Analysis
export const multiPortfolioComparison = task({
	id: "multi-portfolio-comparison",
	run: async (payload: MultiPortfolioPayload) => {
		console.log(`📊 Starting multi-portfolio comparison for ${payload.portfolioIds.length} portfolios`);

		try {
			// 1. Extract data for all portfolios
			const portfolioData = await extractMultiPortfolioData(payload.portfolioIds);

			// 2. Perform comparative analysis
			const comparison = await performPortfolioComparison(portfolioData, payload);

			// 3. Generate correlation analysis if requested
			let correlationAnalysis = null;
			if (payload.includeCorrelation) {
				correlationAnalysis = await performCorrelationAnalysis(portfolioData);
			}

			// 4. Generate rebalancing recommendations if requested
			let rebalancingRecs = null;
			if (payload.includeRebalancing) {
				rebalancingRecs = await generateRebalancingRecommendations(portfolioData);
			}

			// 5. Generate LLM insights if requested
			let llmInsights = null;
			if (payload.includeLLMInsights) {
				llmInsights = await generateMultiPortfolioLLMInsights(portfolioData, comparison);
			}

			return {
				success: true,
				portfoliosCompared: payload.portfolioIds.length,
				comparison: comparison,
				correlationAnalysis: correlationAnalysis,
				rebalancingRecommendations: rebalancingRecs,
				llmInsights: llmInsights,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Multi-portfolio comparison failed:", error);
			throw error;
		}
	},
});

// Helper Functions
async function analyzeOvernightNews(): Promise<{ eventsCount: number; significantEvents: any[] }> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	return await apiClient.post('/news/overnight-analysis');
}

async function updatePreMarketAlerts(): Promise<void> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	await apiClient.post('/alerts/update-premarket');
}

async function generatePreMarketInsights(): Promise<any[]> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	return await apiClient.post('/analysis/premarket-insights');
}

async function sendPreMarketSummary(newsAnalysis: any, portfolioInsights: any[]): Promise<void> {
	await fetch(`${process.env.PYTHON_API_URL}/notifications/premarket-summary`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			news_analysis: newsAnalysis,
			portfolio_insights: portfolioInsights
		})
	});
}

async function analyzeMarketGaps(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/market-gaps`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to analyze market gaps: ${result.statusText}`);
	}

	return await result.json();
}

async function generateOpeningBellAlerts(gapAnalysis: any[]): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/alerts/opening-bell`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ gap_analysis: gapAnalysis })
	});

	if (!result.ok) {
		throw new Error(`Failed to generate opening bell alerts: ${result.statusText}`);
	}

	return await result.json();
}

async function checkMarketHours(): Promise<boolean> {
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	const data = await apiClient.get('/market/hours');
	return data.is_open;
}

async function performPortfolioHealthChecks(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/portfolio/health-checks`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to perform portfolio health checks: ${result.statusText}`);
	}

	return await result.json();
}

async function checkSignificantIntradayMoves(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/intraday-moves`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to check significant intraday moves: ${result.statusText}`);
	}

	return await result.json();
}

async function updateIntradayAlerts(significantMoves: any[]): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/alerts/update-intraday`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ significant_moves: significantMoves })
	});

	if (!result.ok) {
		throw new Error(`Failed to update intraday alerts: ${result.statusText}`);
	}

	return await result.json();
}

async function generateMidDaySummaries(healthChecks: any[], significantMoves: any[]): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/reports/midday-summaries`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			health_checks: healthChecks,
			significant_moves: significantMoves
		})
	});

	if (!result.ok) {
		throw new Error(`Failed to generate mid-day summaries: ${result.statusText}`);
	}

	return await result.json();
}

async function analyzeDailyPerformance(): Promise<{ portfoliosAnalyzed: number }> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/daily-performance`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to analyze daily performance: ${result.statusText}`);
	}

	return await result.json();
}

async function generateEndOfDaySummaries(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/reports/end-of-day`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to generate end-of-day summaries: ${result.statusText}`);
	}

	return await result.json();
}

async function setupAfterHoursAlerts(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/alerts/setup-after-hours`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to setup after-hours alerts: ${result.statusText}`);
	}

	return await result.json();
}

async function sendDailyPortfolioReports(summaries: any[], performance: any): Promise<void> {
	await fetch(`${process.env.PYTHON_API_URL}/notifications/daily-reports`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			summaries: summaries,
			performance: performance
		})
	});
}

async function performDeepPortfolioAnalysis(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/deep-portfolio`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to perform deep portfolio analysis: ${result.statusText}`);
	}

	return await result.json();
}

async function performSectorAnalysis(): Promise<{ sectorsCount: number }> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/sectors`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to perform sector analysis: ${result.statusText}`);
	}

	return await result.json();
}

async function performWeeklyRiskAssessment(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/weekly-risk`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to perform weekly risk assessment: ${result.statusText}`);
	}

	return await result.json();
}

async function performPerformanceAttribution(): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/performance-attribution`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});

	if (!result.ok) {
		throw new Error(`Failed to perform performance attribution: ${result.statusText}`);
	}

	return await result.json();
}

async function generateWeeklyReports(analysisData: any): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/reports/weekly`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(analysisData)
	});

	if (!result.ok) {
		throw new Error(`Failed to generate weekly reports: ${result.statusText}`);
	}

	return await result.json();
}

async function updateWeeklyPriceAlerts(): Promise<void> {
	await fetch(`${process.env.PYTHON_API_URL}/alerts/update-weekly`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		}
	});
}

async function extractMultiPortfolioData(portfolioIds: number[]): Promise<any[]> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/portfolio/multi-extract`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ portfolio_ids: portfolioIds })
	});

	if (!result.ok) {
		throw new Error(`Failed to extract multi-portfolio data: ${result.statusText}`);
	}

	return await result.json();
}

async function performPortfolioComparison(portfolioData: any[], payload: MultiPortfolioPayload): Promise<any> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/portfolio-comparison`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			portfolio_data: portfolioData,
			analysis_type: payload.analysisType
		})
	});

	if (!result.ok) {
		throw new Error(`Failed to perform portfolio comparison: ${result.statusText}`);
	}

	return await result.json();
}

async function performCorrelationAnalysis(portfolioData: any[]): Promise<any> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/correlation`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ portfolio_data: portfolioData })
	});

	if (!result.ok) {
		throw new Error(`Failed to perform correlation analysis: ${result.statusText}`);
	}

	return await result.json();
}

async function generateRebalancingRecommendations(portfolioData: any[]): Promise<any> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/rebalancing`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ portfolio_data: portfolioData })
	});

	if (!result.ok) {
		throw new Error(`Failed to generate rebalancing recommendations: ${result.statusText}`);
	}

	return await result.json();
}

async function generateMultiPortfolioLLMInsights(portfolioData: any[], comparison: any): Promise<any> {
	const result = await fetch(`${process.env.PYTHON_API_URL}/analysis/multi-portfolio-llm`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${process.env.API_TOKEN}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			portfolio_data: portfolioData,
			comparison: comparison
		})
	});

	if (!result.ok) {
		throw new Error(`Failed to generate multi-portfolio LLM insights: ${result.statusText}`);
	}

	return await result.json();
}

// System health monitoring (every minute)
export const systemHealthCheck = task({
	id: "system-health-check",
	run: async () => {
		console.log("🏥 Running system health check");

		try {
			// Run comprehensive health check
			await systemHealthMonitor.trigger();

			console.log(`✅ Health check completed successfully`);

			return {
				success: true,
				healthCheckTriggered: true,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ System health check failed:", error);

			// Send critical alert for health check system failure
			try {
				await fetch(`${process.env.PYTHON_API_URL}/alerts/send-critical-alert`, {
					method: 'POST',
					headers: {
						'Authorization': `Bearer ${process.env.API_TOKEN}`,
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						type: 'health_check_system_failure',
						severity: 'critical',
						subject: '🚨 CRITICAL: Health Check System Failure',
						message: `The health check system itself has failed:\n\nError: ${error.message}\nTimestamp: ${new Date().toISOString()}\n\nThis requires immediate attention!`,
						error: {
							message: error.message,
							stack: error.stack,
							timestamp: new Date().toISOString()
						},
						channels: ['email', 'slack'],
						priority: 'critical'
					})
				});
			} catch (alertError) {
				console.error("Failed to send critical health alert:", alertError);
			}

			throw error;
		}
	},
});
