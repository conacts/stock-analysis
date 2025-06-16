// Core trading system types

export interface Portfolio {
  id: number;
  name: string;
  cash_balance: number;
  total_value: number;
  created_at: string;
  updated_at: string;
}

export interface Position {
  id: number;
  portfolio_id: number;
  symbol: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  created_at: string;
  updated_at: string;
}

export interface MarketData {
  symbol: string;
  price: number;
  volume: number;
  change: number;
  change_percent: number;
  timestamp: string;
}

export interface TradingSignal {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  price_target?: number;
  stop_loss?: number;
}

export interface AnalysisResult {
  signals: TradingSignal[];
  market_outlook: string;
  risk_assessment: string;
  portfolio_suggestions: string[];
  timestamp: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
  error?: string;
}

// Note: DeepSeek AI types are now provided by the OpenAI SDK

// Environment configuration
export interface Config {
  database_url: string;
  deepseek_api_key: string | undefined;
  alpaca_api_key: string | undefined;
  alpaca_secret_key: string | undefined;
  alpaca_base_url: string;
  environment: 'development' | 'test' | 'production';
}
