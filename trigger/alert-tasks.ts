import { task } from "@trigger.dev/sdk/v3";
import { PrismaClient } from "../src/generated/prisma";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);
const prisma = new PrismaClient();

export const stockAlertTask = task({
	id: "stock-alert",
	maxDuration: 300, // 5 minutes
	run: async (payload: {
		symbol: string;
		alertType: "buy" | "sell" | "news" | "earnings";
		score?: number;
		reason?: string;
		urgency?: "low" | "medium" | "high";
	}) => {
		console.log(`🚨 Processing ${payload.alertType} alert for ${payload.symbol}`);

		try {
			// 1. Get current analysis for the stock
			const today = new Date().toISOString().split('T')[0];
			const analysis = await prisma.dailyAnalysis.findFirst({
				where: {
					symbol: payload.symbol,
					date: new Date(today),
				},
			});

			// 2. Prepare alert data
			const alertData = {
				symbol: payload.symbol,
				alertType: payload.alertType,
				score: payload.score || analysis?.compositeScore?.toNumber(),
				rating: analysis?.rating,
				confidence: analysis?.confidence,
				reason: payload.reason || "Automated alert triggered",
				urgency: payload.urgency || "medium",
				timestamp: new Date().toISOString(),
			};

			// 3. Send alert via Python script
			const command = `cd ${process.cwd()} && uv run python scripts/alert_manager.py --alert '${JSON.stringify(alertData)}'`;
			const { stdout, stderr } = await execAsync(command);

			if (stderr) {
				console.warn("⚠️ Alert script warnings:", stderr);
			}

			console.log("✅ Alert sent successfully:", stdout);

			return {
				status: "sent",
				symbol: payload.symbol,
				alertType: payload.alertType,
				urgency: payload.urgency,
				timestamp: alertData.timestamp,
			};

		} catch (error) {
			console.error("❌ Alert failed:", error);
			throw error;
		}
	},
});

export const portfolioAlertTask = task({
	id: "portfolio-alert",
	maxDuration: 300, // 5 minutes
	run: async (payload: {
		portfolioId: number;
		alertType: "rebalance" | "performance" | "risk" | "position";
		threshold?: number;
		message?: string;
	}) => {
		console.log(`📊 Processing portfolio alert for portfolio ${payload.portfolioId}`);

		try {
			// 1. Get portfolio data
			const portfolio = await prisma.portfolio.findUnique({
				where: { id: payload.portfolioId },
				include: {
					positions: true,
					snapshots: {
						orderBy: { snapshotDate: 'desc' },
						take: 1,
					},
				},
			});

			if (!portfolio) {
				throw new Error(`Portfolio ${payload.portfolioId} not found`);
			}

			const latestSnapshot = portfolio.snapshots[0];

			// 2. Prepare portfolio alert data
			const alertData = {
				portfolioId: payload.portfolioId,
				portfolioName: portfolio.name,
				alertType: payload.alertType,
				totalValue: latestSnapshot?.totalValue?.toString(),
				dayChange: latestSnapshot?.dayChange?.toString(),
				dayChangePct: latestSnapshot?.dayChangePct?.toString(),
				positionsCount: portfolio.positions.length,
				message: payload.message || `Portfolio ${payload.alertType} alert`,
				threshold: payload.threshold,
				timestamp: new Date().toISOString(),
			};

			// 3. Send portfolio alert
			const command = `cd ${process.cwd()} && uv run python scripts/alert_manager.py --portfolio-alert '${JSON.stringify(alertData)}'`;
			const { stdout, stderr } = await execAsync(command);

			if (stderr) {
				console.warn("⚠️ Portfolio alert warnings:", stderr);
			}

			console.log("✅ Portfolio alert sent:", stdout);

			return {
				status: "sent",
				portfolioId: payload.portfolioId,
				alertType: payload.alertType,
				timestamp: alertData.timestamp,
			};

		} catch (error) {
			console.error("❌ Portfolio alert failed:", error);
			throw error;
		}
	},
});

