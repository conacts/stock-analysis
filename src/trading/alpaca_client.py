"""
Alpaca Paper Trading Client
Handles all interactions with Alpaca's Paper Trading API
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import ClosePositionRequest, GetOrdersRequest, LimitOrderRequest, MarketOrderRequest

logger = logging.getLogger(__name__)


class AlpacaPaperTradingClient:
    """
    Alpaca Paper Trading Client for AI-driven trading
    """

    def __init__(self):
        """Initialize Alpaca client with paper trading credentials"""
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found in environment variables")

        # Initialize trading client (using positional args like in working test)
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper=True)

        # Initialize data client with credentials
        self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)

        logger.info("✅ Alpaca Paper Trading Client initialized")

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information and buying power"""
        try:
            account = self.trading_client.get_account()
            return {
                "account_id": account.id,
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "equity": float(account.equity),
                "day_trade_count": account.daytrade_count,
                "pattern_day_trader": account.pattern_day_trader,
                "status": account.status.value,
                "created_at": account.created_at.isoformat() if account.created_at else None,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get account info: {e}")
            raise

    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions"""
        try:
            positions = self.trading_client.get_all_positions()
            return [
                {
                    "symbol": pos.symbol,
                    "quantity": float(pos.qty),
                    "market_value": float(pos.market_value) if pos.market_value else 0,
                    "cost_basis": float(pos.cost_basis) if pos.cost_basis else 0,
                    "unrealized_pl": float(pos.unrealized_pl) if pos.unrealized_pl else 0,
                    "unrealized_plpc": float(pos.unrealized_plpc) if pos.unrealized_plpc else 0,
                    "current_price": float(pos.current_price) if pos.current_price else 0,
                    "side": pos.side.value,
                    "avg_entry_price": float(pos.avg_entry_price) if pos.avg_entry_price else 0,
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            raise

    async def place_market_order(self, symbol: str, quantity: float, side: str, time_in_force: str = "day") -> Dict[str, Any]:
        """
        Place a market order

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            quantity: Number of shares
            side: 'buy' or 'sell'
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
        """
        try:
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            tif = TimeInForce.DAY if time_in_force.lower() == "day" else TimeInForce.GTC

            market_order_data = MarketOrderRequest(symbol=symbol, qty=quantity, side=order_side, time_in_force=tif)

            order = self.trading_client.submit_order(order_data=market_order_data)

            result = {
                "order_id": order.id,
                "symbol": order.symbol,
                "quantity": float(order.qty),
                "side": order.side.value,
                "order_type": order.order_type.value,
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0,
            }

            logger.info(f"✅ Market order placed: {side.upper()} {quantity} {symbol} - Order ID: {order.id}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to place market order: {e}")
            raise

    async def place_limit_order(self, symbol: str, quantity: float, side: str, limit_price: float, time_in_force: str = "day") -> Dict[str, Any]:
        """
        Place a limit order

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            quantity: Number of shares
            side: 'buy' or 'sell'
            limit_price: Limit price for the order
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
        """
        try:
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            tif = TimeInForce.DAY if time_in_force.lower() == "day" else TimeInForce.GTC

            limit_order_data = LimitOrderRequest(symbol=symbol, qty=quantity, side=order_side, time_in_force=tif, limit_price=limit_price)

            order = self.trading_client.submit_order(order_data=limit_order_data)

            result = {
                "order_id": order.id,
                "symbol": order.symbol,
                "quantity": float(order.qty),
                "side": order.side.value,
                "order_type": order.order_type.value,
                "limit_price": float(order.limit_price) if order.limit_price else 0,
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0,
            }

            logger.info(f"✅ Limit order placed: {side.upper()} {quantity} {symbol} @ ${limit_price} - Order ID: {order.id}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to place limit order: {e}")
            raise

    async def get_orders(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get orders with optional status filter

        Args:
            status: Filter by status ('open', 'closed', 'all')
            limit: Maximum number of orders to return
        """
        try:
            request = GetOrdersRequest(status=status, limit=limit)

            orders = self.trading_client.get_orders(filter=request)

            return [
                {
                    "order_id": order.id,
                    "symbol": order.symbol,
                    "quantity": float(order.qty),
                    "side": order.side.value,
                    "order_type": order.order_type.value,
                    "status": order.status.value,
                    "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                    "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                    "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                    "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "stop_price": float(order.stop_price) if order.stop_price else None,
                }
                for order in orders
            ]

        except Exception as e:
            logger.error(f"❌ Failed to get orders: {e}")
            raise

    async def get_position(self, symbol: str) -> Dict[str, Any]:
        """Get position for a specific symbol"""
        try:
            position = self.trading_client.get_open_position(symbol)
            return {
                "symbol": position.symbol,
                "quantity": float(position.qty),
                "market_value": float(position.market_value) if position.market_value else 0,
                "cost_basis": float(position.cost_basis) if position.cost_basis else 0,
                "unrealized_pl": float(position.unrealized_pl) if position.unrealized_pl else 0,
                "unrealized_plpc": float(position.unrealized_plpc) if position.unrealized_plpc else 0,
                "current_price": float(position.current_price) if position.current_price else 0,
                "side": position.side.value,
                "avg_entry_price": float(position.avg_entry_price) if position.avg_entry_price else 0,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get position for {symbol}: {e}")
            raise

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an open order"""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"✅ Order cancelled: {order_id}")
            return {"order_id": order_id, "status": "cancelled"}
        except Exception as e:
            logger.error(f"❌ Failed to cancel order {order_id}: {e}")
            raise

    async def close_position(self, symbol: str, percentage: Optional[float] = None) -> Dict[str, Any]:
        """
        Close a position (partial or full)

        Args:
            symbol: Stock symbol
            percentage: Percentage to close (None for 100%)
        """
        try:
            close_request = ClosePositionRequest(qty=str(percentage) if percentage else None)

            order = self.trading_client.close_position(symbol, close_request)

            result = {"order_id": order.id, "symbol": order.symbol, "quantity": float(order.qty), "side": order.side.value, "status": order.status.value, "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None}

            logger.info(f"✅ Position closed: {symbol} - Order ID: {order.id}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to close position {symbol}: {e}")
            raise

    async def close_all_positions(self) -> Dict[str, Any]:
        """Close all open positions"""
        try:
            orders = self.trading_client.close_all_positions(cancel_orders=True)
            logger.info(f"✅ All positions closed: {len(orders)} orders created")
            return {"orders_created": len(orders), "orders": [{"order_id": order.id, "symbol": order.symbol, "quantity": float(order.qty), "side": order.side.value, "status": order.status.value} for order in orders]}
        except Exception as e:
            logger.error(f"❌ Failed to close all positions: {e}")
            raise

    async def cancel_all_orders(self) -> Dict[str, Any]:
        """Cancel all open orders"""
        try:
            orders = self.trading_client.cancel_orders()
            logger.info(f"✅ All orders cancelled: {len(orders)} orders")
            return {"orders_cancelled": len(orders), "orders": [{"order_id": order.id, "symbol": order.symbol, "status": order.status.value} for order in orders]}
        except Exception as e:
            logger.error(f"❌ Failed to cancel all orders: {e}")
            raise

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get specific order by ID"""
        try:
            order = self.trading_client.get_order_by_id(order_id)
            return {
                "order_id": order.id,
                "symbol": order.symbol,
                "quantity": float(order.qty),
                "side": order.side.value,
                "order_type": order.order_type.value,
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0,
                "limit_price": float(order.limit_price) if order.limit_price else None,
                "stop_price": float(order.stop_price) if order.stop_price else None,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get order {order_id}: {e}")
            raise

    async def get_market_data(self, symbol: str, timeframe: str = "1Day", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get historical market data

        Args:
            symbol: Stock symbol
            timeframe: '1Min', '5Min', '15Min', '30Min', '1Hour', '1Day'
            start_date: Start date for data
            end_date: End date for data
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Map timeframe string to TimeFrame enum
            timeframe_map = {"1Min": TimeFrame.Minute, "5Min": TimeFrame(5, "Min"), "15Min": TimeFrame(15, "Min"), "30Min": TimeFrame(30, "Min"), "1Hour": TimeFrame.Hour, "1Day": TimeFrame.Day}

            tf = timeframe_map.get(timeframe, TimeFrame.Day)

            request_params = StockBarsRequest(symbol_or_symbols=[symbol], timeframe=tf, start=start_date, end=end_date)

            bars = self.data_client.get_stock_bars(request_params)

            # Convert to list of dictionaries
            bars_data = []
            for bar in bars[symbol]:
                bars_data.append({"timestamp": bar.timestamp.isoformat(), "open": float(bar.open), "high": float(bar.high), "low": float(bar.low), "close": float(bar.close), "volume": int(bar.volume), "vwap": float(bar.vwap) if bar.vwap else None})

            logger.info(f"✅ Retrieved {len(bars_data)} bars for {symbol}")
            return {"symbol": symbol, "timeframe": timeframe, "bars": bars_data, "count": len(bars_data)}

        except Exception as e:
            logger.error(f"❌ Failed to get market data for {symbol}: {e}")
            raise

    async def get_market_status(self) -> Dict[str, Any]:
        """Get comprehensive market status"""
        try:
            clock = self.trading_client.get_clock()
            return {"is_open": clock.is_open, "next_open": clock.next_open.isoformat() if clock.next_open else None, "next_close": clock.next_close.isoformat() if clock.next_close else None, "timezone": "America/New_York"}
        except Exception as e:
            logger.error(f"❌ Failed to get market status: {e}")
            raise

    def is_market_open(self) -> bool:
        """Check if the market is currently open"""
        try:
            clock = self.trading_client.get_clock()
            return clock.is_open
        except Exception as e:
            logger.error(f"❌ Failed to check market status: {e}")
            return False

    def get_market_calendar(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get market calendar"""
        try:
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=7)

            calendar = self.trading_client.get_calendar(start_date, end_date)

            return [{"date": day.date.isoformat(), "open": day.open.isoformat(), "close": day.close.isoformat()} for day in calendar]

        except Exception as e:
            logger.error(f"❌ Failed to get market calendar: {e}")
            raise


def create_alpaca_client() -> AlpacaPaperTradingClient:
    """Factory function to create Alpaca client"""
    return AlpacaPaperTradingClient()


# Test function
def test_alpaca_connection():
    """Test Alpaca connection and basic functionality"""
    try:
        print("🧪 Testing Alpaca Paper Trading Connection")
        print("=" * 50)

        # Test direct client creation first
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")

        if not api_key or not secret_key:
            print("❌ Environment variables not found")
            return False

        print(f"🔑 API Key: {api_key[:10]}...")
        print(f"🔐 Secret Key: {secret_key[:10]}...")

        # Test direct TradingClient (this works)
        from alpaca.trading.client import TradingClient

        direct_client = TradingClient(api_key, secret_key, paper=True)
        account = direct_client.get_account()
        print(f"✅ Direct client works: ${float(account.buying_power):,.2f}")

        # Now test our class
        client = create_alpaca_client()

        # Test account info
        account_info = client.get_account_info()
        print(f"✅ Account ID: {account_info['account_id']}")
        print(f"💰 Buying Power: ${account_info['buying_power']:,.2f}")
        print(f"💵 Cash: ${account_info['cash']:,.2f}")
        print(f"📊 Portfolio Value: ${account_info['portfolio_value']:,.2f}")

        # Test market status
        is_open = client.is_market_open()
        print(f"🏪 Market Open: {is_open}")

        # Test positions
        positions = client.get_positions()
        print(f"📈 Current Positions: {len(positions)}")

        # Test recent orders
        orders = client.get_orders(limit=5)
        print(f"📋 Recent Orders: {len(orders)}")

        print("\n🎉 Alpaca connection test successful!")
        return True

    except Exception as e:
        print(f"❌ Alpaca connection test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_alpaca_connection()
