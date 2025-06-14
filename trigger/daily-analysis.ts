import { task } from "@trigger.dev/sdk/v3";
import { PrismaClient } from "../src/generated/prisma";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);
const prisma = new PrismaClient();

export const dailyAnalysisTask = task({
	id: "daily-analysis",
	maxDuration: 1800, // 30 minutes
	run: async (payload: { symbols?: string[]; forceRun?: boolean }) => {
		console.log("🚀 Starting daily analysis task");

		try {
			// 1. Check if analysis already exists for today (unless forced)
			const today = new Date().toISOString().split('T')[0];

			if (!payload.forceRun) {
				const existingAnalysis = await prisma.dailyAnalysis.findFirst({
					where: {
						date: new Date(today),
					},
				});

				if (existingAnalysis) {
					console.log("📊 Analysis already exists for today, skipping");
					return { status: "skipped", reason: "already_exists", date: today };
				}
			}

			// 2. Run Python analysis script
			const symbolsArg = payload.symbols ? payload.symbols.join(",") : "";
			const command = `cd ${process.cwd()} && uv run python scripts/master_stock_analyzer.py${symbolsArg ? ` --symbols ${symbolsArg}` : ""}`;

			console.log(`🐍 Running Python analysis: ${command}`);
			const { stdout, stderr } = await execAsync(command);

			if (stderr) {
				console.warn("⚠️ Python script warnings:", stderr);
			}

			console.log("✅ Python analysis completed:", stdout);

			// 3. Fetch analysis results from database
			const analysisResults = await prisma.dailyAnalysis.findMany({
				where: {
					date: new Date(today),
				},
				orderBy: {
					compositeScore: 'desc',
				},
			});

			// 4. Generate market context
			await generateMarketContext(today);

			// 5. Create daily decision record
			await createDailyDecision(today, analysisResults);

			console.log(`📈 Analysis completed for ${analysisResults.length} stocks`);

			return {
				status: "completed",
				date: today,
				stocksAnalyzed: analysisResults.length,
				topPicks: analysisResults.slice(0, 5).map(r => ({
					symbol: r.symbol,
					score: r.compositeScore?.toString(),
					rating: r.rating,
				})),
			};

		} catch (error) {
			console.error("❌ Daily analysis failed:", error);
			throw error;
		}
	},
});

export const portfolioMonitoringTask = task({
	id: "portfolio-monitoring",
	maxDuration: 600, // 10 minutes
	run: async (payload: { portfolioId?: number }) => {
		console.log("📊 Starting portfolio monitoring task");

		try {
			// 1. Get active portfolios
			const portfolios = await prisma.portfolio.findMany({
				where: {
					isActive: true,
					...(payload.portfolioId && { id: payload.portfolioId }),
				},
				include: {
					positions: true,
				},
			});

			const results = [];

			for (const portfolio of portfolios) {
				console.log(`📈 Monitoring portfolio: ${portfolio.name}`);

				// 2. Run portfolio update script
				const command = `cd ${process.cwd()} && uv run python scripts/portfolio_manager.py --portfolio-id ${portfolio.id} --update`;
				const { stdout, stderr } = await execAsync(command);

				if (stderr) {
					console.warn(`⚠️ Portfolio ${portfolio.id} warnings:`, stderr);
				}

				// 3. Get updated portfolio snapshot
				const latestSnapshot = await prisma.portfolioSnapshot.findFirst({
					where: { portfolioId: portfolio.id },
					orderBy: { snapshotDate: 'desc' },
				});

				results.push({
					portfolioId: portfolio.id,
					name: portfolio.name,
					totalValue: latestSnapshot?.totalValue?.toString(),
					dayChange: latestSnapshot?.dayChange?.toString(),
					dayChangePct: latestSnapshot?.dayChangePct?.toString(),
					positionsCount: latestSnapshot?.positionsCount,
				});
			}

			console.log(`✅ Portfolio monitoring completed for ${portfolios.length} portfolios`);

			return {
				status: "completed",
				portfoliosMonitored: portfolios.length,
				results,
			};

		} catch (error) {
			console.error("❌ Portfolio monitoring failed:", error);
			throw error;
		}
	},
});

