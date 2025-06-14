import { schedules } from "@trigger.dev/sdk/v3";
import { dailyAnalysis, portfolioMonitoring, weeklyDeepAnalysis } from "./daily-analysis";

// Daily market analysis at market open (9:30 AM EST)
schedules.create({
	id: "daily-market-analysis",
	cron: "30 9 * * 1-5", // Monday-Friday at 9:30 AM EST
	task: dailyAnalysis,
	payload: {
		symbols: ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "JNJ"],
		maxStocks: 20
	}
});

// Portfolio monitoring at market close (4:00 PM EST)
schedules.create({
	id: "daily-portfolio-monitoring",
	cron: "0 16 * * 1-5", // Monday-Friday at 4:00 PM EST
	task: portfolioMonitoring,
	payload: {
		portfolioId: "default"
	}
});

// Weekly deep analysis on Sunday evenings (8:00 PM EST)
schedules.create({
	id: "weekly-deep-analysis",
	cron: "0 20 * * 0", // Sunday at 8:00 PM EST
	task: weeklyDeepAnalysis,
	payload: {}
});

// Pre-market analysis (8:00 AM EST)
schedules.create({
	id: "pre-market-analysis",
	cron: "0 8 * * 1-5", // Monday-Friday at 8:00 AM EST
	task: dailyAnalysis,
	payload: {
		symbols: ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
		maxStocks: 5
	}
});

// End-of-week portfolio summary (Friday 5:00 PM EST)
schedules.create({
	id: "weekly-portfolio-summary",
	cron: "0 17 * * 5", // Friday at 5:00 PM EST
	task: portfolioMonitoring,
	payload: {
		portfolioId: "default"
	}
});
