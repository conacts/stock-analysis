import { schedules } from "@trigger.dev/sdk/v3";
import { getValidatedEnv, createApiClient } from "../shared/env-validation";
import {
	StockAlertPayload,
	StockPriceAlertConfig,
	PortfolioPosition,
	PortfolioPayload
} from "../shared/types";

// Continuous Stock Price Monitoring - Runs every 5 minutes during market hours (9:30 AM - 4:00 PM EST)
export const continuousStockPriceMonitoringScheduled = schedules.task({
	id: "continuous-stock-price-monitoring-scheduled",
	cron: {
		pattern: "*/5 9-16 * * 1-5", // Every 5 minutes, 9 AM - 4 PM, Monday-Friday
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`📊 Starting scheduled stock price monitoring at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			// Check if market is currently open
			const isMarketOpen = await checkMarketHours();
			if (!isMarketOpen) {
				console.log("📴 Market is closed, skipping price monitoring");
				return {
					success: true,
					skipped: true,
					reason: "Market closed",
					scheduledTime: payload.timestamp,
					nextRun: payload.upcoming[0],
					timestamp: new Date().toISOString()
				};
			}

			// Get all active price alerts
			const env = getValidatedEnv();
			const apiClient = createApiClient(env);
			const activeAlerts = await apiClient.get('/alerts/price-alerts/active');

			console.log(`📋 Found ${activeAlerts.length} active price alerts to monitor`);

			const results: Array<{
				symbol: string;
				status: "triggered" | "monitored" | "error";
				percentageChange?: number;
				alertType?: string;
				error?: string;
			}> = [];
			let alertsTriggered = 0;

			// Process alerts in batches to avoid overwhelming the system
			const batchSize = 10;
			for (let i = 0; i < activeAlerts.length; i += batchSize) {
				const batch = activeAlerts.slice(i, i + batchSize);

				const batchPromises = batch.map(async (alert: StockPriceAlertConfig) => {
					try {
						// Get current price data for the symbol
						const priceData = await apiClient.get(`/market-data/${alert.symbol}/current`);

						// Check if alert condition is met
						const shouldTrigger = checkAlertCondition(alert, priceData);

						if (shouldTrigger) {
							console.log(`🚨 Alert triggered for ${alert.symbol}: ${alert.alertType} threshold ${alert.threshold}%`);

							// Create alert payload
							const alertPayload: StockAlertPayload = {
								symbol: alert.symbol,
								currentPrice: priceData.currentPrice,
								previousPrice: priceData.previousPrice,
								percentageChange: priceData.percentageChange,
								volume: priceData.volume,
								alertType: alert.alertType,
								threshold: alert.threshold,
								portfolioId: alert.portfolioId,
								marketHours: true
							};

							// Process the alert
							await processStockAlert(alertPayload, alert, apiClient);
							alertsTriggered++;

							return {
								symbol: alert.symbol,
								status: "triggered" as const,
								percentageChange: priceData.percentageChange,
								alertType: alert.alertType
							};
						} else {
							return {
								symbol: alert.symbol,
								status: "monitored" as const,
								percentageChange: priceData.percentageChange,
								alertType: alert.alertType
							};
						}

					} catch (error: any) {
						console.error(`❌ Error processing alert for ${alert.symbol}:`, error);
						return {
							symbol: alert.symbol,
							status: "error" as const,
							error: error.message
						};
					}
				});

				const batchResults = await Promise.all(batchPromises);
				results.push(...batchResults);

				// Small delay between batches to avoid rate limiting
				if (i + batchSize < activeAlerts.length) {
					await new Promise(resolve => setTimeout(resolve, 1000));
				}
			}

			console.log(`✅ Stock price monitoring completed - ${alertsTriggered} alerts triggered out of ${activeAlerts.length} monitored`);

			return {
				success: true,
				alertsMonitored: activeAlerts.length,
				alertsTriggered: alertsTriggered,
				results: results,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Scheduled stock price monitoring failed:", error);
			throw error;
		}
	},
});

// After-Hours Price Alert Setup - Runs every weekday at 4:15 PM EST (after market close)
export const afterHoursPriceAlertSetupScheduled = schedules.task({
	id: "after-hours-price-alert-setup-scheduled",
	cron: {
		pattern: "15 16 * * 1-5", // 4:15 PM Monday-Friday
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`🌆 Starting after-hours price alert setup at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			const env = getValidatedEnv();
			const apiClient = createApiClient(env);

			// Get all active portfolios
			const activePortfolios = await apiClient.get('/portfolios/active');
			console.log(`📋 Setting up after-hours alerts for ${activePortfolios.portfolios.length} portfolios`);

			let totalAlertsCreated = 0;
			const portfolioResults: Array<{
				portfolioId: number;
				portfolioName: string;
				alertsCreated: number;
				status: "success" | "error";
				error?: string;
			}> = [];

			// Set up after-hours alerts for each portfolio
			for (const portfolio of activePortfolios.portfolios) {
				try {
					console.log(`⚙️ Setting up after-hours alerts for portfolio ${portfolio.id}: ${portfolio.name}`);

					// Get positions that had significant moves today
					const significantMoves = await apiClient.get(`/portfolio/${portfolio.id}/significant-moves?threshold=3`);

					// Create enhanced alerts for positions with significant moves
					const alertsCreated = await createAfterHoursAlerts(portfolio.id, significantMoves, apiClient);

					totalAlertsCreated += alertsCreated;
					portfolioResults.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						alertsCreated: alertsCreated,
						status: "success"
					});

				} catch (error: any) {
					console.error(`❌ Failed to set up after-hours alerts for portfolio ${portfolio.id}:`, error);
					portfolioResults.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						alertsCreated: 0,
						status: "error",
						error: error.message
					});
				}
			}

			console.log(`✅ After-hours alert setup completed - ${totalAlertsCreated} alerts created`);

			return {
				success: true,
				portfoliosProcessed: activePortfolios.portfolios.length,
				totalAlertsCreated: totalAlertsCreated,
				portfolioResults: portfolioResults,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ After-hours price alert setup failed:", error);
			throw error;
		}
	},
});

