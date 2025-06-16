import axios, { AxiosInstance } from 'axios';
import { ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL } from '@/utils/config';

export interface AlpacaAccount {
  id: string;
  account_number: string;
  status: string;
  currency: string;
  buying_power: number;
  regt_buying_power: number;
  daytrading_buying_power: number;
  cash: number;
  portfolio_value: number;
  equity: number;
  last_equity: number;
  multiplier: number;
  initial_margin: number;
  maintenance_margin: number;
  sma: number;
  daytrade_count: number;
}

export interface AlpacaPosition {
  asset_id: string;
  symbol: string;
  exchange: string;
  asset_class: string;
  qty: number;
  avg_entry_price: number;
  side: 'long' | 'short';
  market_value: number;
  cost_basis: number;
  unrealized_pl: number;
  unrealized_plpc: number;
  unrealized_intraday_pl: number;
  unrealized_intraday_plpc: number;
  current_price: number;
  lastday_price: number;
  change_today: number;
}

export interface AlpacaOrder {
  id: string;
  client_order_id: string;
  created_at: string;
  updated_at: string;
  submitted_at: string;
  filled_at?: string;
  expired_at?: string;
  canceled_at?: string;
  failed_at?: string;
  replaced_at?: string;
  replaced_by?: string;
  replaces?: string;
  asset_id: string;
  symbol: string;
  asset_class: string;
  notional?: number;
  qty?: number;
  filled_qty: number;
  filled_avg_price?: number;
  order_class: string;
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'trailing_stop';
  type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'trailing_stop';
  side: 'buy' | 'sell';
  time_in_force: 'day' | 'gtc' | 'ioc' | 'fok' | 'opg' | 'cls';
  limit_price?: number;
  stop_price?: number;
  status:
    | 'new'
    | 'partially_filled'
    | 'filled'
    | 'done_for_day'
    | 'canceled'
    | 'expired'
    | 'replaced'
    | 'pending_cancel'
    | 'pending_replace'
    | 'accepted'
    | 'pending_new'
    | 'accepted_for_bidding'
    | 'stopped'
    | 'rejected'
    | 'suspended'
    | 'calculated';
  extended_hours: boolean;
  legs?: AlpacaOrder[];
  trail_percent?: number;
  trail_price?: number;
  hwm?: number;
}

export interface AlpacaBar {
  t: string; // timestamp
  o: number; // open
  h: number; // high
  l: number; // low
  c: number; // close
  v: number; // volume
  n: number; // trade count
  vw: number; // volume weighted average price
}

export interface MarketCalendar {
  date: string;
  open: string;
  close: string;
  session_open: string;
  session_close: string;
}

export interface MarketClock {
  timestamp: string;
  is_open: boolean;
  next_open: string;
  next_close: string;
}

export interface OrderRequest {
  symbol: string;
  qty?: number;
  notional?: number;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'trailing_stop';
  time_in_force: 'day' | 'gtc' | 'ioc' | 'fok' | 'opg' | 'cls';
  limit_price?: number;
  stop_price?: number;
  trail_price?: number;
  trail_percent?: number;
  extended_hours?: boolean;
  client_order_id?: string;
  order_class?: 'simple' | 'bracket' | 'oco' | 'oto';
  take_profit?: {
    limit_price: number;
  };
  stop_loss?: {
    stop_price: number;
    limit_price?: number;
  };
}

export class AlpacaClient {
  private client: AxiosInstance;
  private dataClient: AxiosInstance;
  private apiKey: string;
  private secretKey: string;
  private baseUrl: string;
  private dataUrl: string = 'https://data.alpaca.markets';

  constructor(apiKey?: string, secretKey?: string, baseUrl?: string, isPaper: boolean = true) {
    this.apiKey = apiKey || ALPACA_API_KEY || '';
    this.secretKey = secretKey || ALPACA_SECRET_KEY || '';
    this.baseUrl =
      baseUrl ||
      ALPACA_BASE_URL ||
      (isPaper ? 'https://paper-api.alpaca.markets' : 'https://api.alpaca.markets');

    if (!this.apiKey || !this.secretKey) {
      throw new Error(
        'Alpaca API key and secret key are required. Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables.'
      );
    }

    const headers = {
      'APCA-API-KEY-ID': this.apiKey,
      'APCA-API-SECRET-KEY': this.secretKey,
      'Content-Type': 'application/json',
    };

    this.client = axios.create({
      baseURL: this.baseUrl,
      headers,
      timeout: 30000,
    });

    this.dataClient = axios.create({
      baseURL: this.dataUrl,
      headers,
      timeout: 30000,
    });
  }

