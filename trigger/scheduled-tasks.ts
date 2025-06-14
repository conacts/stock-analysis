import { schedules } from "@trigger.dev/sdk/v3";
import { dailyAnalysisTask, portfolioMonitoringTask, weeklyDeepAnalysisTask } from "./daily-analysis";
import { systemHealthTask } from "./alert-tasks";

// Market Open Analysis - 9:30 AM EST (2:30 PM UTC) on weekdays
export const marketOpenAnalysis = schedules.task({
	id: "market-open-analysis",
	cron: "30 14 * * 1-5", // 2:30 PM UTC = 9:30 AM EST
	maxDuration: 1800, // 30 minutes
	run: async (payload, { ctx }) => {
		return await dailyAnalysisTask.trigger({
			symbols: ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "AMD", "CRM"],
			forceRun: false,
		});
	},
});

// Market Close Portfolio Monitoring - 4:30 PM EST (9:30 PM UTC) on weekdays
export const marketCloseMonitoring = schedules.task({
	id: "market-close-monitoring",
	cron: "30 21 * * 1-5", // 9:30 PM UTC = 4:30 PM EST
	maxDuration: 600, // 10 minutes
	run: async (payload, { ctx }) => {
		return await portfolioMonitoringTask.trigger({});
	},
});

// Pre-Market Analysis - 8:00 AM EST (1:00 PM UTC) on weekdays
export const preMarketAnalysis = schedules.task({
	id: "pre-market-analysis",
	cron: "0 13 * * 1-5", // 1:00 PM UTC = 8:00 AM EST
	maxDuration: 1800, // 30 minutes
	run: async (payload, { ctx }) => {
		return await dailyAnalysisTask.trigger({
			symbols: ["SPY", "QQQ", "IWM", "VIX"], // Market indicators
			forceRun: true,
		});
	},
});

// Weekly Deep Analysis - Sunday 8:00 PM EST (Monday 1:00 AM UTC)
export const weeklyAnalysis = schedules.task({
	id: "weekly-deep-analysis",
	cron: "0 1 * * 1", // Monday 1:00 AM UTC = Sunday 8:00 PM EST
	maxDuration: 3600, // 1 hour
	run: async (payload, { ctx }) => {
		return await weeklyDeepAnalysisTask.trigger({});
	},
});

// Sector-Specific Weekly Analysis - Different sectors on different days
export const techSectorAnalysis = schedules.task({
	id: "tech-sector-analysis",
	cron: "0 2 * * 2", // Tuesday 2:00 AM UTC = Monday 9:00 PM EST
	maxDuration: 3600, // 1 hour
	run: async (payload, { ctx }) => {
		return await weeklyDeepAnalysisTask.trigger({
			sector: "Technology",
		});
	},
});

export const financialSectorAnalysis = schedules.task({
	id: "financial-sector-analysis",
	cron: "0 2 * * 3", // Wednesday 2:00 AM UTC = Tuesday 9:00 PM EST
	maxDuration: 3600, // 1 hour
	run: async (payload, { ctx }) => {
		return await weeklyDeepAnalysisTask.trigger({
			sector: "Financial Services",
		});
	},
});

export const healthcareSectorAnalysis = schedules.task({
	id: "healthcare-sector-analysis",
	cron: "0 2 * * 4", // Thursday 2:00 AM UTC = Wednesday 9:00 PM EST
	maxDuration: 3600, // 1 hour
	run: async (payload, { ctx }) => {
		return await weeklyDeepAnalysisTask.trigger({
			sector: "Healthcare",
		});
	},
});

// Mid-day portfolio check - 12:00 PM EST (5:00 PM UTC) on weekdays
export const midDayPortfolioCheck = schedules.task({
	id: "mid-day-portfolio-check",
	cron: "0 17 * * 1-5", // 5:00 PM UTC = 12:00 PM EST
	maxDuration: 600, // 10 minutes
	run: async (payload, { ctx }) => {
		return await portfolioMonitoringTask.trigger({});
	},
});

// System Health Check - Every 6 hours
export const systemHealthCheck = schedules.task({
	id: "system-health-check",
	cron: "0 */6 * * *", // Every 6 hours
	maxDuration: 600, // 10 minutes
	run: async (payload, { ctx }) => {
		return await systemHealthTask.trigger({
			checkType: "quick",
		});
	},
});

// Comprehensive Health Check - Daily at 6:00 AM EST (11:00 AM UTC)
export const dailyHealthCheck = schedules.task({
	id: "daily-health-check",
	cron: "0 11 * * *", // 11:00 AM UTC = 6:00 AM EST
	maxDuration: 600, // 10 minutes
	run: async (payload, { ctx }) => {
		return await systemHealthTask.trigger({
			checkType: "full",
		});
	},
});

// Monthly comprehensive analysis - First Sunday of each month at 10:00 PM EST
export const monthlyComprehensiveAnalysis = schedules.task({
	id: "monthly-comprehensive-analysis",
	cron: "0 3 1-7 * 0", // First Sunday of month at 3:00 AM UTC = 10:00 PM EST Saturday
	maxDuration: 3600, // 1 hour
	run: async (payload, { ctx }) => {
		return await weeklyDeepAnalysisTask.trigger({
			sector: "all",
		});
	},
});
