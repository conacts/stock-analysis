/**
 * Environment Configuration
 *
 * Centralized environment variable management.
 * All environment variables should be accessed through this module.
 */

// Simple environment variable access - Trigger.dev handles injection
export const DATABASE_URL = process.env['DATABASE_URL']!;
export const DEEPSEEK_API_KEY = process.env['DEEPSEEK_API_KEY'];
export const ANTHROPIC_API_KEY = process.env['ANTHROPIC_API_KEY'];
export const OPENAI_API_KEY = process.env['OPENAI_API_KEY'];
export const ALPACA_API_KEY = process.env['ALPACA_API_KEY'];
export const ALPACA_SECRET_KEY = process.env['ALPACA_SECRET_KEY'];
export const ALPACA_BASE_URL = process.env['ALPACA_BASE_URL'] || 'https://paper-api.alpaca.markets';

// Web scraping and data extraction
export const FIRECRAWL_API_KEY = process.env['FIRECRAWL_API_KEY'];

// Structured config object for easy access
export const environment = {
  DATABASE_URL,
  DEEPSEEK_API_KEY,
  ANTHROPIC_API_KEY,
  OPENAI_API_KEY,
  ALPACA_API_KEY,
  ALPACA_SECRET_KEY,
  ALPACA_BASE_URL,
  FIRECRAWL_API_KEY,
} as const;
