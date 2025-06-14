import OpenAI from 'openai';
import { config_instance } from '../utils/config';

export interface DeepSeekAnalysisResult {
	analysis: string;
	confidence: number;
	key_points: string[];
	risk_assessment: string;
	recommendation: 'BUY' | 'SELL' | 'HOLD';
	price_target?: number;
	stop_loss?: number;
}

export interface DeepSeekNewsImpact {
	impact_score: number;
	sentiment: 'positive' | 'negative' | 'neutral';
	key_catalysts: string[];
	market_implications: string[];
	timeline: string;
}

export interface DeepSeekGrowthCatalysts {
	catalysts: Array<{
		catalyst: string;
		impact_potential: 'high' | 'medium' | 'low';
		timeline: string;
		confidence: number;
	}>;
	overall_outlook: string;
	risk_factors: string[];
}

export interface DeepSeekCostSummary {
	total_tokens_used: number;
	total_cost_usd: number;
	api_calls_made: number;
	average_cost_per_call: number;
	cache_hit_rate: number;
}

export class DeepSeekClient {
	private client: OpenAI;
	private model: string = 'deepseek-chat';
	private enableCaching: boolean;
	private responseCache: Map<string, any> = new Map();

	// Cost tracking
	private totalTokensUsed: number = 0;
	private totalCost: number = 0;
	private apiCallsMade: number = 0;

	// Rate limiting
	private lastApiCall: number = 0;
	private minApiInterval: number = 100; // 100ms between calls

	constructor(apiKey?: string, enableCaching: boolean = true) {
		const key = apiKey || config_instance.deepseek_api_key;

		if (!key) {
			throw new Error('DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable.');
		}

		this.enableCaching = enableCaching;

		this.client = new OpenAI({
			baseURL: 'https://api.deepseek.com',
			apiKey: key,
		});
	}

	public async analyzeStockComprehensive(
		symbol: string,
		financialData: Record<string, any>,
		newsData: Array<Record<string, any>>,
		technicalData: Record<string, any>,
		marketContext: Record<string, any>
	): Promise<DeepSeekAnalysisResult> {
		const prompt = this.buildComprehensiveAnalysisPrompt(
			symbol,
			financialData,
			newsData,
			technicalData,
			marketContext
		);

		const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
			{
				role: 'system',
				content: 'You are an expert financial analyst. Provide comprehensive stock analysis with specific recommendations.',
			},
			{
				role: 'user',
				content: prompt,
			},
		];