  // Account Management
  public async getAccount(): Promise<AlpacaAccount> {
    const response = await this.client.get<AlpacaAccount>('/v2/account');
    return response.data;
  }

  public async getAccountConfigurations(): Promise<any> {
    const response = await this.client.get('/v2/account/configurations');
    return response.data;
  }

  public async updateAccountConfigurations(config: any): Promise<any> {
    const response = await this.client.patch('/v2/account/configurations', config);
    return response.data;
  }

  // Positions
  public async getPositions(): Promise<AlpacaPosition[]> {
    const response = await this.client.get<AlpacaPosition[]>('/v2/positions');
    return response.data;
  }

  public async getPosition(symbol: string): Promise<AlpacaPosition> {
    const response = await this.client.get<AlpacaPosition>(`/v2/positions/${symbol}`);
    return response.data;
  }

  public async closePosition(
    symbol: string,
    qty?: number,
    percentage?: number
  ): Promise<AlpacaOrder> {
    const params: any = {};
    if (qty !== undefined) params.qty = qty;
    if (percentage !== undefined) params.percentage = percentage;

    const response = await this.client.delete<AlpacaOrder>(`/v2/positions/${symbol}`, { params });
    return response.data;
  }

  public async closeAllPositions(cancelOrders: boolean = false): Promise<AlpacaOrder[]> {
    const params = cancelOrders ? { cancel_orders: true } : {};
    const response = await this.client.delete<AlpacaOrder[]>('/v2/positions', { params });
    return response.data;
  }

  // Orders
  public async getOrders(
    status?: 'open' | 'closed' | 'all',
    limit?: number,
    after?: string,
    until?: string,
    direction?: 'asc' | 'desc',
    nested?: boolean,
    symbols?: string[]
  ): Promise<AlpacaOrder[]> {
    const params: any = {};
    if (status) params.status = status;
    if (limit) params.limit = limit;
    if (after) params.after = after;
    if (until) params.until = until;
    if (direction) params.direction = direction;
    if (nested !== undefined) params.nested = nested;
    if (symbols) params.symbols = symbols.join(',');

    const response = await this.client.get<AlpacaOrder[]>('/v2/orders', { params });
    return response.data;
  }

  public async getOrder(orderId: string, nested?: boolean): Promise<AlpacaOrder> {
    const params = nested !== undefined ? { nested } : {};
    const response = await this.client.get<AlpacaOrder>(`/v2/orders/${orderId}`, { params });
    return response.data;
  }

  public async createOrder(orderRequest: OrderRequest): Promise<AlpacaOrder> {
    const response = await this.client.post<AlpacaOrder>('/v2/orders', orderRequest);
    return response.data;
  }

  public async replaceOrder(
    orderId: string,
    orderRequest: Partial<OrderRequest>
  ): Promise<AlpacaOrder> {
    const response = await this.client.patch<AlpacaOrder>(`/v2/orders/${orderId}`, orderRequest);
    return response.data;
  }

  public async cancelOrder(orderId: string): Promise<void> {
    await this.client.delete(`/v2/orders/${orderId}`);
  }

  public async cancelAllOrders(): Promise<AlpacaOrder[]> {
    const response = await this.client.delete<AlpacaOrder[]>('/v2/orders');
    return response.data;
  }

  // Market Data
  public async getBars(
    symbols: string[],
    timeframe: '1Min' | '5Min' | '15Min' | '30Min' | '1Hour' | '1Day' = '1Day',
    start?: string,
    end?: string,
    limit?: number,
    adjustment?: 'raw' | 'split' | 'dividend' | 'all'
  ): Promise<{ bars: Record<string, AlpacaBar[]> }> {
    const params: any = {
      symbols: symbols.join(','),
      timeframe,
    };
    if (start) params.start = start;
    if (end) params.end = end;
    if (limit) params.limit = limit;
    if (adjustment) params.adjustment = adjustment;

    const response = await this.dataClient.get('/v2/stocks/bars', { params });
    return response.data;
  }

  public async getLatestBars(symbols: string[]): Promise<{ bars: Record<string, AlpacaBar> }> {
    const params = { symbols: symbols.join(',') };
    const response = await this.dataClient.get('/v2/stocks/bars/latest', { params });
    return response.data;
  }

  public async getTrades(
    symbols: string[],
    start?: string,
    end?: string,
    limit?: number
  ): Promise<any> {
    const params: any = { symbols: symbols.join(',') };
    if (start) params.start = start;
    if (end) params.end = end;
    if (limit) params.limit = limit;

    const response = await this.dataClient.get('/v2/stocks/trades', { params });
    return response.data;
  }