export const weeklyDeepAnalysisTask = task({
	id: "weekly-deep-analysis",
	maxDuration: 3600, // 1 hour
	run: async (payload: { sector?: string }) => {
		console.log("🔍 Starting weekly deep analysis task");

		try {
			const today = new Date().toISOString().split('T')[0];

			// 1. Run comprehensive analysis with LLM enhancement
			const command = `cd ${process.cwd()} && uv run python scripts/master_stock_analyzer.py --deep-analysis${payload.sector ? ` --sector ${payload.sector}` : ""}`;

			console.log(`🧠 Running deep analysis: ${command}`);
			const { stdout, stderr } = await execAsync(command);

			if (stderr) {
				console.warn("⚠️ Deep analysis warnings:", stderr);
			}

			// 2. Generate performance report
			const performanceCommand = `cd ${process.cwd()} && uv run python -c "
from src.db.connection import get_db_connection
from src.core.analyzer import StockAnalyzer
import json

with get_db_connection() as conn:
    analyzer = StockAnalyzer(conn)
    report = analyzer.generate_performance_report()
    print(json.dumps(report, indent=2))
"`;

			const { stdout: reportOutput } = await execAsync(performanceCommand);
			const performanceReport = JSON.parse(reportOutput);

			// 3. Get top performers from last week
			const weekAgo = new Date();
			weekAgo.setDate(weekAgo.getDate() - 7);

			const topPerformers = await prisma.performanceTracking.findMany({
				where: {
					recommendationDate: {
						gte: weekAgo,
					},
					status: 'active',
				},
				orderBy: {
					returnPct: 'desc',
				},
				take: 10,
			});

			console.log("✅ Weekly deep analysis completed");

			return {
				status: "completed",
				date: today,
				sector: payload.sector || "all",
				performanceReport,
				topPerformers: topPerformers.map(p => ({
					symbol: p.symbol,
					returnPct: p.returnPct?.toString(),
					daysHeld: p.daysHeld,
					rating: p.rating,
				})),
			};

		} catch (error) {
			console.error("❌ Weekly deep analysis failed:", error);
			throw error;
		}
	},
});

// Helper functions
async function generateMarketContext(date: string) {
	try {
		const command = `cd ${process.cwd()} && uv run python -c "
from src.data.market_data import MarketDataProvider
from src.db.connection import get_db_connection
import json
from datetime import datetime

provider = MarketDataProvider()
context = provider.get_market_context()

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO market_context (date, market_sentiment, vix_level, sector_rotation, economic_indicators, news_themes)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date) DO UPDATE SET
            market_sentiment = EXCLUDED.market_sentiment,
            vix_level = EXCLUDED.vix_level,
            sector_rotation = EXCLUDED.sector_rotation,
            economic_indicators = EXCLUDED.economic_indicators,
            news_themes = EXCLUDED.news_themes
    ''', (
        '${date}',
        context.get('sentiment'),
        context.get('vix'),
        json.dumps(context.get('sector_rotation', {})),
        json.dumps(context.get('economic_indicators', {})),
        json.dumps(context.get('news_themes', {}))
    ))
    conn.commit()
    print('Market context updated')
"`;

		await execAsync(command);
		console.log("📊 Market context generated");
	} catch (error) {
		console.warn("⚠️ Failed to generate market context:", error);
	}
}

async function createDailyDecision(date: string, analysisResults: any[]) {
	try {
		const topStocks = analysisResults.slice(0, 5);
		const reasoning = `Daily analysis completed for ${analysisResults.length} stocks. Top performers based on composite scoring algorithm combining fundamental analysis, technical indicators, and LLM-enhanced sector analysis.`;

		await prisma.dailyDecision.upsert({
			where: { date: new Date(date) },
			update: {
				decisionType: "daily_analysis",
				reasoning,
				selectedStocks: topStocks.map(s => ({
					symbol: s.symbol,
					score: s.compositeScore?.toString(),
					rating: s.rating,
					confidence: s.confidence,
				})),
				marketContext: {
					totalAnalyzed: analysisResults.length,
					avgScore: analysisResults.reduce((sum, r) => sum + (Number(r.compositeScore) || 0), 0) / analysisResults.length,
				},
			},
			create: {
				date: new Date(date),
				decisionType: "daily_analysis",
				reasoning,
				selectedStocks: topStocks.map(s => ({
					symbol: s.symbol,
					score: s.compositeScore?.toString(),
					rating: s.rating,
					confidence: s.confidence,
				})),
				marketContext: {
					totalAnalyzed: analysisResults.length,
					avgScore: analysisResults.reduce((sum, r) => sum + (Number(r.compositeScore) || 0), 0) / analysisResults.length,
				},
			},
		});

		console.log("📝 Daily decision recorded");
	} catch (error) {
		console.warn("⚠️ Failed to create daily decision:", error);
	}
}
