// Shared types for automation tasks
// These match the Python models and database schema

// Trigger.dev Task Types for Stock Analysis System

// Basic analysis payload
export interface StockAnalysisPayload {
	symbols: string[];
	analysisType: "daily" | "weekly" | "alert" | "custom";
	portfolioId?: number;
	includeNews?: boolean;
	includeTechnical?: boolean;
	includeLLM?: boolean;
}

// Portfolio-specific payload
export interface PortfolioPayload {
	portfolioId: number;
	portfolioName: string;
	analysisType: "daily" | "weekly" | "monthly" | "rebalance" | "alert";
	includePositions?: boolean;
	includeLLMHistory?: boolean;
	maxHistoryDays?: number;
}

// Stock price alert payload
export interface StockAlertPayload {
	symbol: string;
	currentPrice: number;
	previousPrice: number;
	percentageChange: number;
	volume?: number;
	alertType: "percentage_up" | "percentage_down" | "price_target";
	threshold: number;
	portfolioId?: number;
	marketHours: boolean;
}

// LLM message for portfolio context
export interface PortfolioLlmMessage {
	id?: number;
	portfolioId: number;
	role: "user" | "assistant" | "system";
	content: string;
	tokensUsed?: number;
	costUsd?: number;
	model?: string;
	analysisType?: "daily" | "weekly" | "alert" | "rebalance";
	stockSymbols?: string[];
	createdAt?: Date;
}

// Portfolio analysis result
export interface PortfolioAnalysisResult {
	portfolioId: number;
	analysisType: "daily" | "weekly" | "monthly" | "rebalance" | "alert";
	totalValue: number;
	dailyReturn?: number;
	totalReturn?: number;
	riskScore?: number;
	diversification?: number;
	llmSummary?: string;
	recommendations?: string[];
	riskFactors?: string[];
	opportunities?: string[];
	sharpeRatio?: number;
	maxDrawdown?: number;
	volatility?: number;
	beta?: number;
}

// Stock price alert configuration
export interface StockPriceAlertConfig {
	id?: number;
	symbol: string;
	alertType: "percentage_up" | "percentage_down" | "price_target";
	threshold: number;
	isActive: boolean;
	portfolioId?: number;
	lastTriggeredAt?: Date;
	triggerCount: number;
}

// Analysis result from Python scripts
export interface AnalysisResult {
	symbol: string;
	score: number;
	recommendation: "BUY" | "SELL" | "HOLD";
	confidence: number;
	analysis: {
		fundamental?: any;
		technical?: any;
		llm?: any;
		sentiment?: any;
	};
	alerts?: string[];
	timestamp: string;
}

// Portfolio position data
export interface PortfolioPosition {
	symbol: string;
	quantity: number;
	averagePrice: number;
	currentPrice: number;
	marketValue: number;
	unrealizedPnl: number;
	unrealizedPnlPercent: number;
	weight: number;
}

// Portfolio summary
export interface PortfolioSummary {
	id: number;
	name: string;
	totalValue: number;
	dailyChange: number;
	dailyChangePercent: number;
	positions: PortfolioPosition[];
	lastUpdated: string;
}

// System health check result
export interface HealthCheckResult {
	status: "healthy" | "warning" | "error";
	checks: {
		database: boolean;
		api_keys: boolean;
		recent_analysis: boolean;
		portfolio_data: boolean;
	};
	message: string;
	timestamp: string;
}

// Task execution context
export interface TaskContext {
	taskId: string;
	portfolioId?: number;
	symbols?: string[];
	analysisType: string;
	environment: "development" | "production";
	timestamp: string;
}

// Multi-portfolio analysis payload
export interface MultiPortfolioPayload {
	portfolioIds: number[];
	analysisType: "daily" | "weekly" | "comparative";
	includeCorrelation?: boolean;
	includeRebalancing?: boolean;
	includeLLMInsights?: boolean;
}

// Price movement trigger payload
export interface PriceMovementPayload {
	symbol: string;
	priceChange: {
		current: number;
		previous: number;
		percentage: number;
		timeframe: "1m" | "5m" | "15m" | "1h" | "1d";
	};
	volume?: {
		current: number;
		average: number;
		percentageChange: number;
	};
	portfolioContext?: {
		portfolioId: number;
		position?: PortfolioPosition;
		impact: number; // Impact on portfolio value
	};
}

// LLM conversation context
export interface LlmConversationContext {
	portfolioId: number;
	recentMessages: PortfolioLlmMessage[];
	analysisType: string;
	stockContext: string[];
	marketContext?: {
		marketHours: boolean;
		marketTrend: "up" | "down" | "sideways";
		volatility: "low" | "medium" | "high";
	};
}

// Database Models (simplified for TypeScript)
export interface DailyAnalysis {
	id?: number;
	date: string;
	symbol: string;
	analysisData: any;
	compositeScore?: number;
	rating?: string;
	confidence?: string;
	createdAt?: string;
}

export interface Portfolio {
	id?: number;
	name: string;
	description?: string;
	portfolioType: string;
	baseCurrency: string;
	createdAt?: string;
	updatedAt?: string;
	isActive: boolean;
}
