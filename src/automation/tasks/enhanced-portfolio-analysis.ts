import { schedules, task } from "@trigger.dev/sdk/v3";
import { getValidatedEnv, createApiClient } from "../shared/env-validation";

// Enhanced interfaces for conversation-aware portfolio analysis
interface PortfolioConversationContext {
	portfolio_id: string;
	conversation_thread_id: string;
	last_analysis_date: string;
	conversation_history: ConversationMessage[];
	trading_decisions: TradingDecision[];
	market_context: MarketContext;
	portfolio_state: PortfolioState;
	context_summary: string;
	total_conversations: number;
	performance_since_start: number;
}

interface ConversationMessage {
	role: "user" | "assistant" | "system";
	content: string;
	timestamp?: string;
	agent?: string;
}

interface TradingDecision {
	decision_id: string;
	symbol: string;
	action: "buy" | "sell" | "hold";
	quantity?: number;
	price?: number;
	reasoning: string;
	confidence: number;
	timestamp: string;
	executed: boolean;
	outcome?: "success" | "failure" | "pending";
}

interface MarketContext {
	market_regime: "bull" | "bear" | "sideways";
	volatility_level: "low" | "medium" | "high";
	recent_events: any[];
	sector_performance: Record<string, number>;
	economic_indicators: Record<string, any>;
	last_updated: string;
}

interface PortfolioState {
	total_value: number;
	daily_return: number;
	positions: any[];
	risk_metrics: Record<string, number>;
	allocation: Record<string, number>;
	last_updated: string;
}

interface ConversationThread {
	thread_id: string;
	conversation_type: "daily_analysis" | "trading_decision" | "risk_check" | "market_event";
	user_message: string;
	ai_responses: ConversationMessage[];
	market_context?: MarketContext;
	portfolio_state?: PortfolioState;
	actions_taken: TradingDecision[];
	trigger_source?: "scheduled" | "manual" | "market_event";
	metadata: Record<string, any>;
}

interface PortfolioConfig {
	portfolio_id: string;
	automation_level: "monitor_only" | "suggest_only" | "auto_execute";
	risk_tolerance: "conservative" | "moderate" | "aggressive";
	max_position_size: number;
	daily_loss_limit: number;
	trading_hours?: any;
	preferred_sectors: string[];
	blacklisted_symbols: string[];
	rebalancing_frequency: "daily" | "weekly" | "monthly";
	notification_settings?: any;
}

