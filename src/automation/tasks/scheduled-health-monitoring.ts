import { schedules } from "@trigger.dev/sdk/v3";
import { getValidatedEnv, createApiClient } from "../shared/env-validation";
import { HealthCheckResult } from "../shared/types";

// System Health Check - Runs every 15 minutes during business hours
export const systemHealthCheckScheduled = schedules.task({
	id: "system-health-check-scheduled",
	cron: {
		pattern: "*/15 * * * *", // Every 15 minutes
		timezone: "UTC"
	},
	run: async (payload) => {
		console.log(`🏥 Starting scheduled system health check at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			const healthResult = await runComprehensiveHealthCheck();

			// Determine if we need to send alerts
			const shouldAlert = healthResult.status === 'error' ||
				(healthResult.status === 'warning' && hasEnvironmentIssues(healthResult));

			if (shouldAlert) {
				console.log("🚨 System health issues detected, sending alerts");
				await sendHealthAlert(healthResult);
			}

			// Log summary
			const failedChecks = Object.entries(healthResult.checks)
				.filter(([_, check]) => check === false)
				.map(([name, _]) => name);

			if (failedChecks.length > 0) {
				console.log(`⚠️ Failed checks: ${failedChecks.join(', ')}`);
			}

			console.log(`✅ Health check completed: ${healthResult.status} - ${healthResult.message}`);

			return {
				success: true,
				healthStatus: healthResult.status,
				checksRun: Object.keys(healthResult.checks).length,
				checksPassed: Object.values(healthResult.checks).filter(c => c === true).length,
				alertSent: shouldAlert,
				failedChecks: failedChecks,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Scheduled health check failed:", error);

			// Send critical failure alert
			await sendCriticalFailureAlert(error);

			throw error;
		}
	},
});

// Daily Health Summary - Runs every day at 6:00 AM EST
export const dailyHealthSummaryScheduled = schedules.task({
	id: "daily-health-summary-scheduled",
	cron: {
		pattern: "0 6 * * *", // 6:00 AM daily
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`📊 Starting scheduled daily health summary at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			// Run comprehensive health check
			const currentHealth = await runComprehensiveHealthCheck();

			// Get health history for the last 24 hours
			const healthHistory = await getHealthHistory(24);

			// Calculate uptime and reliability metrics
			const metrics = calculateHealthMetrics(healthHistory);

			// Generate daily health report
			const report = await generateDailyHealthReport(currentHealth, metrics);

			// Send daily health summary
			await sendDailyHealthSummary(report);

			console.log(`✅ Daily health summary completed - System uptime: ${metrics.uptime.toFixed(2)}%`);

			return {
				success: true,
				currentHealthStatus: currentHealth.status,
				systemUptime: metrics.uptime,
				averageResponseTime: metrics.averageResponseTime,
				totalChecksRun: metrics.totalChecks,
				issuesDetected: metrics.issuesCount,
				reportGenerated: true,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Daily health summary failed:", error);
			throw error;
		}
	},
});

// Weekly Health Analysis - Runs every Sunday at 7:00 AM EST
export const weeklyHealthAnalysisScheduled = schedules.task({
	id: "weekly-health-analysis-scheduled",
	cron: {
		pattern: "0 7 * * 0", // 7:00 AM on Sundays
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`📈 Starting scheduled weekly health analysis at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		try {
			// Get health history for the last 7 days
			const weeklyHealthHistory = await getHealthHistory(168); // 7 days * 24 hours

			// Analyze trends and patterns
			const trends = analyzeHealthTrends(weeklyHealthHistory);

			// Generate performance insights
			const insights = generatePerformanceInsights(trends);

			// Create weekly health report
			const weeklyReport = await generateWeeklyHealthReport(trends, insights);

			// Send weekly health analysis
			await sendWeeklyHealthAnalysis(weeklyReport);

			console.log(`✅ Weekly health analysis completed - ${insights.recommendations.length} recommendations generated`);

			return {
				success: true,
				weeklyUptime: trends.averageUptime,
				performanceTrend: trends.performanceTrend,
				recommendationsGenerated: insights.recommendations.length,
				criticalIssuesIdentified: insights.criticalIssues.length,
				reportGenerated: true,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Weekly health analysis failed:", error);
			throw error;
		}
	},
});

// Helper functions

async function runComprehensiveHealthCheck(): Promise<HealthCheckResult> {
	console.log("🏥 Starting comprehensive system health check");

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
		const { getEnvironmentStatus } = await import("../shared/env-validation");
		const envStatus = getEnvironmentStatus();

		if (envStatus.configured) {
			checks.api_keys = true;
			console.log("✅ API keys configured");
		} else {
			checks.api_keys = false;
			overallStatus = 'error';
			console.log(`❌ Missing environment variables: ${envStatus.missingVars.join(', ')}`);
		}

		// 2. Database Check
		if (process.env.DATABASE_URL) {
			console.log("🗄️ Checking database connectivity...");
			try {
				const env = getValidatedEnv();
				const apiClient = createApiClient(env);
				await apiClient.get('/health');
				checks.database = true;
				console.log("✅ Database connection healthy");
			} catch (error: any) {
				checks.database = false;
				overallStatus = overallStatus === 'healthy' ? 'warning' : 'error';
				console.log(`❌ Database connectivity failed: ${error.message}`);
			}
		} else {
			checks.database = false;
			console.log("⚠️ DATABASE_URL not configured");
		}

		// 3. Recent Analysis Check
		if (checks.api_keys) {
			console.log("📊 Checking recent analysis activity...");
			try {
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

		// 4. Portfolio Data Check
		if (checks.api_keys) {
			console.log("💼 Checking portfolio data integrity...");
			try {
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
	return !healthResult.checks.api_keys || !healthResult.checks.database;
}

async function sendHealthAlert(healthResult: HealthCheckResult): Promise<void> {
	try {
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		const alertMessage = `🚨 System Health Alert: ${healthResult.status.toUpperCase()}\n\n${healthResult.message}\n\nFailed checks: ${Object.entries(healthResult.checks).filter(([_, check]) => !check).map(([name, _]) => name).join(', ')}`;

		await apiClient.post('/alerts/send', {
			type: 'system_health',
			severity: healthResult.status === 'error' ? 'critical' : 'warning',
			message: alertMessage,
			channels: ['slack', 'email']
		});

		console.log("📧 Health alert sent successfully");
	} catch (error: any) {
		console.error("❌ Failed to send health alert:", error);
	}
}

async function sendCriticalFailureAlert(error: any): Promise<void> {
	try {
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		const alertMessage = `🚨 CRITICAL: System health monitoring failed\n\nError: ${error.message}\n\nImmediate attention required!`;

		await apiClient.post('/alerts/send', {
			type: 'system_critical',
			severity: 'critical',
			message: alertMessage,
			channels: ['slack', 'email']
		});

		console.log("📧 Critical failure alert sent");
	} catch (alertError: any) {
		console.error("❌ Failed to send critical failure alert:", alertError);
	}
}

async function getHealthHistory(hours: number): Promise<any[]> {
	try {
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		const response = await apiClient.get(`/health/history?hours=${hours}`);
		return response.history || [];
	} catch (error: any) {
		console.error("❌ Failed to get health history:", error);
		return [];
	}
}

function calculateHealthMetrics(healthHistory: any[]): {
	uptime: number;
	averageResponseTime: number;
	totalChecks: number;
	issuesCount: number;
} {
	if (healthHistory.length === 0) {
		return {
			uptime: 100,
			averageResponseTime: 0,
			totalChecks: 0,
			issuesCount: 0
		};
	}

	const healthyChecks = healthHistory.filter(h => h.status === 'healthy').length;
	const uptime = (healthyChecks / healthHistory.length) * 100;
	const averageResponseTime = healthHistory.reduce((sum, h) => sum + (h.responseTime || 0), 0) / healthHistory.length;
	const issuesCount = healthHistory.filter(h => h.status === 'error').length;

	return {
		uptime,
		averageResponseTime,
		totalChecks: healthHistory.length,
		issuesCount
	};
}

async function generateDailyHealthReport(currentHealth: HealthCheckResult, metrics: any): Promise<any> {
	return {
		date: new Date().toISOString().split('T')[0],
		currentStatus: currentHealth.status,
		uptime: metrics.uptime,
		totalChecks: metrics.totalChecks,
		issuesDetected: metrics.issuesCount,
		averageResponseTime: metrics.averageResponseTime,
		recommendations: generateHealthRecommendations(currentHealth, metrics)
	};
}

async function sendDailyHealthSummary(report: any): Promise<void> {
	try {
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		await apiClient.post('/reports/daily-health-summary', report);
		console.log("📧 Daily health summary sent");
	} catch (error: any) {
		console.error("❌ Failed to send daily health summary:", error);
	}
}

function analyzeHealthTrends(weeklyHistory: any[]): any {
	// Analyze weekly trends
	const dailyAverages: number[] = [];
	for (let i = 0; i < 7; i++) {
		const dayStart = i * 24;
		const dayEnd = (i + 1) * 24;
		const dayData = weeklyHistory.slice(dayStart, dayEnd);

		if (dayData.length > 0) {
			const healthyCount = dayData.filter(h => h.status === 'healthy').length;
			dailyAverages.push(healthyCount / dayData.length);
		}
	}

	const averageUptime = dailyAverages.reduce((sum, avg) => sum + avg, 0) / dailyAverages.length * 100;
	const performanceTrend = dailyAverages.length > 1 ?
		(dailyAverages[dailyAverages.length - 1] > dailyAverages[0] ? 'improving' : 'declining') : 'stable';

	return {
		averageUptime,
		performanceTrend,
		dailyAverages
	};
}

function generatePerformanceInsights(trends: any): any {
	const recommendations: string[] = [];
	const criticalIssues: string[] = [];

	if (trends.averageUptime < 95) {
		criticalIssues.push('System uptime below 95%');
		recommendations.push('Investigate recurring system issues');
	}

	if (trends.performanceTrend === 'declining') {
		recommendations.push('Monitor system performance closely');
	}

	return {
		recommendations,
		criticalIssues
	};
}

async function generateWeeklyHealthReport(trends: any, insights: any): Promise<any> {
	return {
		weekStarting: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
		weekEnding: new Date().toISOString().split('T')[0],
		averageUptime: trends.averageUptime,
		performanceTrend: trends.performanceTrend,
		recommendations: insights.recommendations,
		criticalIssues: insights.criticalIssues
	};
}

async function sendWeeklyHealthAnalysis(report: any): Promise<void> {
	try {
		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		await apiClient.post('/reports/weekly-health-analysis', report);
		console.log("📧 Weekly health analysis sent");
	} catch (error: any) {
		console.error("❌ Failed to send weekly health analysis:", error);
	}
}

function generateHealthRecommendations(currentHealth: HealthCheckResult, metrics: any): string[] {
	const recommendations: string[] = [];

	if (!currentHealth.checks.database) {
		recommendations.push('Check database connectivity and configuration');
	}

	if (!currentHealth.checks.api_keys) {
		recommendations.push('Verify all required API keys are configured');
	}

	if (!currentHealth.checks.recent_analysis) {
		recommendations.push('Investigate why no recent analysis has been performed');
	}

	if (metrics.uptime < 99) {
		recommendations.push('Investigate system reliability issues');
	}

	return recommendations;
}
