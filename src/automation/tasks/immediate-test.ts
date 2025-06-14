import { task } from "@trigger.dev/sdk/v3";

export const immediateTest = task({
	id: "immediate-test",
	maxDuration: 30, // 30 seconds
	run: async (payload?: { testData?: string }) => {
		console.log("🚀 Immediate test task started!");
		console.log("Payload:", payload);

		// Simple test of our environment
		const result = {
			success: true,
			message: "Test task executed successfully!",
			timestamp: new Date().toISOString(),
			payload: payload || {},
			environment: process.env['NODE_ENV'] || 'development',
		};

		console.log("✅ Test result:", result);
		return result;
	},
}); 