// Simple environment variable access - Trigger.dev handles injection
export const DATABASE_URL = process.env['DATABASE_URL']!;
export const DEEPSEEK_API_KEY = process.env['DEEPSEEK_API_KEY'];
export const ALPACA_API_KEY = process.env['ALPACA_API_KEY'];
export const ALPACA_SECRET_KEY = process.env['ALPACA_SECRET_KEY'];
export const ALPACA_BASE_URL = process.env['ALPACA_BASE_URL'] || 'https://paper-api.alpaca.markets';
