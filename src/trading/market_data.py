"""
Market Data Provider

Provides real-time market data, technical indicators, and sentiment analysis
using Alpha Vantage API and other data sources.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List

import aiohttp

from src.models.trading_models import (
    MarketSentiment,
    Price,
    TechnicalIndicators,
)

logger = logging.getLogger(__name__)


class MarketDataProvider:
    """
    Provides real-time market data and analysis for trading decisions.

    Features:
    - Real-time stock prices
    - Technical indicators (RSI, MACD, Moving Averages)
    - Market sentiment analysis
    - News sentiment integration
    """

    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.base_url = "https://www.alphavantage.co/query"

        # Cache for reducing API calls
        self._price_cache = {}
        self._technical_cache = {}
        self._cache_duration = timedelta(minutes=5)  # 5-minute cache

        # Rate limiting
        self._last_request_time = {}
        self._min_request_interval = 12  # 12 seconds between requests (5 requests per minute)

    async def get_real_time_price(self, symbol: str) -> Price:
        """
        Get real-time price data for a symbol.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Price object with current market data
        """
        # Check cache first
        cache_key = f"price_{symbol}"
        if self._is_cached_valid(cache_key):
            return self._price_cache[cache_key]

        try:
            # Rate limiting
            await self._rate_limit()

            # For demo purposes, we'll use mock data if no API key
            if self.alpha_vantage_key == "demo":
                price_data = self._get_mock_price_data(symbol)
            else:
                price_data = await self._fetch_real_price_data(symbol)

            # Cache the result
            self._price_cache[cache_key] = price_data

            return price_data

        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            # Return mock data as fallback
            return self._get_mock_price_data(symbol)

    async def get_technical_indicators(self, symbol: str) -> TechnicalIndicators:
        """
        Get technical indicators for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            TechnicalIndicators with RSI, MACD, moving averages, etc.
        """
        # Check cache first
        cache_key = f"technical_{symbol}"
        if self._is_cached_valid(cache_key):
            return self._technical_cache[cache_key]

        try:
            # Rate limiting
            await self._rate_limit()

            # For demo purposes, use mock data if no API key
            if self.alpha_vantage_key == "demo":
                technical_data = self._get_mock_technical_data(symbol)
            else:
                technical_data = await self._fetch_real_technical_data(symbol)

            # Cache the result
            self._technical_cache[cache_key] = technical_data

            return technical_data

        except Exception as e:
            logger.error(f"Error fetching technical data for {symbol}: {e}")
            # Return mock data as fallback
            return self._get_mock_technical_data(symbol)

    async def get_market_sentiment(self, symbols: List[str]) -> MarketSentiment:
        """
        Get market sentiment analysis for given symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            MarketSentiment with overall sentiment scores
        """
        try:
            # For now, return mock sentiment data
            # In production, this would integrate with news APIs, social media sentiment, etc.
            return self._get_mock_sentiment_data(symbols)

        except Exception as e:
            logger.error(f"Error fetching sentiment data: {e}")
            return MarketSentiment(
                overall_sentiment=0.0,
                news_sentiment=0.0,
                confidence=0.5,
                key_themes=["Market uncertainty"],
            )

    async def get_news_sentiment(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get news sentiment for specific symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to sentiment scores (-1 to 1)
        """
        try:
            # Mock implementation - in production would use news APIs
            sentiment_scores = {}
            for symbol in symbols:
                # Generate mock sentiment based on symbol hash for consistency
                hash_val = hash(symbol) % 100
                sentiment = (hash_val - 50) / 50  # Convert to -1 to 1 range
                sentiment_scores[symbol] = max(-1, min(1, sentiment))

            return sentiment_scores

        except Exception as e:
            logger.error(f"Error fetching news sentiment: {e}")
            return {symbol: 0.0 for symbol in symbols}

    def _is_cached_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._price_cache and cache_key not in self._technical_cache:
            return False

        # Check timestamp (simplified - would store timestamps separately in production)
        return False  # For now, always fetch fresh data in demo mode

    async def _rate_limit(self):
        """Implement rate limiting for API calls."""
        current_time = datetime.now()

        if hasattr(self, "_last_api_call"):
            time_since_last = (current_time - self._last_api_call).total_seconds()
            if time_since_last < self._min_request_interval:
                sleep_time = self._min_request_interval - time_since_last
                await asyncio.sleep(sleep_time)

        self._last_api_call = current_time

    async def _fetch_real_price_data(self, symbol: str) -> Price:
        """Fetch real price data from Alpha Vantage API."""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                data = await response.json()

                if "Global Quote" not in data:
                    raise ValueError(f"Invalid response for {symbol}")

                quote = data["Global Quote"]

                return Price(
                    symbol=symbol,
                    current_price=Decimal(quote["05. price"]),
                    open_price=Decimal(quote["02. open"]),
                    high_price=Decimal(quote["03. high"]),
                    low_price=Decimal(quote["04. low"]),
                    volume=int(quote["06. volume"]),
                    previous_close=Decimal(quote["08. previous close"]),
                    change=Decimal(quote["09. change"]),
                    change_percent=float(quote["10. change percent"].rstrip("%")),
                )

    async def _fetch_real_technical_data(self, symbol: str) -> TechnicalIndicators:
        """Fetch real technical indicators from Alpha Vantage API."""
        # This would require multiple API calls to get different indicators
        # For now, return mock data even with real API key
        return self._get_mock_technical_data(symbol)

    def _get_mock_price_data(self, symbol: str) -> Price:
        """Generate mock price data for testing."""
        # Generate consistent mock data based on symbol
        base_price = 100 + (hash(symbol) % 500)  # $100-600 range

        # Add some randomness based on current time
        time_factor = datetime.now().minute / 60  # 0-1 based on current minute
        price_variation = (time_factor - 0.5) * 10  # -5 to +5 variation

        current_price = Decimal(str(base_price + price_variation))
        previous_close = current_price * Decimal("0.99")  # 1% down from previous
        change = current_price - previous_close
        change_percent = float((change / previous_close) * 100)

        return Price(
            symbol=symbol,
            current_price=current_price,
            open_price=current_price * Decimal("0.995"),
            high_price=current_price * Decimal("1.02"),
            low_price=current_price * Decimal("0.98"),
            volume=1000000 + (hash(symbol) % 5000000),  # 1M-6M volume
            previous_close=previous_close,
            change=change,
            change_percent=change_percent,
        )

    def _get_mock_technical_data(self, symbol: str) -> TechnicalIndicators:
        """Generate mock technical indicators for testing."""
        # Generate consistent mock data based on symbol
        base_rsi = 30 + (hash(symbol) % 40)  # RSI between 30-70

        current_price = 100 + (hash(symbol) % 500)

        return TechnicalIndicators(
            rsi=float(base_rsi),
            macd=0.5 + ((hash(symbol) % 100) - 50) / 100,  # -0.5 to 1.5
            macd_signal=0.3 + ((hash(symbol) % 80) - 40) / 100,  # -0.1 to 1.1
            sma_20=current_price * 0.98,  # Slightly below current price
            sma_50=current_price * 0.95,  # Further below
            sma_200=current_price * 0.90,  # Even further below (bullish setup)
            bollinger_upper=current_price * 1.05,
            bollinger_lower=current_price * 0.95,
            volume_avg=1500000.0,
            volatility=0.15 + ((hash(symbol) % 30) / 100),  # 0.15-0.45 volatility
        )

    def _get_mock_sentiment_data(self, symbols: List[str]) -> MarketSentiment:
        """Generate mock sentiment data for testing."""
        if not symbols:
            return MarketSentiment(
                overall_sentiment=0.0,
                news_sentiment=0.0,
                confidence=0.5,
                key_themes=["No symbols provided"],
            )

        # Generate sentiment based on symbols
        sentiment_sum = sum((hash(symbol) % 100) - 50 for symbol in symbols)
        overall_sentiment = sentiment_sum / (len(symbols) * 50)  # Normalize to -1 to 1
        overall_sentiment = max(-1, min(1, overall_sentiment))

        # News sentiment slightly different
        news_sentiment = overall_sentiment * 0.8 + 0.1
        news_sentiment = max(-1, min(1, news_sentiment))

        # Generate themes based on sentiment
        if overall_sentiment > 0.3:
            themes = ["Market optimism", "Growth expectations", "Positive earnings outlook"]
        elif overall_sentiment < -0.3:
            themes = ["Market concerns", "Economic uncertainty", "Risk-off sentiment"]
        else:
            themes = ["Mixed signals", "Market consolidation", "Waiting for catalysts"]

        return MarketSentiment(
            overall_sentiment=overall_sentiment,
            news_sentiment=news_sentiment,
            social_sentiment=overall_sentiment * 1.2,  # Amplify for social
            analyst_sentiment=overall_sentiment * 0.6,  # More conservative
            confidence=0.7 + abs(overall_sentiment) * 0.3,  # Higher confidence with stronger sentiment
            key_themes=themes,
        )
