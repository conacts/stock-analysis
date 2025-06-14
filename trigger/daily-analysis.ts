import { task } from "@trigger.dev/sdk/v3";
import { python } from "@trigger.dev/python";

export const dailyAnalysis = task({
	id: "daily-analysis",
	run: async (payload: { symbols?: string[]; maxStocks?: number }) => {
		console.log("🚀 Starting daily stock analysis...");

		const symbols = payload.symbols || ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"];
		const maxStocks = payload.maxStocks || 10;

		try {
			// Run the master stock analyzer
			console.log("📊 Running stock analysis...");
			const analysisResult = await python.runScript("./scripts/master_stock_analyzer.py", [
				"--symbols", symbols.join(","),
				"--max-stocks", maxStocks.toString(),
				"--output-format", "json"
			], {
				env: {
					DEEPSEEK_API_KEY: process.env.DEEPSEEK_API_KEY,
					DATABASE_URL: process.env.DATABASE_URL,
					SLACK_WEBHOOK_URL: process.env.SLACK_WEBHOOK_URL,
				}
			});

			if (analysisResult.exitCode !== 0) {
				throw new Error(`Analysis failed: ${analysisResult.stderr}`);
			}

			// Parse the analysis results
			const results = JSON.parse(analysisResult.stdout);
			console.log(`✅ Analysis completed for ${results.length} stocks`);

			// Send alerts for high-confidence signals
			const highConfidenceSignals = results.filter((stock: any) =>
				stock.score > 70 || stock.score < 30
			);

			if (highConfidenceSignals.length > 0) {
				console.log("🚨 Sending alerts for high-confidence signals...");
				await python.runScript("./scripts/alert_manager.py", [
					"--signals", JSON.stringify(highConfidenceSignals),
					"--type", "daily-analysis"
				], {
					env: {
						SLACK_WEBHOOK_URL: process.env.SLACK_WEBHOOK_URL,
					}
				});
			}

			return {
				success: true,
				analysisCount: results.length,
				highConfidenceSignals: highConfidenceSignals.length,
				topPicks: results.slice(0, 5).map((stock: any) => ({
					symbol: stock.symbol,
					score: stock.score,
					rating: stock.rating
				}))
			};

		} catch (error) {
			console.error("❌ Daily analysis failed:", error);

			// Send error notification
			await python.runScript("./scripts/alert_manager.py", [
				"--error", error.message,
				"--type", "system-error"
			], {
				env: {
					SLACK_WEBHOOK_URL: process.env.SLACK_WEBHOOK_URL,
				}
			});

			throw error;
		}
	},
});

export const portfolioMonitoring = task({
	id: "portfolio-monitoring",
	run: async (payload: { portfolioId?: string }) => {
		console.log("📈 Starting portfolio monitoring...");

		const portfolioId = payload.portfolioId || "default";

		try {
			// Run portfolio analysis
			console.log("🔍 Analyzing portfolio performance...");
			const portfolioResult = await python.runScript("./scripts/portfolio_manager.py", [
				"--portfolio-id", portfolioId,
				"--action", "analyze",
				"--output-format", "json"
			], {
				env: {
					DATABASE_URL: process.env.DATABASE_URL,
					DEEPSEEK_API_KEY: process.env.DEEPSEEK_API_KEY,
				}
			});

			if (portfolioResult.exitCode !== 0) {
				throw new Error(`Portfolio analysis failed: ${portfolioResult.stderr}`);
			}

			const portfolioData = JSON.parse(portfolioResult.stdout);
			console.log(`✅ Portfolio analysis completed: ${portfolioData.totalValue}`);

			// Check for rebalancing opportunities
			if (portfolioData.rebalancingRecommendations?.length > 0) {
				console.log("⚖️ Sending rebalancing recommendations...");
				await python.runScript("./scripts/alert_manager.py", [
					"--portfolio-data", JSON.stringify(portfolioData),
					"--type", "rebalancing"
				], {
					env: {
						SLACK_WEBHOOK_URL: process.env.SLACK_WEBHOOK_URL,
					}
				});
			}

			return {
				success: true,
				portfolioValue: portfolioData.totalValue,
				dayChange: portfolioData.dayChange,
				rebalancingNeeded: portfolioData.rebalancingRecommendations?.length > 0,
				topPositions: portfolioData.positions?.slice(0, 5)
			};

		} catch (error) {
			console.error("❌ Portfolio monitoring failed:", error);
			throw error;
		}
	},
});

export const weeklyDeepAnalysis = task({
	id: "weekly-deep-analysis",
	run: async () => {
		console.log("🔬 Starting weekly deep analysis...");

		try {
			// Run comprehensive analysis
			console.log("📊 Running deep market analysis...");
			const deepAnalysisResult = await python.runScript("./scripts/master_stock_analyzer.py", [
				"--mode", "deep",
				"--max-stocks", "100",
				"--include-sectors", "all",
				"--output-format", "json"
			], {
				env: {
					DEEPSEEK_API_KEY: process.env.DEEPSEEK_API_KEY,
					DATABASE_URL: process.env.DATABASE_URL,
				}
			});

			if (deepAnalysisResult.exitCode !== 0) {
				throw new Error(`Deep analysis failed: ${deepAnalysisResult.stderr}`);
			}

			const results = JSON.parse(deepAnalysisResult.stdout);
			console.log(`✅ Deep analysis completed for ${results.length} stocks`);

			// Generate weekly report
			console.log("📄 Generating weekly report...");
			await python.runScript("./scripts/alert_manager.py", [
				"--weekly-report", JSON.stringify(results),
				"--type", "weekly-summary"
			], {
				env: {
					SLACK_WEBHOOK_URL: process.env.SLACK_WEBHOOK_URL,
				}
			});

			return {
				success: true,
				stocksAnalyzed: results.length,
				topPerformers: results.slice(0, 10),
				sectorAnalysis: results.reduce((acc: any, stock: any) => {
					acc[stock.sector] = (acc[stock.sector] || 0) + 1;
					return acc;
				}, {})
			};

		} catch (error) {
			console.error("❌ Weekly deep analysis failed:", error);
			throw error;
		}
	},
});
