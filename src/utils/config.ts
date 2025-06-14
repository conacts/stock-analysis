import { config } from 'dotenv';
import { Config } from '../types';

// Load environment variables
config();

export const getConfig = (): Config => {
	const requiredEnvVar = (name: string): string => {
		const value = process.env[name];
		if (!value) {
			throw new Error(`Required environment variable ${name} is not set`);
		}
		return value;
	};

	const optionalEnvVar = (name: string): string | undefined => {
		const value = process.env[name];
		return value && value.trim() !== '' ? value : undefined;
	};

	const config: Config = {
		database_url: requiredEnvVar('DATABASE_URL'),
		deepseek_api_key: optionalEnvVar('DEEPSEEK_API_KEY'),
		alpaca_api_key: optionalEnvVar('ALPACA_API_KEY'),
		alpaca_secret_key: optionalEnvVar('ALPACA_SECRET_KEY'),
		alpaca_base_url: optionalEnvVar('ALPACA_BASE_URL') || 'https://paper-api.alpaca.markets',
		environment: (process.env['NODE_ENV'] as Config['environment']) || 'development',
	};
	return config;
};
