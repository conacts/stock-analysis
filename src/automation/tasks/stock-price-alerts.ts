import { task } from "@trigger.dev/sdk/v3";
import {
	StockAlertPayload,
	PriceMovementPayload,
	StockPriceAlertConfig,
	PortfolioPosition,
	PortfolioPayload
} from "../shared/types";
import { getValidatedEnv, createApiClient } from "../shared/env-validation";

export const stockPriceMonitorTask = task({
	id: "stock-price-monitor",
	run: async () => {
		console.log("📊 Starting stock price monitoring");

		try {
			// Validate environment variables first
			const env = getValidatedEnv();
			const apiClient = createApiClient(env);

			// Get all active price alerts
			const activeAlerts = await apiClient.get('/alerts/price-alerts/active');

			console.log(`📋 Found ${activeAlerts.length} active price alerts`);

			const results: Array<{
				symbol: string;
				status: "triggered" | "monitored" | "error";
				percentageChange?: number;
				alertType?: string;
				error?: string;
			}> = [];
			let alertsTriggered = 0;

			for (const alert of activeAlerts) {
				try {
					// Get current price data for the symbol
					const priceData = await apiClient.get(`/market-data/${alert.symbol}/current`);

					// Check if alert condition is met
					const shouldTrigger = await checkAlertCondition(alert, priceData);

					if (shouldTrigger) {
						console.log(`🚨 Alert triggered for ${alert.symbol}: ${alert.alertType} threshold ${alert.threshold}`);

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
							marketHours: priceData.marketHours
						};

						// Process the alert
						await processStockAlert(alertPayload, alert);
						alertsTriggered++;

						results.push({
							symbol: alert.symbol,
							status: "triggered",
							percentageChange: priceData.percentageChange,
							alertType: alert.alertType
						});
					} else {
						results.push({
							symbol: alert.symbol,
							status: "monitored",
							percentageChange: priceData.percentageChange,
							alertType: alert.alertType
						});
					}

				} catch (error) {
					console.error(`❌ Error processing alert for ${alert.symbol}:`, error);
					results.push({
						symbol: alert.symbol,
						status: "error",
						error: error.message
					});
				}
			}

			console.log(`✅ Price monitoring completed - ${alertsTriggered} alerts triggered`);

			return {
				success: true,
				alertsMonitored: activeAlerts.length,
				alertsTriggered: alertsTriggered,
				results: results,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ Stock price monitoring failed:", error);
			throw error;
		}
	},
});