  public async getQuotes(
    symbols: string[],
    start?: string,
    end?: string,
    limit?: number
  ): Promise<any> {
    const params: any = { symbols: symbols.join(',') };
    if (start) params.start = start;
    if (end) params.end = end;
    if (limit) params.limit = limit;

    const response = await this.dataClient.get('/v2/stocks/quotes', { params });
    return response.data;
  }

  public async getLatestQuotes(symbols: string[]): Promise<any> {
    const params = { symbols: symbols.join(',') };
    const response = await this.dataClient.get('/v2/stocks/quotes/latest', { params });
    return response.data;
  }

  // Market Status
  public async getMarketCalendar(start?: string, end?: string): Promise<MarketCalendar[]> {
    const params: any = {};
    if (start) params.start = start;
    if (end) params.end = end;

    const response = await this.client.get<MarketCalendar[]>('/v2/calendar', { params });
    return response.data;
  }

  public async getMarketClock(): Promise<MarketClock> {
    const response = await this.client.get<MarketClock>('/v2/clock');
    return response.data;
  }

  // Convenience Methods
  public async buyMarket(
    symbol: string,
    qty: number,
    extendedHours: boolean = false
  ): Promise<AlpacaOrder> {
    return this.createOrder({
      symbol,
      qty,
      side: 'buy',
      type: 'market',
      time_in_force: 'day',
      extended_hours: extendedHours,
    });
  }

  public async sellMarket(
    symbol: string,
    qty: number,
    extendedHours: boolean = false
  ): Promise<AlpacaOrder> {
    return this.createOrder({
      symbol,
      qty,
      side: 'sell',
      type: 'market',
      time_in_force: 'day',
      extended_hours: extendedHours,
    });
  }

  public async buyLimit(
    symbol: string,
    qty: number,
    limitPrice: number,
    timeInForce: 'day' | 'gtc' = 'day',
    extendedHours: boolean = false
  ): Promise<AlpacaOrder> {
    return this.createOrder({
      symbol,
      qty,
      side: 'buy',
      type: 'limit',
      limit_price: limitPrice,
      time_in_force: timeInForce,
      extended_hours: extendedHours,
    });
  }

  public async sellLimit(
    symbol: string,
    qty: number,
    limitPrice: number,
    timeInForce: 'day' | 'gtc' = 'day',
    extendedHours: boolean = false
  ): Promise<AlpacaOrder> {
    return this.createOrder({
      symbol,
      qty,
      side: 'sell',
      type: 'limit',
      limit_price: limitPrice,
      time_in_force: timeInForce,
      extended_hours: extendedHours,
    });
  }

  public async bracketOrder(
    symbol: string,
    qty: number,
    side: 'buy' | 'sell',
    takeProfitPrice: number,
    stopLossPrice: number,
    limitPrice?: number
  ): Promise<AlpacaOrder> {
    const orderRequest: OrderRequest = {
      symbol,
      qty,
      side,
      type: limitPrice ? 'limit' : 'market',
      time_in_force: 'day',
      order_class: 'bracket',
      take_profit: {
        limit_price: takeProfitPrice,
      },
      stop_loss: {
        stop_price: stopLossPrice,
      },
    };

    if (limitPrice) {
      orderRequest.limit_price = limitPrice;
    }

    return this.createOrder(orderRequest);
  }

  // Portfolio Analysis Helpers
  public async getPortfolioSummary(): Promise<{
    account: AlpacaAccount;
    positions: AlpacaPosition[];
    totalValue: number;
    totalPnL: number;
    totalPnLPercent: number;
    positionsCount: number;
    cashBalance: number;
    buyingPower: number;
  }> {
    const [account, positions] = await Promise.all([this.getAccount(), this.getPositions()]);

    const totalValue = account.portfolio_value;
    const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pl, 0);
    const totalPnLPercent = totalValue > 0 ? (totalPnL / (totalValue - totalPnL)) * 100 : 0;

    return {
      account,
      positions,
      totalValue,
      totalPnL,
      totalPnLPercent,
      positionsCount: positions.length,
      cashBalance: account.cash,
      buyingPower: account.buying_power,
    };
  }

  public async isMarketOpen(): Promise<boolean> {
    const clock = await this.getMarketClock();
    return clock.is_open;
  }

  public async waitForMarketOpen(checkIntervalMs: number = 60000): Promise<void> {
    while (!(await this.isMarketOpen())) {
      console.log('Market is closed, waiting...');
      await new Promise(resolve => setTimeout(resolve, checkIntervalMs));
    }
    console.log('Market is now open!');
  }
}
