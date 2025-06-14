import { describe, it, expect } from 'vitest';
import { PortfolioSchema, DailyAnalysisSchema, SwarmPortfolioConfigSchema } from '../../src/database/models';

describe('TypeScript Core Implementation (unit)', () => {
	describe('Database Models', () => {
		it('should validate Portfolio schema correctly', () => {
			const validPortfolio = {
				name: 'Test Portfolio',
				description: 'A test portfolio',
				portfolio_type: 'personal',
				base_currency: 'USD',
				is_active: true,
			};

			const result = PortfolioSchema.safeParse(validPortfolio);
			expect(result.success).toBe(true);

			if (result.success) {
				expect(result.data.name).toBe('Test Portfolio');
				expect(result.data.portfolio_type).toBe('personal');
				expect(result.data.base_currency).toBe('USD');
			}
		});

		it('should apply default values for Portfolio', () => {
			const minimalPortfolio = {
				name: 'Minimal Portfolio',
			};

			const result = PortfolioSchema.parse(minimalPortfolio);
			expect(result.portfolio_type).toBe('personal');
			expect(result.base_currency).toBe('USD');
			expect(result.is_active).toBe(true);
		});

		it('should reject invalid Portfolio data', () => {
			const invalidPortfolio = {
				// Missing required 'name' field
				description: 'A test portfolio',
			};

			const result = PortfolioSchema.safeParse(invalidPortfolio);
			expect(result.success).toBe(false);
		});

		it('should validate DailyAnalysis schema correctly', () => {
			const validAnalysis = {
				date: '2024-01-15',
				symbol: 'AAPL',
				analysis_data: {
					score: 85,
					trend: 'bullish',
					indicators: ['RSI', 'MACD'],
					fundamentals: {
						pe_ratio: 25.5,
						revenue_growth: 0.08
					}
				},
				composite_score: 8.5,
				rating: 'BUY',
				confidence: 'HIGH',
			};

			const result = DailyAnalysisSchema.safeParse(validAnalysis);
			expect(result.success).toBe(true);

			if (result.success) {
				expect(result.data.symbol).toBe('AAPL');
				expect(result.data.composite_score).toBe(8.5);
				expect(result.data.analysis_data['score']).toBe(85);
			}
		});

		it('should validate SwarmPortfolioConfig schema correctly', () => {
			const validConfig = {
				portfolio_id: 'portfolio_123',
				name: 'AI Trading Portfolio',
				symbols: {
					'AAPL': { weight: 0.3, target_allocation: 30 },
					'TSLA': { weight: 0.2, target_allocation: 20 },
					'NVDA': { weight: 0.25, target_allocation: 25 }
				},
				risk_tolerance: 'moderate',
				max_position_size_pct: 10.0,
				max_sector_exposure_pct: 25.0,
				cash_reserve_pct: 15.0,
				trading_enabled: true,
				rebalance_frequency: 'weekly',
			};

			const result = SwarmPortfolioConfigSchema.safeParse(validConfig);
			expect(result.success).toBe(true);

			if (result.success) {
				expect(result.data.portfolio_id).toBe('portfolio_123');
				expect(result.data.symbols['AAPL'].weight).toBe(0.3);
				expect(result.data.max_position_size_pct).toBe(10.0);
			}
		});

		it('should apply default values for SwarmPortfolioConfig', () => {
			const minimalConfig = {
				portfolio_id: 'test_portfolio',
				name: 'Test Portfolio',
				symbols: { 'AAPL': { weight: 1.0 } },
				risk_tolerance: 'moderate',
			};

			const result = SwarmPortfolioConfigSchema.parse(minimalConfig);
			expect(result.max_position_size_pct).toBe(5.0);
			expect(result.max_sector_exposure_pct).toBe(20.0);
			expect(result.cash_reserve_pct).toBe(10.0);
			expect(result.trading_enabled).toBe(true);
			expect(result.rebalance_frequency).toBe('weekly');
			expect(result.is_active).toBe(true);
		});
	});

	describe('Type System Validation', () => {
		it('should enforce strict typing for Portfolio fields', () => {
			// Test that TypeScript types are working correctly
			const portfolio = PortfolioSchema.parse({
				name: 'Test Portfolio',
			});

			// These should be properly typed
			expect(typeof portfolio.name).toBe('string');
			expect(typeof portfolio.is_active).toBe('boolean');
			expect(typeof portfolio.portfolio_type).toBe('string');
		});

		it('should handle complex nested objects in analysis_data', () => {
			const complexAnalysis = {
				date: '2024-01-15',
				symbol: 'AAPL',
				analysis_data: {
					technical: {
						rsi: 65.5,
						macd: { signal: 'bullish', histogram: 0.25 },
						moving_averages: {
							sma_20: 150.25,
							sma_50: 148.75,
							ema_12: 151.00
						}
					},
					fundamental: {
						pe_ratio: 25.5,
						peg_ratio: 1.2,
						debt_to_equity: 0.3,
						roe: 0.28
					},
					sentiment: {
						news_score: 0.75,
						social_sentiment: 'positive',
						analyst_ratings: {
							buy: 15,
							hold: 8,
							sell: 2
						}
					}
				},
				composite_score: 8.7,
				rating: 'BUY',
				confidence: 'HIGH',
			};

			const result = DailyAnalysisSchema.safeParse(complexAnalysis);
			expect(result.success).toBe(true);

			if (result.success) {
				expect(result.data.analysis_data['technical']['rsi']).toBe(65.5);
				expect(result.data.analysis_data['fundamental']['pe_ratio']).toBe(25.5);
				expect(result.data.analysis_data['sentiment']['news_score']).toBe(0.75);
			}
		});

		it('should validate string length constraints', () => {
			// Test symbol length constraint (max 10 characters)
			const longSymbolAnalysis = {
				date: '2024-01-15',
				symbol: 'VERYLONGSYMBOL', // 14 characters - should fail
				analysis_data: { score: 85 },
			};

			const result = DailyAnalysisSchema.safeParse(longSymbolAnalysis);
			expect(result.success).toBe(false);
		});

		it('should validate required vs optional fields', () => {
			// Test minimal required fields
			const minimalAnalysis = {
				date: '2024-01-15',
				symbol: 'AAPL',
				analysis_data: { basic: true },
			};

			const result = DailyAnalysisSchema.safeParse(minimalAnalysis);
			expect(result.success).toBe(true);

			if (result.success) {
				expect(result.data.composite_score).toBeUndefined();
				expect(result.data.rating).toBeUndefined();
				expect(result.data.confidence).toBeUndefined();
			}
		});
	});

	describe('Schema Composition and Reusability', () => {
		it('should handle multiple schema validations consistently', () => {
			const testData = [
				{
					schema: PortfolioSchema,
					valid: { name: 'Portfolio 1' },
					invalid: { description: 'Missing name' }
				},
				{
					schema: DailyAnalysisSchema,
					valid: { date: '2024-01-15', symbol: 'AAPL', analysis_data: {} },
					invalid: { symbol: 'AAPL', analysis_data: {} } // Missing date
				}
			];

			testData.forEach(({ schema, valid, invalid }) => {
				expect(schema.safeParse(valid).success).toBe(true);
				expect(schema.safeParse(invalid).success).toBe(false);
			});
		});

		it('should maintain type safety across schema transformations', () => {
			const portfolioData = {
				name: 'Test Portfolio',
				description: 'Test Description',
			};

			const parsed = PortfolioSchema.parse(portfolioData);

			// Verify that parsed data maintains proper types
			expect(parsed.name).toBe('Test Portfolio');
			expect(parsed.description).toBe('Test Description');
			expect(parsed.portfolio_type).toBe('personal'); // Default value

			// TypeScript should enforce these types at compile time
			const name: string = parsed.name;
			const isActive: boolean = parsed.is_active;

			expect(typeof name).toBe('string');
			expect(typeof isActive).toBe('boolean');
		});
	});
}); 