import { exec } from 'child_process';
import { promisify } from 'util';
import type { HealthCheckResult, DatabaseHealth, EnvironmentHealth, EnvironmentVariables } from './types';

const execAsync = promisify(exec);

/**
 * Execute a Python script using uv
 */
export async function runPythonScript(
	scriptPath: string,
	args: string[] = [],
	options: { timeout?: number; cwd?: string } = {}
): Promise<{ stdout: string; stderr: string }> {
	const { timeout = 300000, cwd = process.cwd() } = options;

	const command = `uv run python ${scriptPath} ${args.join(' ')}`;

	try {
		const result = await execAsync(command, {
			timeout,
			cwd,
			env: { ...process.env }
		});

		return result;
	} catch (error: any) {
		throw new Error(`Python script failed: ${error.message}`);
	}
}

/**
 * Check if we're in market hours (9:30 AM - 4:00 PM ET)
 */
export function isMarketHours(): boolean {
	const now = new Date();
	const et = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));

	const hour = et.getHours();
	const minute = et.getMinutes();
	const dayOfWeek = et.getDay();

	// Weekend check
	if (dayOfWeek === 0 || dayOfWeek === 6) {
		return false;
	}

	// Market hours: 9:30 AM - 4:00 PM ET
	const marketOpen = 9 * 60 + 30; // 9:30 AM in minutes
	const marketClose = 16 * 60; // 4:00 PM in minutes
	const currentTime = hour * 60 + minute;

	return currentTime >= marketOpen && currentTime < marketClose;
}

/**
 * Check if it's a trading day (weekday, not holiday)
 */
export function isTradingDay(): boolean {
	const now = new Date();
	const et = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
	const dayOfWeek = et.getDay();

	// Basic check - weekdays only (doesn't account for holidays)
	return dayOfWeek >= 1 && dayOfWeek <= 5;
}

/**
 * Get the current date in YYYY-MM-DD format (ET timezone)
 */
export function getCurrentDateET(): string {
	const now = new Date();
	const et = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));

	return et.toISOString().split('T')[0];
}

/**
 * Perform comprehensive health checks
 */
export async function performHealthCheck(): Promise<HealthCheckResult> {
	const timestamp = new Date().toISOString();

	const [databaseHealth, pythonHealth, uvHealth, envVars] = await Promise.allSettled([
		checkDatabaseHealth(),
		checkPythonEnvironment(),
		checkUvEnvironment(),
		checkEnvironmentVariables()
	]);

	const checks = {
		database: databaseHealth.status === 'fulfilled' ? databaseHealth.value : { status: 'unhealthy' as const, timestamp, error: 'Check failed' },
		python: pythonHealth.status === 'fulfilled' ? pythonHealth.value : { status: 'unhealthy' as const, version: 'unknown', error: 'Check failed' },
		uv: uvHealth.status === 'fulfilled' ? uvHealth.value : { status: 'unhealthy' as const, version: 'unknown', error: 'Check failed' },
		environment: envVars.status === 'fulfilled' ? envVars.value : { database_url: false, deepseek_key: false }
	};

	// Determine overall status
	let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';

	if (checks.database.status === 'unhealthy' || !checks.environment.database_url) {
		status = 'unhealthy';
	} else if (checks.python.status === 'unhealthy' || checks.uv.status === 'unhealthy' || !checks.environment.deepseek_key) {
		status = 'degraded';
	}

	return {
		status,
		timestamp,
		checks
	};
}

async function checkDatabaseHealth(): Promise<DatabaseHealth> {
	const timestamp = new Date().toISOString();

	try {
		// Simple database connectivity check
		const result = await runPythonScript('scripts/test_db_connection.py', [], { timeout: 10000 });

		if (result.stderr && result.stderr.includes('error')) {
			return {
				status: 'unhealthy',
				timestamp,
				error: result.stderr
			};
		}

		return {
			status: 'healthy',
			timestamp
		};
	} catch (error: any) {
		return {
			status: 'unhealthy',
			timestamp,
			error: error.message
		};
	}
}

async function checkPythonEnvironment(): Promise<EnvironmentHealth> {
	try {
		const result = await execAsync('python --version', { timeout: 5000 });
		return {
			status: 'healthy',
			version: result.stdout.trim()
		};
	} catch (error: any) {
		return {
			status: 'unhealthy',
			version: 'unknown',
			error: error.message
		};
	}
}

async function checkUvEnvironment(): Promise<EnvironmentHealth> {
	try {
		const result = await execAsync('uv --version', { timeout: 5000 });
		return {
			status: 'healthy',
			version: result.stdout.trim()
		};
	} catch (error: any) {
		return {
			status: 'unhealthy',
			version: 'unknown',
			error: error.message
		};
	}
}

async function checkEnvironmentVariables(): Promise<EnvironmentVariables> {
	return {
		database_url: !!process.env.DATABASE_URL,
		deepseek_key: !!process.env.DEEPSEEK_API_KEY,
		slack_webhook: !!process.env.SLACK_WEBHOOK_URL
	};
}

/**
 * Format currency values
 */
export function formatCurrency(value: number, currency = 'USD'): string {
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency
	}).format(value);
}

/**
 * Format percentage values
 */
export function formatPercentage(value: number, decimals = 2): string {
	return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Sleep utility for delays
 */
export function sleep(ms: number): Promise<void> {
	return new Promise(resolve => setTimeout(resolve, ms));
}
