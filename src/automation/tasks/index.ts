// Scheduled Tasks Index
// This file exports all scheduled tasks for the AI Trading System

// Portfolio Analysis Scheduled Tasks
export {
	dailyPortfolioAnalysisScheduled,
	weeklyPortfolioAnalysisScheduled,
	endOfDayPortfolioSummaryScheduled
} from "./scheduled-portfolio-analysis";

// Health Monitoring Scheduled Tasks
export {
	systemHealthCheckScheduled,
	dailyHealthSummaryScheduled,
	weeklyHealthAnalysisScheduled
} from "./scheduled-health-monitoring";

// Stock Price Alert Scheduled Tasks
export {
	continuousStockPriceMonitoringScheduled,
	afterHoursPriceAlertSetupScheduled,
	preMarketAlertReviewScheduled,
	weeklyAlertCleanupScheduled
} from "./scheduled-stock-alerts";

// Original Tasks (for manual triggering)
export { portfolioAnalysisTask } from "./portfolio-analysis";
export { healthCheckTask, systemHealthMonitor, scheduledHealthCheck } from "./health-monitor";
export {
	stockPriceMonitorTask,
	processStockAlertTask,
	setupPortfolioPriceAlertsTask
} from "./stock-price-alerts";
export {
	preMarketAnalysis,
	marketOpenAnalysis,
	midDayPortfolioCheck,
	marketCloseAnalysis,
	weeklyDeepAnalysis,
	continuousPriceMonitoring
} from "./scheduled-orchestrator";

// Simple test task
export { simpleTestTask } from "./simple-test";
