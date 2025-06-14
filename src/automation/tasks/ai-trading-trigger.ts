import { task } from "@trigger.dev/sdk/v3";
import { validateEnv } from "../shared/env-validation";

interface ConversationMessage {
	role: "user" | "assistant" | "system";
	content: string;
	timestamp?: string;
}

interface AITradingTriggerPayload {
	conversation_messages: ConversationMessage[];
	context: string;
	symbols?: string[];
	trigger_reason: string;
	portfolio_id?: number;
}

export const aiTradingDecisionTask = task({
	id: "ai-trading-decision",
	run: async (payload: AITradingTriggerPayload) => {
		console.log("🤖 AI Trading Decision Task Started");
		console.log(`📝 Context: ${payload.context}`);
		console.log(`💬 Messages: ${payload.conversation_messages.length}`);
		console.log(`🎯 Symbols: ${payload.symbols?.join(", ") || "None specified"}`);
		console.log(`🔔 Trigger: ${payload.trigger_reason}`);

		const env = validateEnv();

		try {
			// Prepare the AI trading request
			const aiRequest = {
				context: payload.context,
				symbols: payload.symbols || [],
				conversation_messages: payload.conversation_messages.map(msg => ({
					role: msg.role,
					content: msg.content
				})),
				portfolio_id: payload.portfolio_id,
				max_iterations: 25
			};

			console.log("🚀 Sending request to AI trading endpoint...");

			// Call the AI trading endpoint
			const response = await fetch(`${env.API_BASE_URL}/trading/ai-trade`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"Authorization": `Bearer ${env.API_TOKEN}`
				},
				body: JSON.stringify(aiRequest)
			});

			if (!response.ok) {
				const errorText = await response.text();
				throw new Error(`AI trading request failed: ${response.status} - ${errorText}`);
			}

			const result = await response.json();

			console.log("✅ AI Trading Analysis Complete");
			console.log(`🧠 AI Response: ${result.ai_response?.substring(0, 200)}...`);
			console.log(`📊 Trade Actions: ${result.trade_actions?.length || 0}`);
			console.log(`🔄 Iterations: ${result.total_iterations}`);

			// Log any trades that were executed
			if (result.trade_actions && result.trade_actions.length > 0) {
				console.log("💰 TRADES EXECUTED:");
				for (const trade of result.trade_actions) {
					const args = trade.arguments;
					console.log(`  🔸 ${args.side.toUpperCase()} ${args.quantity} ${args.symbol} ${args.limit_price ? `@ $${args.limit_price}` : '(MARKET)'}`);
					console.log(`  📝 Reason: ${args.reason}`);
					console.log(`  ⏰ Time: ${trade.timestamp}`);
				}
			} else {
				console.log("📈 No trades executed - AI chose to hold or wait");
			}

			// Store the conversation and results in database if portfolio_id provided
			if (payload.portfolio_id) {
				try {
					const storeResponse = await fetch(`${env.API_BASE_URL}/portfolio/store-analysis`, {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
							"Authorization": `Bearer ${env.API_TOKEN}`
						},
						body: JSON.stringify({
							portfolio_id: payload.portfolio_id,
							analysis_type: "ai_trading_decision",
							analysis_result: result,
							conversation_context: payload.conversation_messages,
							symbols_analyzed: payload.symbols || [],
							timestamp: new Date().toISOString()
						})
					});

					if (storeResponse.ok) {
						console.log("💾 Analysis results stored in database");
					} else {
						console.log("⚠️ Failed to store analysis results");
					}
				} catch (storeError) {
					console.log("⚠️ Error storing analysis results:", storeError);
				}
			}

			return {
				success: true,
				ai_response: result.ai_response,
				trade_actions: result.trade_actions || [],
				total_iterations: result.total_iterations,
				conversation_length: result.conversation_length,
				trigger_reason: payload.trigger_reason,
				timestamp: new Date().toISOString()
			};

		} catch (error) {
			console.error("❌ AI Trading Decision Task Failed:", error);

			return {
				success: false,
				error: error instanceof Error ? error.message : String(error),
				trigger_reason: payload.trigger_reason,
				timestamp: new Date().toISOString()
			};
		}
	},
});

// Scheduled task to check for trading opportunities
export const scheduledTradingAnalysis = task({
	id: "scheduled-trading-analysis",
	run: async () => {
		console.log("📅 Scheduled Trading Analysis Started");

		const env = validateEnv();

		try {
			// Get recent portfolio analysis or market news
			const context = `Scheduled market analysis at ${new Date().toISOString()}.
      Please analyze current market conditions, check my portfolio performance,
      and make any necessary trading adjustments. Consider:
      - Market trends and momentum
      - Portfolio balance and risk exposure
      - Recent news or market events
      - Technical indicators`;

			// Trigger AI trading analysis
			const result = await aiTradingDecisionTask.trigger({
				conversation_messages: [
					{
						role: "system",
						content: "You are conducting a scheduled portfolio review and trading analysis."
					}
				],
				context: context,
				symbols: ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"], // Focus symbols
				trigger_reason: "scheduled_analysis"
			});

			console.log("✅ Scheduled trading analysis triggered");
			return { success: true, task_id: result.id };

		} catch (error) {
			console.error("❌ Scheduled Trading Analysis Failed:", error);
			return {
				success: false,
				error: error instanceof Error ? error.message : String(error)
			};
		}
	},
});

// Market event triggered trading
export const marketEventTradingTrigger = task({
	id: "market-event-trading",
	run: async (payload: {
		event_type: string;
		event_description: string;
		affected_symbols?: string[];
		severity: "low" | "medium" | "high";
	}) => {
		console.log("📰 Market Event Trading Trigger");
		console.log(`🚨 Event: ${payload.event_type}`);
		console.log(`📝 Description: ${payload.event_description}`);
		console.log(`⚡ Severity: ${payload.severity}`);

		const context = `MARKET EVENT ALERT: ${payload.event_type}

    Description: ${payload.event_description}
    Severity: ${payload.severity}
    Affected Symbols: ${payload.affected_symbols?.join(", ") || "Market-wide"}

    Please analyze this market event and determine if any trading actions are needed.
    Consider the impact on my current positions and potential opportunities.`;

		// Trigger AI trading analysis for market event
		const result = await aiTradingDecisionTask.trigger({
			conversation_messages: [
				{
					role: "system",
					content: "You are responding to a significant market event that may require immediate trading action."
				}
			],
			context: context,
			symbols: payload.affected_symbols,
			trigger_reason: `market_event_${payload.event_type}`
		});

		console.log("✅ Market event trading analysis triggered");
		return { success: true, task_id: result.id, event_type: payload.event_type };
	},
});
