import { schedules } from "@trigger.dev/sdk/v3";
import { healthCheck } from './health-check';
import { aiTradingAnalysis } from './ai-trading-analysis';

export const testScheduledTasks = schedules.task({
	id: "test-scheduled-tasks",
	cron: "*/1 * * * *", // Every minute for testing
	maxDuration: 120, // 2 minutes
	run: async () => {
		console.log("🧪 Running scheduled test of our tasks...");

		try {
			// Test health check
			console.log("🏥 Triggering health check...");
			const healthResult = await healthCheck.trigger();
			console.log("Health check triggered:", healthResult.id);

			// Test AI analysis with AAPL
			console.log("🤖 Triggering AI analysis for AAPL...");
			const aiResult = await aiTradingAnalysis.trigger({ symbol: "AAPL" });
			console.log("AI analysis triggered:", aiResult.id);

			return {
				success: true,
				health_check_id: healthResult.id,
				ai_analysis_id: aiResult.id,
				timestamp: new Date().toISOString(),
			};
		} catch (error) {
			console.error("❌ Test error:", error);
			return {
				success: false,
				error: error instanceof Error ? error.message : 'Unknown error',
				timestamp: new Date().toISOString(),
			};
		}
	},
}); 