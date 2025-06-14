"""
Stock Data Provider

Simple wrapper around yfinance for getting stock data and prices.
"""

import logging
from typing import Any, Dict, Optional

import yfinance as yf


class StockDataProvider:
    """
    Stock data provider using yfinance

    Provides current prices and basic stock information.
    """

    def __init__(self):
        """Initialize stock data provider"""
        self.logger = logging.getLogger(__name__)

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price

        Args:
            symbol: Stock ticker symbol

        Returns:
            Current price or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Try different price fields
            price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")

            if price and price > 0:
                return float(price)

            # Fallback to recent history
            hist = ticker.history(period="1d")
            if not hist.empty:
                return float(hist["Close"].iloc[-1])

            return None

        except Exception as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return None

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get basic stock information

        Args:
            symbol: Stock ticker symbol

        Returns:
            Stock info dict or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or "symbol" not in info:
                return None

            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "current_price": self.get_current_price(symbol),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
            }

        except Exception as e:
            self.logger.error(f"Failed to get info for {symbol}: {e}")
            return None