		const response = await this.makeApiCall(messages, 0.1, 2000);
		return this.parseAnalysisResponse(response.choices[0]?.message?.content || '');
	}

	public async analyzeNewsImpact(
		symbol: string,
		newsData: Array<Record<string, any>>
	): Promise<DeepSeekNewsImpact> {
		const prompt = this.buildNewsAnalysisPrompt(symbol, newsData);

		const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
			{
				role: 'system',
				content: 'You are a financial news analyst. Analyze news impact on stock prices with specific metrics.',
			},
			{
				role: 'user',
				content: prompt,
			},
		];

		const response = await this.makeApiCall(messages, 0.1, 1500);
		return this.parseNewsImpactResponse(response.choices[0]?.message?.content || '');
	}

	public async identifyGrowthCatalysts(
		symbol: string,
		financialData: Record<string, any>,
		newsData: Array<Record<string, any>>
	): Promise<DeepSeekGrowthCatalysts> {
		const prompt = this.buildGrowthCatalystsPrompt(symbol, financialData, newsData);

		const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
			{
				role: 'system',
				content: 'You are a growth investment analyst. Identify key catalysts that could drive stock price appreciation.',
			},
			{
				role: 'user',
				content: prompt,
			},
		];

		const response = await this.makeApiCall(messages, 0.1, 1500);
		return this.parseGrowthCatalystsResponse(response.choices[0]?.message?.content || '');
	}

	public async callWithFunctions(
		messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[],
		tools: OpenAI.Chat.Completions.ChatCompletionTool[],
		maxIterations: number = 10
	): Promise<{
		finalResponse: string;
		functionCalls: Array<{ name: string; arguments: any; result: any }>;
		iterations: number;
	}> {
		const functionCalls: Array<{ name: string; arguments: any; result: any }> = [];
		let currentMessages = [...messages];
		let iteration = 0;

		while (iteration < maxIterations) {
			iteration++;

			const response = await this.makeApiCall(currentMessages, 0.1, 2000, tools);
			const message = response.choices[0]?.message;

			if (!message) {
				break;
			}

			// Add assistant message to conversation
			const assistantMessage: OpenAI.Chat.Completions.ChatCompletionMessageParam = {
				role: 'assistant',
				content: message.content || '',
			};

			if (message.tool_calls) {
				(assistantMessage as any).tool_calls = message.tool_calls;
			}

			currentMessages.push(assistantMessage);

			// Check if there are function calls
			if (message.tool_calls && message.tool_calls.length > 0) {
				for (const toolCall of message.tool_calls) {
					const functionName = toolCall.function.name;
					const functionArgs = JSON.parse(toolCall.function.arguments);

					// Execute function (this would be implemented by the caller)
					const functionResult = { executed: true, args: functionArgs };

					functionCalls.push({
						name: functionName,
						arguments: functionArgs,
						result: functionResult,
					});

					// Add function result to conversation
					currentMessages.push({
						role: 'tool',
						content: JSON.stringify(functionResult),
						tool_call_id: toolCall.id,
					});
				}
			} else {
				// No more function calls, return final response
				return {
					finalResponse: message.content || '',
					functionCalls,
					iterations: iteration,
				};
			}
		}

		return {
			finalResponse: 'Max iterations reached',
			functionCalls,
			iterations: iteration,
		};
	}

	public getCostSummary(): DeepSeekCostSummary {
		const cacheHitRate = this.responseCache.size > 0 ?
			(this.responseCache.size / this.apiCallsMade) * 100 : 0;

		return {
			total_tokens_used: this.totalTokensUsed,
			total_cost_usd: this.totalCost,
			api_calls_made: this.apiCallsMade,
			average_cost_per_call: this.apiCallsMade > 0 ? this.totalCost / this.apiCallsMade : 0,
			cache_hit_rate: cacheHitRate,
		};
	}

	public clearCache(): void {
		this.responseCache.clear();
	}

	private async makeApiCall(
		messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[],
		temperature: number = 0.1,
		maxTokens: number = 2000,
		tools?: OpenAI.Chat.Completions.ChatCompletionTool[]
	): Promise<OpenAI.Chat.Completions.ChatCompletion> {
		// Rate limiting
		const now = Date.now();
		const timeSinceLastCall = now - this.lastApiCall;
		if (timeSinceLastCall < this.minApiInterval) {
			await new Promise(resolve => setTimeout(resolve, this.minApiInterval - timeSinceLastCall));
		}
		this.lastApiCall = Date.now();

		// Check cache
		const cacheKey = this.generateCacheKey(messages, temperature, maxTokens, tools);
		if (this.enableCaching && this.responseCache.has(cacheKey)) {
			return this.responseCache.get(cacheKey);
		}

		try {
			const requestParams: OpenAI.Chat.Completions.ChatCompletionCreateParams = {
				model: this.model,
				messages,
				temperature,
				max_tokens: maxTokens,
			};

			if (tools && tools.length > 0) {
				requestParams.tools = tools;
				requestParams.tool_choice = 'auto';
			}

			const response = await this.client.chat.completions.create(requestParams);

			// Update cost tracking
			this.apiCallsMade++;
			if (response.usage) {
				this.totalTokensUsed += response.usage.total_tokens;
				// DeepSeek pricing: ~$0.14 per 1M input tokens, ~$0.28 per 1M output tokens
				const inputCost = (response.usage.prompt_tokens / 1000000) * 0.14;
				const outputCost = (response.usage.completion_tokens / 1000000) * 0.28;
				this.totalCost += inputCost + outputCost;
			}

			// Cache response
			if (this.enableCaching) {
				this.responseCache.set(cacheKey, response);
			}

			return response;
		} catch (error) {
			console.error('DeepSeek API call failed:', error);
			throw error;
		}
	}

	private generateCacheKey(
		messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[],
		temperature: number,
		maxTokens: number,
		tools?: OpenAI.Chat.Completions.ChatCompletionTool[]
	): string {
		const key = {
			messages: messages.map(m => ({ role: m.role, content: m.content })),
			temperature,
			maxTokens,
			tools: tools?.map(t => t.function.name) || [],
		};
		return JSON.stringify(key);
	}

	private buildComprehensiveAnalysisPrompt(
		symbol: string,
		financialData: Record<string, any>,
		newsData: Array<Record<string, any>>,
		technicalData: Record<string, any>,
		marketContext: Record<string, any>
	): string {
		return `
Analyze ${symbol} comprehensively using the following data:

FINANCIAL DATA:
${JSON.stringify(financialData, null, 2)}

RECENT NEWS:
${newsData.map(news => `- ${news['title']}: ${news['summary']}`).join('\n')}

TECHNICAL INDICATORS:
${JSON.stringify(technicalData, null, 2)}

MARKET CONTEXT:
${JSON.stringify(marketContext, null, 2)}

Provide a comprehensive analysis with:
1. Overall recommendation (BUY/SELL/HOLD)
2. Confidence level (0-100)
3. Key supporting points
4. Risk assessment
5. Price target (if applicable)
6. Stop loss level (if applicable)

Format your response as JSON with the following structure:
{
  "analysis": "detailed analysis text",
  "confidence": 85,
  "key_points": ["point 1", "point 2", "point 3"],
  "risk_assessment": "risk analysis text",
  "recommendation": "BUY",
  "price_target": 150.00,
  "stop_loss": 120.00
}
`;
	}

	private buildNewsAnalysisPrompt(symbol: string, newsData: Array<Record<string, any>>): string {
		return `
Analyze the impact of recent news on ${symbol}:

NEWS ARTICLES:
${newsData.map(news => `
Title: ${news['title']}
Summary: ${news['summary']}
Date: ${news['date']}
`).join('\n')}

Provide a news impact analysis with:
1. Impact score (0-100)
2. Overall sentiment (positive/negative/neutral)
3. Key catalysts identified
4. Market implications
5. Timeline for impact

Format as JSON:
{
  "impact_score": 75,
  "sentiment": "positive",
  "key_catalysts": ["catalyst 1", "catalyst 2"],
  "market_implications": ["implication 1", "implication 2"],
  "timeline": "short-term (1-3 months)"
}
`;
	}

	private buildGrowthCatalystsPrompt(
		symbol: string,
		financialData: Record<string, any>,
		newsData: Array<Record<string, any>>
	): string {
		return `
Identify growth catalysts for ${symbol}:

FINANCIAL DATA:
${JSON.stringify(financialData, null, 2)}

RECENT NEWS:
${newsData.map(news => `- ${news['title']}: ${news['summary']}`).join('\n')}

Identify potential growth catalysts with:
1. Specific catalysts and their impact potential
2. Timeline for each catalyst
3. Confidence level for each
4. Overall growth outlook
5. Key risk factors

Format as JSON:
{
  "catalysts": [
    {
      "catalyst": "catalyst description",
      "impact_potential": "high",
      "timeline": "6-12 months",
      "confidence": 80
    }
  ],
  "overall_outlook": "positive outlook description",
  "risk_factors": ["risk 1", "risk 2"]
}
`;
	}

	private parseAnalysisResponse(content: string): DeepSeekAnalysisResult {
		try {
			const parsed = JSON.parse(content);
			return {
				analysis: parsed.analysis || 'No analysis provided',
				confidence: parsed.confidence || 50,
				key_points: parsed.key_points || [],
				risk_assessment: parsed.risk_assessment || 'No risk assessment provided',
				recommendation: parsed.recommendation || 'HOLD',
				price_target: parsed.price_target,
				stop_loss: parsed.stop_loss,
			};
		} catch (error) {
			// Fallback parsing if JSON fails
			return {
				analysis: content,
				confidence: 50,
				key_points: [],
				risk_assessment: 'Unable to parse structured risk assessment',
				recommendation: 'HOLD',
			};
		}
	}

	private parseNewsImpactResponse(content: string): DeepSeekNewsImpact {
		try {
			const parsed = JSON.parse(content);
			return {
				impact_score: parsed.impact_score || 50,
				sentiment: parsed.sentiment || 'neutral',
				key_catalysts: parsed.key_catalysts || [],
				market_implications: parsed.market_implications || [],
				timeline: parsed.timeline || 'unknown',
			};
		} catch (error) {
			return {
				impact_score: 50,
				sentiment: 'neutral',
				key_catalysts: [],
				market_implications: [],
				timeline: 'unknown',
			};
		}
	}

	private parseGrowthCatalystsResponse(content: string): DeepSeekGrowthCatalysts {
		try {
			const parsed = JSON.parse(content);
			return {
				catalysts: parsed.catalysts || [],
				overall_outlook: parsed.overall_outlook || 'No outlook provided',
				risk_factors: parsed.risk_factors || [],
			};
		} catch (error) {
			return {
				catalysts: [],
				overall_outlook: 'Unable to parse growth outlook',
				risk_factors: [],
			};
		}
	}
} 