// Pre-Market Alert Review - Runs every weekday at 8:00 AM EST (before market open)
export const preMarketAlertReviewScheduled = schedules.task({
	id: "pre-market-alert-review-scheduled",
	cron: {
		pattern: "0 8 * * 1-5", // 8:00 AM Monday-Friday
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`🌅 Starting pre-market alert review at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			const env = getValidatedEnv();
			const apiClient = createApiClient(env);

			// Get overnight price movements
			const overnightMoves = await apiClient.get('/market-data/overnight-moves');
			console.log(`📊 Found ${overnightMoves.length} significant overnight moves`);

			// Review and update existing alerts based on overnight activity
			const alertUpdates = await reviewAndUpdateAlerts(overnightMoves, apiClient);

			// Generate pre-market alerts for significant gaps
			const preMarketAlerts = await generatePreMarketAlerts(overnightMoves, apiClient);

			// Send pre-market summary
			await sendPreMarketAlertSummary(overnightMoves, alertUpdates, preMarketAlerts, apiClient);

			console.log(`✅ Pre-market alert review completed - ${alertUpdates.length} alerts updated, ${preMarketAlerts.length} new alerts created`);

			return {
				success: true,
				overnightMovesAnalyzed: overnightMoves.length,
				alertsUpdated: alertUpdates.length,
				newAlertsCreated: preMarketAlerts.length,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Pre-market alert review failed:", error);
			throw error;
		}
	},
});

// Weekly Alert Cleanup - Runs every Sunday at 9:00 PM EST
export const weeklyAlertCleanupScheduled = schedules.task({
	id: "weekly-alert-cleanup-scheduled",
	cron: {
		pattern: "0 21 * * 0", // 9:00 PM on Sundays
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`🧹 Starting weekly alert cleanup at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			const env = getValidatedEnv();
			const apiClient = createApiClient(env);

			// Clean up old triggered alerts (older than 30 days)
			const oldAlertsCleanup = await apiClient.delete('/alerts/cleanup?days=30');

			// Deactivate alerts for positions no longer in portfolios
			const orphanedAlertsCleanup = await apiClient.post('/alerts/cleanup-orphaned');

			// Reset trigger counts for active alerts
			const triggerCountReset = await apiClient.post('/alerts/reset-trigger-counts');

			// Generate weekly alert performance report
			const performanceReport = await generateWeeklyAlertReport(apiClient);

			console.log(`✅ Weekly alert cleanup completed - ${oldAlertsCleanup.deleted} old alerts removed, ${orphanedAlertsCleanup.deactivated} orphaned alerts deactivated`);

			return {
				success: true,
				oldAlertsDeleted: oldAlertsCleanup.deleted,
				orphanedAlertsDeactivated: orphanedAlertsCleanup.deactivated,
				triggerCountsReset: triggerCountReset.reset,
				reportGenerated: true,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Weekly alert cleanup failed:", error);
			throw error;
		}
	},
});

