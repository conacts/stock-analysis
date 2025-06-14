import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getConfig } from '../../src/utils/config';

describe('Config (unit)', () => {
	beforeEach(() => {
		// Clear environment variables before each test
		vi.resetModules();
	});

	it('should load config with required DATABASE_URL', () => {
		// Mock process.env for this test
		vi.stubEnv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db');

		const config = getConfig();

		expect(config.database_url).toBe('postgresql://test:test@localhost:5432/test_db');
		expect(config.environment).toBe('test'); // Set by vitest
	});

	it('should throw error when DATABASE_URL is missing', () => {
		// Ensure DATABASE_URL is not set
		vi.stubEnv('DATABASE_URL', '');

		expect(() => getConfig()).toThrow('Required environment variable DATABASE_URL is not set');
	});

	it('should use default values for optional environment variables', () => {
		vi.stubEnv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db');
		vi.stubEnv('DEEPSEEK_API_KEY', '');
		vi.stubEnv('ALPACA_API_KEY', '');
		vi.stubEnv('ALPACA_SECRET_KEY', '');

		const config = getConfig();

		expect(config.deepseek_api_key).toBeUndefined();
		expect(config.alpaca_api_key).toBeUndefined();
		expect(config.alpaca_secret_key).toBeUndefined();
		expect(config.alpaca_base_url).toBe('https://paper-api.alpaca.markets');
	});

	it('should load optional API keys when provided', () => {
		vi.stubEnv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db');
		vi.stubEnv('DEEPSEEK_API_KEY', 'test_deepseek_key');
		vi.stubEnv('ALPACA_API_KEY', 'test_alpaca_key');
		vi.stubEnv('ALPACA_SECRET_KEY', 'test_alpaca_secret');
		vi.stubEnv('ALPACA_BASE_URL', 'https://custom-alpaca.com');

		const config = getConfig();

		expect(config.deepseek_api_key).toBe('test_deepseek_key');
		expect(config.alpaca_api_key).toBe('test_alpaca_key');
		expect(config.alpaca_secret_key).toBe('test_alpaca_secret');
		expect(config.alpaca_base_url).toBe('https://custom-alpaca.com');
	});
}); 