export const systemHealthTask = task({
	id: "system-health-check",
	maxDuration: 600, // 10 minutes
	run: async (payload: { checkType?: "full" | "quick" }) => {
		console.log("🏥 Running system health check");

		try {
			const checkType = payload.checkType || "quick";
			const healthData: any = {
				timestamp: new Date().toISOString(),
				checkType,
				status: "healthy",
				issues: [],
			};

			// 1. Database connectivity check
			try {
				await prisma.$queryRaw`SELECT 1`;
				healthData.database = "connected";
			} catch (error) {
				healthData.database = "error";
				healthData.issues.push("Database connection failed");
				healthData.status = "unhealthy";
			}

			// 2. Recent analysis check
			const today = new Date();
			const yesterday = new Date(today);
			yesterday.setDate(yesterday.getDate() - 1);

			const recentAnalysis = await prisma.dailyAnalysis.count({
				where: {
					date: {
						gte: yesterday,
					},
				},
			});

			if (recentAnalysis === 0) {
				healthData.issues.push("No recent analysis found");
				healthData.status = "warning";
			}

			healthData.recentAnalysisCount = recentAnalysis;

			// 3. Portfolio data check
			const activePortfolios = await prisma.portfolio.count({
				where: { isActive: true },
			});

			healthData.activePortfolios = activePortfolios;

			if (checkType === "full") {
				// 4. Python environment check
				try {
					const { stdout } = await execAsync("cd ${process.cwd()} && uv run python --version");
					healthData.pythonVersion = stdout.trim();
				} catch (error) {
					healthData.issues.push("Python environment check failed");
					healthData.status = "unhealthy";
				}

				// 5. API keys check
				const requiredEnvVars = ["DATABASE_URL", "DEEPSEEK_API_KEY"];
				const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

				if (missingVars.length > 0) {
					healthData.issues.push(`Missing environment variables: ${missingVars.join(", ")}`);
					healthData.status = "unhealthy";
				}
			}

			// 6. Send health report if there are issues
			if (healthData.status !== "healthy") {
				const command = `cd ${process.cwd()} && uv run python scripts/alert_manager.py --health-alert '${JSON.stringify(healthData)}'`;
				await execAsync(command);
			}

			console.log(`✅ Health check completed: ${healthData.status}`);

			return healthData;

		} catch (error) {
			console.error("❌ Health check failed:", error);

			// Send critical system alert
			try {
				const criticalAlert = {
					type: "critical_system_error",
					message: `System health check failed: ${error.message}`,
					timestamp: new Date().toISOString(),
				};

				const command = `cd ${process.cwd()} && uv run python scripts/alert_manager.py --critical-alert '${JSON.stringify(criticalAlert)}'`;
				await execAsync(command);
			} catch (alertError) {
				console.error("❌ Failed to send critical alert:", alertError);
			}

			throw error;
		}
	},
});

export const newsAnalysisTask = task({
	id: "news-analysis",
	maxDuration: 900, // 15 minutes
	run: async (payload: {
		symbols?: string[];
		newsSource?: string;
		urgency?: "low" | "medium" | "high";
	}) => {
		console.log("📰 Running news analysis task");

		try {
			const symbols = payload.symbols || [];
			const newsSource = payload.newsSource || "all";

			// 1. Run news analysis script
			const command = `cd ${process.cwd()} && uv run python -c "
from src.data.news_analyzer import NewsAnalyzer
from src.db.connection import get_db_connection
import json

analyzer = NewsAnalyzer()
symbols = ${JSON.stringify(symbols)}

if symbols:
    results = analyzer.analyze_stock_news(symbols)
else:
    results = analyzer.analyze_market_news()

print(json.dumps(results, indent=2))
"`;

			const { stdout, stderr } = await execAsync(command);

			if (stderr) {
				console.warn("⚠️ News analysis warnings:", stderr);
			}

			const newsResults = JSON.parse(stdout);

			// 2. Process significant news events
			const significantNews = newsResults.filter((news: any) =>
				news.sentiment_score && (news.sentiment_score > 0.7 || news.sentiment_score < -0.7)
			);

			// 3. Send alerts for significant news
			for (const news of significantNews) {
				await stockAlertTask.trigger({
					symbol: news.symbol,
					alertType: "news",
					reason: `Significant news: ${news.headline}`,
					urgency: payload.urgency || "medium",
				});
			}

			console.log(`✅ News analysis completed: ${significantNews.length} significant events`);

			return {
				status: "completed",
				totalNews: newsResults.length,
				significantNews: significantNews.length,
				alerts: significantNews.map((news: any) => ({
					symbol: news.symbol,
					headline: news.headline,
					sentiment: news.sentiment_score,
				})),
			};

		} catch (error) {
			console.error("❌ News analysis failed:", error);
			throw error;
		}
	},
});
