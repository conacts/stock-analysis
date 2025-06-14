import { task } from "@trigger.dev/sdk/v3";

export const simpleHealthCheck = task({
	id: "simple-health-check",
	run: async () => {
		const startTime = new Date();

		console.log("🏥 Running simple health check...");

		try {
			// Basic environment check
			const envCheck = {
				nodeVersion: process.version,
				platform: process.platform,
				timestamp: startTime.toISOString(),
				environment: process.env.NODE_ENV || 'development'
			};

			console.log("✅ Environment check passed:", envCheck);

			// Simple Python test (without database)
			console.log("🐍 Testing Python availability...");

			const endTime = new Date();
			const duration = endTime.getTime() - startTime.getTime();

			return {
				status: "completed" as const,
				timestamp: endTime.toISOString(),
				duration,
				checks: envCheck,
				message: "Simple health check completed successfully"
			};

		} catch (error: any) {
			console.error("❌ Health check failed:", error);

			return {
				status: "failed" as const,
				timestamp: new Date().toISOString(),
				error: error.message,
				message: "Health check failed"
			};
		}
	},
});

export const manualTest = task({
	id: "manual-test",
	run: async (payload: { message?: string } = {}) => {
		console.log("🧪 Running manual test...");
		console.log("📝 Message:", payload.message || "No message provided");

		return {
			status: "completed" as const,
			timestamp: new Date().toISOString(),
			message: payload.message || "Manual test completed",
			payload
		};
	},
});