export const processStockAlertTask = task({
	id: "process-stock-alert",
	run: async (payload: StockAlertPayload) => {
		console.log(`🔔 Processing stock alert for ${payload.symbol}: ${payload.alertType} ${payload.threshold}%`);

		try {
			// Validate environment variables
			const env = getValidatedEnv();
			const apiClient = createApiClient(env);

			// Get portfolio context if portfolio ID is provided
			let portfolioContext: any = null;
			if (payload.portfolioId) {
				portfolioContext = await apiClient.get(`/portfolio/${payload.portfolioId}/context/${payload.symbol}`);
			}

			// Generate LLM analysis for the alert
			const analysis = await generateAlertAnalysis(payload, portfolioContext, apiClient);

			// Store the alert trigger in database
			await storeAlertTrigger(payload, analysis, apiClient);

			// Send notifications
			const notificationChannels = await sendAlertNotifications(payload, analysis, portfolioContext, apiClient);

			console.log(`✅ Alert processed for ${payload.symbol} - Notifications sent via: ${notificationChannels.join(', ')}`);

			return {
				success: true,
				symbol: payload.symbol,
				alertType: payload.alertType,
				analysis: analysis,
				portfolioImpact: portfolioContext?.impact || 0,
				notificationChannels: notificationChannels,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error(`❌ Failed to process stock alert for ${payload.symbol}:`, error);
			throw error;
		}
	},
});

export const setupPortfolioPriceAlertsTask = task({
	id: "setup-portfolio-price-alerts",
	run: async (payload: PortfolioPayload) => {
		console.log(`⚙️ Setting up price alerts for portfolio ${payload.portfolioId}: ${payload.portfolioName}`);

		try {
			// Validate environment variables
			const env = getValidatedEnv();
			const apiClient = createApiClient(env);

			// Get portfolio positions
			const positions: PortfolioPosition[] = await apiClient.get(`/portfolio/${payload.portfolioId}/positions`);

			console.log(`📊 Found ${positions.length} positions in portfolio`);

			const alertsCreated: any[] = [];

			// Create price alerts for each position
			for (const position of positions) {
				// Create percentage-based alerts (±5%, ±10%)
				const alertConfigs = [
					{
						symbol: position.symbol,
						alertType: "percentage_up" as const,
						threshold: 5.0,
						isActive: true,
						portfolioId: payload.portfolioId,
						triggerCount: 0
					},
					{
						symbol: position.symbol,
						alertType: "percentage_down" as const,
						threshold: 5.0,
						isActive: true,
						portfolioId: payload.portfolioId,
						triggerCount: 0
					}
				];

				for (const alertConfig of alertConfigs) {
					const createdAlert = await apiClient.post('/alerts/price-alerts', alertConfig);
					alertsCreated.push(createdAlert);
				}
			}

			console.log(`✅ Created ${alertsCreated.length} price alerts for portfolio ${payload.portfolioName}`);

			return {
				success: true,
				portfolioId: payload.portfolioId,
				portfolioName: payload.portfolioName,
				positionsCount: positions.length,
				alertsCreated: alertsCreated.length,
				alerts: alertsCreated,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error(`❌ Failed to setup portfolio price alerts:`, error);
			throw error;
		}
	},
});

// Helper functions with proper environment validation

// Check if alert condition is met
async function checkAlertCondition(
	alert: StockPriceAlertConfig,
	priceData: any
): Promise<boolean> {
	const { alertType, threshold } = alert;
	const { percentageChange, currentPrice } = priceData;

	switch (alertType) {
		case 'percentage_up':
			return percentageChange >= threshold;
		case 'percentage_down':
			return percentageChange <= -threshold;
		case 'price_target':
			return currentPrice >= threshold;
		default:
			return false;
	}
}

// Process a triggered stock alert
async function processStockAlert(
	alertPayload: StockAlertPayload,
	alertConfig: StockPriceAlertConfig
): Promise<void> {
	// Trigger the alert processing task
	await processStockAlertTask.trigger(alertPayload);

	// Update alert trigger count and last triggered time
	const env = getValidatedEnv();
	const apiClient = createApiClient(env);

	await apiClient.post(`/alerts/price-alerts/${alertConfig.id}/trigger`, {
		triggered_at: new Date().toISOString()
	});
}

// Generate LLM analysis for the alert
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
	const analysisPayload = {
		alert_data: alertPayload,
		portfolio_context: portfolioContext,
		include_news_analysis: true,
		include_technical_analysis: true,
		generate_recommendations: true
	};

	return await apiClient.post('/alerts/analyze-with-llm', analysisPayload);
}

// Store alert trigger in database
async function storeAlertTrigger(
	alertPayload: StockAlertPayload,
	analysis: any,
	apiClient: any
): Promise<void> {
	const triggerData = {
		alert_payload: alertPayload,
		analysis: analysis,
		triggered_at: new Date().toISOString()
	};

	await apiClient.post('/alerts/store-trigger', triggerData);
}

// Send alert notifications
async function sendAlertNotifications(
	alertPayload: StockAlertPayload,
	analysis: any,
	portfolioContext: any,
	apiClient: any
): Promise<string[]> {
	const notificationPayload = {
		alert: alertPayload,
		analysis: analysis,
		portfolio_context: portfolioContext,
		channels: ['slack', 'email'], // Configure based on urgency and preferences
		priority: analysis.urgency || 'medium'
	};

	return await apiClient.post('/notifications/send-alert', notificationPayload);
}