// Helper functions

async function checkMarketHours(): Promise<boolean> {
	try {
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		const marketStatus = await apiClient.get('/market-data/status');
		return marketStatus.isOpen;
	} catch (error: any) {
		console.error("❌ Failed to check market hours:", error);
		// Default to assuming market is open during scheduled hours
		const now = new Date();
		const hour = now.getHours();
		const day = now.getDay();

		// Monday-Friday, 9:30 AM - 4:00 PM EST
		return day >= 1 && day <= 5 && hour >= 9 && hour < 16;
	}
}

function checkAlertCondition(alert: StockPriceAlertConfig, priceData: any): boolean {
	const { alertType, threshold } = alert;
	const { percentageChange } = priceData;

	switch (alertType) {
		case "percentage_up":
			return percentageChange >= threshold;
		case "percentage_down":
			return percentageChange <= -threshold;
		case "price_target":
			// For price targets, we'd need to implement specific logic
			// This is a simplified version
			return Math.abs(percentageChange) >= threshold;
		default:
			return false;
	}
}

async function processStockAlert(
	alertPayload: StockAlertPayload,
	alertConfig: StockPriceAlertConfig,
	apiClient: any
): Promise<void> {
	try {
		// Get portfolio context if portfolio ID is provided
		let portfolioContext: any = null;
		if (alertPayload.portfolioId) {
			portfolioContext = await apiClient.get(`/portfolio/${alertPayload.portfolioId}/context/${alertPayload.symbol}`);
		}

		// Generate LLM analysis for the alert
		const analysis = await generateAlertAnalysis(alertPayload, portfolioContext, apiClient);

		// Store the alert trigger in database
		await storeAlertTrigger(alertPayload, analysis, apiClient);

		// Send notifications
		await sendAlertNotifications(alertPayload, analysis, portfolioContext, apiClient);

		// Update alert trigger count
		await apiClient.post(`/alerts/price-alerts/${alertConfig.id}/trigger`);

	} catch (error: any) {
		console.error(`❌ Failed to process stock alert for ${alertPayload.symbol}:`, error);
		throw error;
	}
}

async function generateAlertAnalysis(
	alertPayload: StockAlertPayload,
	portfolioContext: any,
	apiClient: any
): Promise<{
	analysis: string;
	recommendation: string;
	urgency: 'low' | 'medium' | 'high';
	actionItems: string[];
}> {
	const analysisRequest = {
		symbol: alertPayload.symbol,
		price_change: alertPayload.percentageChange,
		alert_type: alertPayload.alertType,
		portfolio_context: portfolioContext,
		market_hours: alertPayload.marketHours
	};

	const response = await apiClient.post('/analysis/alert-analysis', analysisRequest);
	return response;
}

async function storeAlertTrigger(
	alertPayload: StockAlertPayload,
	analysis: any,
	apiClient: any
): Promise<void> {
	const triggerData = {
		symbol: alertPayload.symbol,
		alert_type: alertPayload.alertType,
		threshold: alertPayload.threshold,
		current_price: alertPayload.currentPrice,
		percentage_change: alertPayload.percentageChange,
		portfolio_id: alertPayload.portfolioId,
		analysis: analysis,
		triggered_at: new Date().toISOString()
	};

	await apiClient.post('/alerts/triggers', triggerData);
}

async function sendAlertNotifications(
	alertPayload: StockAlertPayload,
	analysis: any,
	portfolioContext: any,
	apiClient: any
): Promise<void> {
	const notificationData = {
		type: 'stock_price_alert',
		symbol: alertPayload.symbol,
		alert_type: alertPayload.alertType,
		percentage_change: alertPayload.percentageChange,
		current_price: alertPayload.currentPrice,
		analysis: analysis,
		portfolio_context: portfolioContext,
		urgency: analysis.urgency,
		channels: ['slack', 'email']
	};

	await apiClient.post('/notifications/send', notificationData);
}