// Enhanced Daily Portfolio Analysis with Conversation History
export const enhancedDailyPortfolioAnalysis = schedules.task({
	id: "enhanced-daily-portfolio-analysis",
	cron: {
		pattern: "45 9 * * 1-5", // 9:45 AM Monday-Friday
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`🧠 Enhanced Daily Portfolio Analysis Started at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		try {
			// Get all active portfolios
			const activePortfolios = await getActivePortfolios(apiClient);
			console.log(`📋 Found ${activePortfolios.length} active portfolios for enhanced analysis`);

			const results = [];

			for (const portfolio of activePortfolios) {
				try {
					console.log(`🔍 Enhanced analysis for portfolio ${portfolio.id}: ${portfolio.name}`);

					// 1. Get portfolio-specific conversation context
					const conversationContext = await getPortfolioConversationContext(
						apiClient,
						portfolio.id,
						7 // Last 7 days
					);

					console.log(`💬 Retrieved ${conversationContext.total_conversations} conversations for context`);

					// 2. Get portfolio configuration
					const portfolioConfig = await getPortfolioConfig(apiClient, portfolio.id);

					// 3. Get current portfolio data
					const portfolioData = await getPortfolioData(apiClient, portfolio.id);

					// 4. Build enhanced analysis request with full context
					const analysisRequest = {
						portfolio_data: portfolioData,
						conversation_context: conversationContext,
						previous_decisions: conversationContext.trading_decisions,
						market_memory: conversationContext.market_context,
						analysis_type: "daily_with_context",
						include_recommendations: true,
						include_risk_analysis: true,
						include_opportunities: true,
						store_conversation: true
					};

					// 5. Run AI analysis with full context
					const analysisResult = await runAIAnalysisWithContext(apiClient, analysisRequest);

					console.log(`🤖 AI Analysis completed with ${analysisResult.recommendations?.length || 0} recommendations`);

					// 6. Execute approved actions based on automation level
					let actionsExecuted = [];
					if (portfolioConfig.automation_level === "auto_execute" && analysisResult.recommended_actions) {
						actionsExecuted = await executePortfolioActions(
							apiClient,
							portfolio.id,
							analysisResult.recommended_actions,
							portfolioConfig
						);
						console.log(`⚡ Executed ${actionsExecuted.length} automated actions`);
					} else if (portfolioConfig.automation_level === "suggest_only") {
						console.log(`💡 Generated ${analysisResult.recommended_actions?.length || 0} suggestions (auto-execution disabled)`);
					}

					// 7. Store conversation thread with full context
					const conversationThread: ConversationThread = {
						thread_id: `daily_${portfolio.id}_${Date.now()}`,
						conversation_type: "daily_analysis",
						user_message: `Daily portfolio analysis for ${portfolio.name}`,
						ai_responses: analysisResult.ai_responses || [],
						market_context: conversationContext.market_context,
						portfolio_state: conversationContext.portfolio_state,
						actions_taken: actionsExecuted,
						trigger_source: "scheduled",
						metadata: {
							analysis_type: "daily_with_context",
							automation_level: portfolioConfig.automation_level,
							context_conversations: conversationContext.total_conversations,
							previous_decisions: conversationContext.trading_decisions.length
						}
					};

					await storeConversationThread(apiClient, portfolio.id, conversationThread);

					// 8. Generate alerts if needed
					const alerts = await generatePortfolioAlerts(apiClient, portfolio.id, analysisResult, portfolioConfig);

					results.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						status: "success",
						totalValue: portfolioData.total_value,
						dailyReturn: portfolioData.daily_return,
						conversationsUsed: conversationContext.total_conversations,
						recommendationsGenerated: analysisResult.recommendations?.length || 0,
						actionsExecuted: actionsExecuted.length,
						alertsGenerated: alerts.length,
						automationLevel: portfolioConfig.automation_level,
						contextSummary: conversationContext.context_summary
					});

				} catch (error: any) {
					console.error(`❌ Enhanced analysis failed for portfolio ${portfolio.id}:`, error);
					results.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						status: "error",
						error: error.message
					});
				}
			}

			const successCount = results.filter(r => r.status === "success").length;
			const totalActions = results.reduce((sum, r) => sum + (r.actionsExecuted || 0), 0);
			const totalAlerts = results.reduce((sum, r) => sum + (r.alertsGenerated || 0), 0);

			console.log(`✅ Enhanced daily analysis completed: ${successCount}/${activePortfolios.length} portfolios`);
			console.log(`⚡ Total actions executed: ${totalActions}`);
			console.log(`🚨 Total alerts generated: ${totalAlerts}`);

			return {
				success: true,
				portfoliosAnalyzed: activePortfolios.length,
				successfulAnalyses: successCount,
				totalActionsExecuted: totalActions,
				totalAlertsGenerated: totalAlerts,
				results: results,
				scheduledTime: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Enhanced daily portfolio analysis failed:", error);
			throw error;
		}
	},
});

// Portfolio-Specific Risk Monitor with Conversation Context
export const portfolioRiskMonitor = schedules.task({
	id: "portfolio-risk-monitor",
	cron: {
		pattern: "*/15 * * * *", // Every 15 minutes during market hours
		timezone: "America/New_York"
	},
	run: async (payload) => {
		console.log(`🛡️ Portfolio Risk Monitor Started at ${payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })}`);

		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		try {
			const activePortfolios = await getActivePortfolios(apiClient);
			const riskEvents = [];

			for (const portfolio of activePortfolios) {
				try {
					// Calculate current risk metrics
					const riskMetrics = await calculatePortfolioRisk(apiClient, portfolio.id);
					const config = await getPortfolioConfig(apiClient, portfolio.id);

					// Check risk thresholds
					if (riskMetrics.daily_loss > config.daily_loss_limit) {
						console.log(`🚨 Risk threshold exceeded for portfolio ${portfolio.id}: ${(riskMetrics.daily_loss * 100).toFixed(2)}%`);

						// Get conversation context for risk decision
						const conversationContext = await getPortfolioConversationContext(
							apiClient,
							portfolio.id,
							3 // Last 3 days for risk context
						);

						// AI risk assessment with conversation context
						const riskAssessment = await runRiskAssessmentWithContext(
							apiClient,
							portfolio.id,
							riskMetrics,
							conversationContext,
							config
						);

						// Execute risk management actions if needed
						let riskActionsExecuted = [];
						if (riskAssessment.immediate_action_required) {
							riskActionsExecuted = await executeRiskManagementActions(
								apiClient,
								portfolio.id,
								riskAssessment.actions,
								config
							);
							console.log(`⚡ Executed ${riskActionsExecuted.length} risk management actions`);
						}

						// Store risk decision in conversation thread
						const riskConversationThread: ConversationThread = {
							thread_id: `risk_${portfolio.id}_${Date.now()}`,
							conversation_type: "risk_check",
							user_message: `Risk threshold exceeded: ${(riskMetrics.daily_loss * 100).toFixed(2)}% daily loss`,
							ai_responses: riskAssessment.ai_responses || [],
							market_context: conversationContext.market_context,
							portfolio_state: conversationContext.portfolio_state,
							actions_taken: riskActionsExecuted,
							trigger_source: "scheduled",
							metadata: {
								trigger: "daily_loss_limit_exceeded",
								daily_loss: riskMetrics.daily_loss,
								loss_limit: config.daily_loss_limit,
								immediate_action_required: riskAssessment.immediate_action_required,
								risk_score: riskMetrics.risk_score
							}
						};

						await storeConversationThread(apiClient, portfolio.id, riskConversationThread);

						riskEvents.push({
							portfolioId: portfolio.id,
							portfolioName: portfolio.name,
							riskType: "daily_loss_limit_exceeded",
							dailyLoss: riskMetrics.daily_loss,
							lossLimit: config.daily_loss_limit,
							actionsExecuted: riskActionsExecuted.length,
							immediateActionRequired: riskAssessment.immediate_action_required
						});
					}

				} catch (error: any) {
					console.error(`❌ Risk monitoring failed for portfolio ${portfolio.id}:`, error);
				}
			}

			console.log(`✅ Risk monitoring completed: ${riskEvents.length} risk events detected`);

			return {
				success: true,
				portfoliosMonitored: activePortfolios.length,
				riskEventsDetected: riskEvents.length,
				riskEvents: riskEvents,
				monitoredAt: payload.timestamp,
				nextRun: payload.upcoming[0],
				timestamp: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Portfolio risk monitoring failed:", error);
			throw error;
		}
	},
});

// Market Event Response with Portfolio Context
export const marketEventResponseTrigger = task({
	id: "market-event-response",
	run: async (payload: {
		event_type: string;
		event_description: string;
		affected_symbols?: string[];
		severity: "low" | "medium" | "high";
	}) => {
		console.log(`📰 Market Event Response Trigger: ${payload.event_type}`);
		console.log(`📝 Description: ${payload.event_description}`);
		console.log(`⚡ Severity: ${payload.severity}`);

		const env = getValidatedEnv();
		const apiClient = createApiClient(env);

		try {
			const activePortfolios = await getActivePortfolios(apiClient);
			const eventResponses = [];

			for (const portfolio of activePortfolios) {
				try {
					// Get conversation history and market memory
					const conversationContext = await getPortfolioConversationContext(
						apiClient,
						portfolio.id,
						14 // Last 2 weeks for market event context
					);

					// Check if we've seen similar events before
					const similarEvents = conversationContext.market_context.recent_events.filter(
						(event: any) => event.type === payload.event_type
					);

					console.log(`📚 Found ${similarEvents.length} similar events in portfolio ${portfolio.id} history`);

					// AI analysis with event context and memory
					const eventAnalysis = await runEventAnalysisWithContext(apiClient, {
						portfolio_id: portfolio.id,
						event: payload,
						conversation_context: conversationContext,
						similar_events: similarEvents,
						portfolio_state: conversationContext.portfolio_state
					});

					// Execute event-driven actions if needed
					let eventActionsExecuted = [];
					if (eventAnalysis.actions_required) {
						const config = await getPortfolioConfig(apiClient, portfolio.id);
						eventActionsExecuted = await executeEventActions(
							apiClient,
							portfolio.id,
							eventAnalysis.actions,
							config
						);
						console.log(`⚡ Executed ${eventActionsExecuted.length} event-driven actions for portfolio ${portfolio.id}`);
					}

					// Store event response in conversation thread
					const eventConversationThread: ConversationThread = {
						thread_id: `event_${portfolio.id}_${Date.now()}`,
						conversation_type: "market_event",
						user_message: `Market event: ${payload.event_type} - ${payload.event_description}`,
						ai_responses: eventAnalysis.ai_responses || [],
						market_context: conversationContext.market_context,
						portfolio_state: conversationContext.portfolio_state,
						actions_taken: eventActionsExecuted,
						trigger_source: "market_event",
						metadata: {
							event_type: payload.event_type,
							event_severity: payload.severity,
							affected_symbols: payload.affected_symbols || [],
							similar_events_found: similarEvents.length,
							actions_required: eventAnalysis.actions_required
						}
					};

					await storeConversationThread(apiClient, portfolio.id, eventConversationThread);

					eventResponses.push({
						portfolioId: portfolio.id,
						portfolioName: portfolio.name,
						actionsRequired: eventAnalysis.actions_required,
						actionsExecuted: eventActionsExecuted.length,
						similarEventsFound: similarEvents.length,
						impactAssessment: eventAnalysis.impact_assessment
					});

				} catch (error: any) {
					console.error(`❌ Market event response failed for portfolio ${portfolio.id}:`, error);
				}
			}

			const totalActions = eventResponses.reduce((sum, r) => sum + r.actionsExecuted, 0);
			console.log(`✅ Market event response completed: ${totalActions} total actions executed`);

			return {
				success: true,
				eventType: payload.event_type,
				eventSeverity: payload.severity,
				portfoliosAnalyzed: activePortfolios.length,
				totalActionsExecuted: totalActions,
				eventResponses: eventResponses,
				processedAt: new Date().toISOString()
			};

		} catch (error: any) {
			console.error("❌ Market event response failed:", error);
			throw error;
		}
	},
});

// Helper functions

async function getActivePortfolios(apiClient: any): Promise<Array<{ id: string, name: string }>> {
	const response = await apiClient.get('/portfolios/active');
	return response.portfolios || [];
}

async function getPortfolioConversationContext(
	apiClient: any,
	portfolioId: string,
	daysBack: number
): Promise<PortfolioConversationContext> {
	const response = await apiClient.post(`/trading/swarm/conversation-context/${portfolioId}`, {
		days_back: daysBack,
		include_market_context: true,
		include_trading_decisions: true,
		include_portfolio_state: true
	});
	return response;
}

async function getPortfolioConfig(apiClient: any, portfolioId: string): Promise<PortfolioConfig> {
	// This would get portfolio-specific configuration
	// For now, return default config
	return {
		portfolio_id: portfolioId,
		automation_level: "monitor_only",
		risk_tolerance: "moderate",
		max_position_size: 0.10,
		daily_loss_limit: 0.02,
		preferred_sectors: [],
		blacklisted_symbols: [],
		rebalancing_frequency: "weekly"
	};
}

async function getPortfolioData(apiClient: any, portfolioId: string): Promise<any> {
	const response = await apiClient.get(`/portfolio/${portfolioId}/summary`);
	return response;
}

async function runAIAnalysisWithContext(apiClient: any, analysisRequest: any): Promise<any> {
	const response = await apiClient.post('/portfolio/analyze-with-llm', analysisRequest);
	return response;
}

async function executePortfolioActions(
	apiClient: any,
	portfolioId: string,
	actions: any[],
	config: PortfolioConfig
): Promise<TradingDecision[]> {
	// This would execute portfolio actions with safety checks
	// For now, return empty array
	console.log(`🔒 Action execution disabled in demo mode for portfolio ${portfolioId}`);
	return [];
}

async function storeConversationThread(
	apiClient: any,
	portfolioId: string,
	conversationThread: ConversationThread
): Promise<void> {
	await apiClient.post(`/trading/swarm/store-conversation-thread/${portfolioId}`, conversationThread);
}

async function generatePortfolioAlerts(
	apiClient: any,
	portfolioId: string,
	analysisResult: any,
	config: PortfolioConfig
): Promise<string[]> {
	// Generate portfolio-specific alerts
	const alerts: string[] = [];

	if (analysisResult.risk_score && analysisResult.risk_score > 0.8) {
		alerts.push(`🚨 HIGH RISK: Portfolio ${portfolioId} risk score is ${(analysisResult.risk_score * 100).toFixed(1)}%`);
	}

	if (analysisResult.opportunities && analysisResult.opportunities.length > 0) {
		alerts.push(`💡 OPPORTUNITIES: ${analysisResult.opportunities.length} new opportunities identified`);
	}

	return alerts;
}

async function calculatePortfolioRisk(apiClient: any, portfolioId: string): Promise<any> {
	// Calculate portfolio risk metrics
	return {
		daily_loss: 0.01, // 1% daily loss
		risk_score: 0.5,
		volatility: 0.15
	};
}

async function runRiskAssessmentWithContext(
	apiClient: any,
	portfolioId: string,
	riskMetrics: any,
	conversationContext: PortfolioConversationContext,
	config: PortfolioConfig
): Promise<any> {
	// Run AI risk assessment with conversation context
	return {
		immediate_action_required: riskMetrics.daily_loss > config.daily_loss_limit * 1.5,
		actions: [],
		ai_responses: []
	};
}

async function executeRiskManagementActions(
	apiClient: any,
	portfolioId: string,
	actions: any[],
	config: PortfolioConfig
): Promise<TradingDecision[]> {
	// Execute risk management actions
	console.log(`🛡️ Risk management actions disabled in demo mode for portfolio ${portfolioId}`);
	return [];
}

async function runEventAnalysisWithContext(apiClient: any, eventData: any): Promise<any> {
	// Run AI analysis for market events with context
	return {
		actions_required: false,
		actions: [],
		ai_responses: [],
		impact_assessment: "low"
	};
}

async function executeEventActions(
	apiClient: any,
	portfolioId: string,
	actions: any[],
	config: PortfolioConfig
): Promise<TradingDecision[]> {
	// Execute event-driven actions
	console.log(`📰 Event actions disabled in demo mode for portfolio ${portfolioId}`);
	return [];
}
