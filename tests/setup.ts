import { config } from 'dotenv';
import { beforeAll, afterAll, beforeEach, afterEach } from 'vitest';
import { vi } from 'vitest';

// Load environment variables for testing
config({ path: ['.env.test', '.env.local', '.env'] });

// Global test configuration
beforeAll(async () => {
	// Set test environment
	process.env['NODE_ENV'] = 'test';

	// Initialize test logging
	console.log('🧪 Initializing TypeScript test environment...');

	// Check for database connectivity (optional for most tests)
	if (!process.env['DATABASE_URL']) {
		console.log('ℹ️  No DATABASE_URL configured - database-dependent tests will be skipped');
	}

	// Check for optional API keys (for LLM tests)
	const optionalEnvVars = ['DEEPSEEK_API_KEY', 'ALPACA_API_KEY', 'ALPACA_SECRET_KEY'];
	const availableKeys = optionalEnvVars.filter(varName => process.env[varName]);

	if (availableKeys.length > 0) {
		console.log(`🔑 Available API keys: ${availableKeys.join(', ')}`);
	}
});

afterAll(async () => {
	console.log('🧹 Cleaning up test environment...');
});

beforeEach(() => {
	// Clear all mocks before each test
	vi.clearAllMocks();
});

afterEach(() => {
	// Reset all mocks after each test
	vi.resetAllMocks();
});

// Global test utilities
export const testCategories = {
	UNIT: 'unit',
	INTEGRATION: 'integration',
	LLM: 'llm',
	FAST: 'fast'
} as const;

export type TestCategory = typeof testCategories[keyof typeof testCategories];

// Test helper to skip tests based on category
export function skipUnless(condition: boolean, reason: string) {
	if (!condition) {
		console.log(`⏭️  Skipping test: ${reason}`);
		return true;
	}
	return false;
}

// Environment check helpers
export const hasApiKey = (keyName: string): boolean => {
	return Boolean(process.env[keyName]);
};

export const hasDeepseekKey = (): boolean => hasApiKey('DEEPSEEK_API_KEY');
export const hasAlpacaKeys = (): boolean =>
	hasApiKey('ALPACA_API_KEY') && hasApiKey('ALPACA_SECRET_KEY');

// Database helpers
export const hasDatabaseUrl = (): boolean => hasApiKey('DATABASE_URL');

// Test data factories
export const createTestPortfolio = () => ({
	id: 1,
	name: 'Test Portfolio',
	cash_balance: 10000,
	total_value: 15000,
	created_at: new Date().toISOString(),
	updated_at: new Date().toISOString()
});

export const createTestPosition = () => ({
	id: 1,
	portfolio_id: 1,
	symbol: 'AAPL',
	quantity: 100,
	average_cost: 150.00,
	current_price: 155.00,
	created_at: new Date().toISOString(),
	updated_at: new Date().toISOString()
});

// Mock factory for external APIs
export const createMockApiResponse = <T>(data: T) => ({
	data,
	status: 200,
	statusText: 'OK',
	headers: {},
	config: {}
});

console.log('✅ Test setup loaded'); 