async function createAfterHoursAlerts(
	portfolioId: number,
	significantMoves: any[],
	apiClient: any
): Promise<number> {
	let alertsCreated = 0;

	for (const move of significantMoves) {
		// Create tighter alerts for positions that moved significantly
		const alertConfigs = [
			{
				symbol: move.symbol,
				alertType: "percentage_up" as const,
				threshold: 2.0, // Tighter threshold for after-hours
				isActive: true,
				portfolioId: portfolioId,
				triggerCount: 0,
				expiresAt: new Date(Date.now() + 16 * 60 * 60 * 1000) // Expires in 16 hours
			},
			{
				symbol: move.symbol,
				alertType: "percentage_down" as const,
				threshold: 2.0,
				isActive: true,
				portfolioId: portfolioId,
				triggerCount: 0,
				expiresAt: new Date(Date.now() + 16 * 60 * 60 * 1000)
			}
		];

		for (const alertConfig of alertConfigs) {
			await apiClient.post('/alerts/price-alerts', alertConfig);
			alertsCreated++;
		}
	}

	return alertsCreated;
}

async function reviewAndUpdateAlerts(overnightMoves: any[], apiClient: any): Promise<any[]> {
	const updates: any[] = [];

	for (const move of overnightMoves) {
		// Get existing alerts for this symbol
		const existingAlerts = await apiClient.get(`/alerts/price-alerts/symbol/${move.symbol}`);

		for (const alert of existingAlerts) {
			// Adjust thresholds based on overnight volatility
			const newThreshold = calculateAdjustedThreshold(alert.threshold, move.volatility);

			if (newThreshold !== alert.threshold) {
				await apiClient.put(`/alerts/price-alerts/${alert.id}`, {
					threshold: newThreshold
				});

				updates.push({
					alertId: alert.id,
					symbol: move.symbol,
					oldThreshold: alert.threshold,
					newThreshold: newThreshold
				});
			}
		}
	}

	return updates;
}

async function generatePreMarketAlerts(overnightMoves: any[], apiClient: any): Promise<any[]> {
	const newAlerts: any[] = [];

	for (const move of overnightMoves) {
		// Create gap alerts for significant overnight moves
		if (Math.abs(move.gapPercentage) > 5) {
			const gapAlert = {
				symbol: move.symbol,
				alertType: move.gapPercentage > 0 ? "percentage_down" as const : "percentage_up" as const,
				threshold: 3.0, // Alert if it reverses 3% from the gap
				isActive: true,
				triggerCount: 0,
				expiresAt: new Date(Date.now() + 6 * 60 * 60 * 1000) // Expires in 6 hours
			};

			const createdAlert = await apiClient.post('/alerts/price-alerts', gapAlert);
			newAlerts.push(createdAlert);
		}
	}

	return newAlerts;
}

async function sendPreMarketAlertSummary(
	overnightMoves: any[],
	alertUpdates: any[],
	preMarketAlerts: any[],
	apiClient: any
): Promise<void> {
	const summaryData = {
		type: 'pre_market_alert_summary',
		overnight_moves: overnightMoves,
		alert_updates: alertUpdates,
		new_alerts: preMarketAlerts,
		summary_date: new Date().toISOString().split('T')[0]
	};

	await apiClient.post('/reports/pre-market-alert-summary', summaryData);
}

async function generateWeeklyAlertReport(apiClient: any): Promise<any> {
	const weekStart = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
	const reportData = await apiClient.get(`/alerts/weekly-report?start_date=${weekStart.toISOString()}`);

	await apiClient.post('/reports/weekly-alert-performance', reportData);
	return reportData;
}

function calculateAdjustedThreshold(currentThreshold: number, volatility: number): number {
	// Adjust threshold based on volatility
	// Higher volatility = higher threshold to reduce noise
	const volatilityMultiplier = Math.max(1, volatility / 10);
	return Math.round(currentThreshold * volatilityMultiplier * 100) / 100;
}
