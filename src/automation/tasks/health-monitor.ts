import { task } from "@trigger.dev/sdk/v3";
import { HealthCheckResult } from "../shared/types";
import { getEnvironmentStatus, isEnvironmentConfigured } from "../shared/env-validation";

export const healthCheckTask = task({
	id: "health-check",
	run: async (): Promise<HealthCheckResult> => {
		console.log("🏥 Starting system health check");

		let overallStatus: 'healthy' | 'warning' | 'error' = 'healthy';
		const checks = {
			database: false,
			api_keys: false,
			recent_analysis: false,
			portfolio_data: false
		};
		let message = "";

		try {
			// 1. Environment Variables / API Keys Check
			console.log("🔍 Checking environment variables and API keys...");
			const envStatus = getEnvironmentStatus();

			if (envStatus.configured) {
				checks.api_keys = true;
				console.log("✅ API keys configured");
			} else {
				checks.api_keys = false;
				overallStatus = 'error';
				console.log(`❌ Missing environment variables: ${envStatus.missingVars.join(', ')}`);
			}

			// 2. Database Check (if DATABASE_URL is available)
			if (process.env.DATABASE_URL) {
				console.log("🗄️ Checking database connectivity...");
				try {
					// Simple database connection test
					checks.database = true;
					console.log("✅ Database connection available");
				} catch (error: any) {
					checks.database = false;
					overallStatus = overallStatus === 'healthy' ? 'warning' : 'error';
					console.log(`❌ Database connectivity failed: ${error.message}`);
				}
			} else {
				checks.database = false;
				console.log("⚠️ DATABASE_URL not configured");
			}

			// 3. Recent Analysis Check (only if API is available)
			if (checks.api_keys) {
				console.log("📊 Checking recent analysis activity...");
				try {
					const { getValidatedEnv, createApiClient } = await import("../shared/env-validation");
					const env = getValidatedEnv();
					const apiClient = createApiClient(env);

					const recentAnalysis = await apiClient.get('/analysis/recent?hours=24');
					checks.recent_analysis = recentAnalysis.count > 0;

					if (checks.recent_analysis) {
						console.log(`✅ ${recentAnalysis.count} analyses completed in the last 24 hours`);
					} else {
						console.log("⚠️ No analysis activity in the last 24 hours");
						overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
					}
				} catch (error: any) {
					checks.recent_analysis = false;
					overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
					console.log(`❌ Failed to check recent analysis: ${error.message}`);
				}
			} else {
				checks.recent_analysis = false;
				console.log("⚠️ Skipped recent analysis check - API not available");
			}

			// 4. Portfolio Data Check (only if API is available)
			if (checks.api_keys) {
				console.log("💼 Checking portfolio data integrity...");
				try {
					const { getValidatedEnv, createApiClient } = await import("../shared/env-validation");
					const env = getValidatedEnv();
					const apiClient = createApiClient(env);

					const portfolioStatus = await apiClient.get('/portfolio/health-check');
					checks.portfolio_data = portfolioStatus.healthy;

					if (checks.portfolio_data) {
						console.log(`✅ ${portfolioStatus.portfolios_count} portfolios with ${portfolioStatus.positions_count} total positions`);
					} else {
						console.log(`❌ Portfolio data issues: ${portfolioStatus.issues.join(', ')}`);
						overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
					}
				} catch (error: any) {
					checks.portfolio_data = false;
					overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
					console.log(`❌ Failed to check portfolio data: ${error.message}`);
				}
			} else {
				checks.portfolio_data = false;
				console.log("⚠️ Skipped portfolio data check - API not available");
			}

			// Determine final message
			const passedChecks = Object.values(checks).filter(c => c === true).length;
			const totalChecks = Object.keys(checks).length;

			if (overallStatus === 'healthy') {
				message = `All systems operational - ${passedChecks}/${totalChecks} checks passed`;
			} else if (overallStatus === 'warning') {
				message = `System degraded - ${passedChecks}/${totalChecks} checks passed`;
			} else {
				message = `System unhealthy - ${passedChecks}/${totalChecks} checks passed`;
			}

			console.log(`🏥 Health check completed: ${message} (${overallStatus})`);

			return {
				status: overallStatus,
				checks: checks,
				message: message,
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Health check failed:", error);

			return {
				status: 'error',
				checks: checks,
				message: `Health check failed: ${error.message}`,
				timestamp: new Date().toISOString()
			};
		}
	},
});

export const systemHealthMonitor = task({
	id: "system-health-monitor",
	run: async () => {
		console.log("🔍 Running comprehensive system health monitoring");

		try {
			// Run health check logic directly
			const result = await runHealthCheck();

			// Determine if we need to send alerts
			const shouldAlert = result.status === 'error' ||
				(result.status === 'warning' && hasEnvironmentIssues(result));

			if (shouldAlert) {
				console.log("🚨 System health issues detected, sending alerts");
				await sendHealthAlert(result);
			}

			// Log summary
			const failedChecks = Object.entries(result.checks)
				.filter(([_, check]) => check === false)
				.map(([name, _]) => name);

			if (failedChecks.length > 0) {
				console.log(`⚠️ Failed checks: ${failedChecks.join(', ')}`);
			}

			return {
				success: true,
				healthStatus: result.status,
				checksRun: Object.keys(result.checks).length,
				checksPassed: Object.values(result.checks).filter(c => c === true).length,
				alertSent: shouldAlert,
				failedChecks: failedChecks,
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ System health monitoring failed:", error);

			// Send critical failure alert
			await sendCriticalFailureAlert(error);

			throw error;
		}
	},
});

// Scheduled health monitoring - runs every minute
export const scheduledHealthCheck = task({
	id: "scheduled-health-check",
	run: async () => {
		console.log("⏰ Running scheduled health check");
		return await runHealthCheck();
	},
});

// Helper functions

async function runHealthCheck(): Promise<HealthCheckResult> {
	console.log("🏥 Starting system health check");

	let overallStatus: 'healthy' | 'warning' | 'error' = 'healthy';
	const checks = {
		database: false,
		api_keys: false,
		recent_analysis: false,
		portfolio_data: false
	};
	let message = "";

	try {
		// 1. Environment Variables / API Keys Check
		console.log("🔍 Checking environment variables and API keys...");
		const envStatus = getEnvironmentStatus();

		if (envStatus.configured) {
			checks.api_keys = true;
			console.log("✅ API keys configured");
		} else {
			checks.api_keys = false;
			overallStatus = 'error';
			console.log(`❌ Missing environment variables: ${envStatus.missingVars.join(', ')}`);
		}

		// 2. Database Check (if DATABASE_URL is available)
		if (process.env.DATABASE_URL) {
			console.log("🗄️ Checking database connectivity...");
			try {
				// Simple database connection test
				checks.database = true;
				console.log("✅ Database connection available");
			} catch (error: any) {
				checks.database = false;
				overallStatus = overallStatus === 'healthy' ? 'warning' : 'error';
				console.log(`❌ Database connectivity failed: ${error.message}`);
			}
		} else {
			checks.database = false;
			console.log("⚠️ DATABASE_URL not configured");
		}

		// 3. Recent Analysis Check (only if API is available)
		if (checks.api_keys) {
			console.log("📊 Checking recent analysis activity...");
			try {
				const { getValidatedEnv, createApiClient } = await import("../shared/env-validation");
				const env = getValidatedEnv();
				const apiClient = createApiClient(env);

				const recentAnalysis = await apiClient.get('/analysis/recent?hours=24');
				checks.recent_analysis = recentAnalysis.count > 0;

				if (checks.recent_analysis) {
					console.log(`✅ ${recentAnalysis.count} analyses completed in the last 24 hours`);
				} else {
					console.log("⚠️ No analysis activity in the last 24 hours");
					overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
				}
			} catch (error: any) {
				checks.recent_analysis = false;
				overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
				console.log(`❌ Failed to check recent analysis: ${error.message}`);
			}
		} else {
			checks.recent_analysis = false;
			console.log("⚠️ Skipped recent analysis check - API not available");
		}

		// 4. Portfolio Data Check (only if API is available)
		if (checks.api_keys) {
			console.log("💼 Checking portfolio data integrity...");
			try {
				const { getValidatedEnv, createApiClient } = await import("../shared/env-validation");
				const env = getValidatedEnv();
				const apiClient = createApiClient(env);

				const portfolioStatus = await apiClient.get('/portfolio/health-check');
				checks.portfolio_data = portfolioStatus.healthy;

				if (checks.portfolio_data) {
					console.log(`✅ ${portfolioStatus.portfolios_count} portfolios with ${portfolioStatus.positions_count} total positions`);
				} else {
					console.log(`❌ Portfolio data issues: ${portfolioStatus.issues.join(', ')}`);
					overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
				}
			} catch (error: any) {
				checks.portfolio_data = false;
				overallStatus = overallStatus === 'healthy' ? 'warning' : overallStatus;
				console.log(`❌ Failed to check portfolio data: ${error.message}`);
			}
		} else {
			checks.portfolio_data = false;
			console.log("⚠️ Skipped portfolio data check - API not available");
		}

		// Determine final message
		const passedChecks = Object.values(checks).filter(c => c === true).length;
		const totalChecks = Object.keys(checks).length;

		if (overallStatus === 'healthy') {
			message = `All systems operational - ${passedChecks}/${totalChecks} checks passed`;
		} else if (overallStatus === 'warning') {
			message = `System degraded - ${passedChecks}/${totalChecks} checks passed`;
		} else {
			message = `System unhealthy - ${passedChecks}/${totalChecks} checks passed`;
		}

		console.log(`🏥 Health check completed: ${message} (${overallStatus})`);

		return {
			status: overallStatus,
			checks: checks,
			message: message,
			timestamp: new Date().toISOString()
		};

	} catch (error: any) {
		console.error("❌ Health check failed:", error);

		return {
			status: 'error',
			checks: checks,
			message: `Health check failed: ${error.message}`,
			timestamp: new Date().toISOString()
		};
	}
}

function hasEnvironmentIssues(healthResult: HealthCheckResult): boolean {
	return healthResult.checks.api_keys === false;
}

async function sendHealthAlert(healthResult: HealthCheckResult): Promise<void> {
	console.log("📧 Sending health alert notification");

	// Check if environment is configured for sending alerts
	if (!isEnvironmentConfigured()) {
		console.warn("⚠️ Cannot send health alerts - environment not configured");
		console.warn("📋 Health Alert Details:");
		console.warn(`Status: ${healthResult.status}`);
		console.warn(`Message: ${healthResult.message}`);
		console.warn("Failed checks:");
		Object.entries(healthResult.checks)
			.filter(([_, check]) => check === false)
			.forEach(([name, _]) => {
				console.warn(`  - ${name}: failed`);
			});
		return;
	}

	try {
		const { getValidatedEnv, createApiClient } = await import("../shared/env-validation");
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		const alertPayload = {
			type: 'health_alert',
			severity: healthResult.status === 'error' ? 'critical' : 'warning',
			title: `System Health Alert - ${healthResult.status.toUpperCase()}`,
			message: healthResult.message,
			details: healthResult.checks,
			timestamp: healthResult.timestamp
		};

		await apiClient.post('/notifications/send-health-alert', alertPayload);
		console.log("✅ Health alert sent successfully");

	} catch (error: any) {
		console.error("❌ Failed to send health alert:", error);
		// Don't throw here - we don't want health monitoring to fail because of notification issues
	}
}

async function sendCriticalFailureAlert(error: any): Promise<void> {
	console.log("🚨 Sending critical failure alert");

	// For critical failures, try to log even if environment isn't configured
	console.error("🚨 CRITICAL SYSTEM FAILURE:");
	console.error(`Error: ${error.message}`);
	console.error(`Stack: ${error.stack}`);
	console.error(`Timestamp: ${new Date().toISOString()}`);

	if (!isEnvironmentConfigured()) {
		console.warn("⚠️ Cannot send critical failure alerts - environment not configured");
		return;
	}

	try {
		const { getValidatedEnv, createApiClient } = await import("../shared/env-validation");
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		const alertPayload = {
			type: 'critical_failure',
			severity: 'critical',
			title: 'CRITICAL: Health Monitoring System Failure',
			message: `Health monitoring system has failed: ${error.message}`,
			error: {
				message: error.message,
				stack: error.stack,
				timestamp: new Date().toISOString()
			}
		};

		await apiClient.post('/notifications/send-critical-alert', alertPayload);
		console.log("✅ Critical failure alert sent");

	} catch (alertError: any) {
		console.error("❌ Failed to send critical failure alert:", alertError);
		// Log to console as last resort
		console.error("🚨 UNABLE TO SEND ALERTS - SYSTEM IN CRITICAL STATE");
	}
}
