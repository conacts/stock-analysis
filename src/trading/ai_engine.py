"""
AI Trading Engine

Uses DeepSeek AI to analyze portfolios, generate trading signals,
and provide intelligent trading recommendations with risk assessment.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from src.llm.deepseek_client import DeepSeekClient
from src.models.trading_models import (
    MarketCondition,
    OrderType,
    SignalType,
    TechnicalIndicators,
    TradeAction,
    TradeRecommendation,
    TradingAnalysis,
    TradingSignal,
)
from src.services.portfolio_service import PortfolioService
from src.trading.market_data import MarketDataProvider
from src.trading.risk_manager import RiskManager

logger = logging.getLogger(__name__)


class AITradingEngine:
    """
    AI-powered trading engine that uses DeepSeek for analysis and decision making.

    This engine combines:
    - Real-time market data
    - Technical analysis
    - Fundamental analysis
    - Sentiment analysis
    - Risk assessment
    - AI-powered decision making
    """

    def __init__(
        self,
        deepseek_client: DeepSeekClient,
        market_data_provider: MarketDataProvider,
        portfolio_service: PortfolioService,
        risk_manager: RiskManager,
    ):
        self.deepseek = deepseek_client
        self.market_data = market_data_provider
        self.portfolio_service = portfolio_service
        self.risk_manager = risk_manager

        # Configuration
        self.max_signals_per_analysis = 10
        self.signal_confidence_threshold = 0.6
        self.max_position_size_pct = 0.10  # 10% max position size

    async def analyze_portfolio(self, portfolio_id: int) -> TradingAnalysis:
        """
        Perform comprehensive AI-powered portfolio analysis.

        Args:
            portfolio_id: Portfolio to analyze

        Returns:
            TradingAnalysis with AI insights and recommendations
        """
        logger.info(f"Starting AI analysis for portfolio {portfolio_id}")

        try:
            # Get portfolio data
            portfolio = await self.portfolio_service.get_portfolio(portfolio_id)
            if not portfolio:
                raise ValueError(f"Portfolio {portfolio_id} not found")

            # Get current positions
            positions = await self.portfolio_service.get_positions(portfolio_id)

            # Get market data for all positions
            symbols = [pos.symbol for pos in positions] if positions else []
            market_data = {}
            technical_data = {}

            if symbols:
                # Fetch market data in parallel
                market_tasks = [self.market_data.get_real_time_price(symbol) for symbol in symbols]
                technical_tasks = [self.market_data.get_technical_indicators(symbol) for symbol in symbols]

                market_results = await asyncio.gather(*market_tasks, return_exceptions=True)
                technical_results = await asyncio.gather(*technical_tasks, return_exceptions=True)

                for i, symbol in enumerate(symbols):
                    if not isinstance(market_results[i], Exception):
                        market_data[symbol] = market_results[i]
                    if not isinstance(technical_results[i], Exception):
                        technical_data[symbol] = technical_results[i]

            # Get market sentiment
            market_sentiment = await self.market_data.get_market_sentiment(symbols[:5])  # Top 5 positions

            # Assess market condition
            market_condition = await self._assess_market_condition(market_data, technical_data)

            # Calculate portfolio metrics
            portfolio_value = sum(pos.current_value for pos in positions) if positions else Decimal("0")
            cash_available = portfolio.cash_balance if hasattr(portfolio, "cash_balance") else Decimal("100000")  # Default

            # Perform risk assessment
            risk_assessment = await self.risk_manager.assess_portfolio_risk(portfolio_id, positions, market_data)

            # Generate AI analysis
            ai_analysis = await self._generate_ai_analysis(portfolio, positions, market_data, technical_data, market_sentiment, market_condition)

            # Create comprehensive analysis
            analysis = TradingAnalysis(
                portfolio_id=portfolio_id,
                market_condition=market_condition,
                market_sentiment=market_sentiment,
                current_positions=[pos.dict() for pos in positions] if positions else [],
                portfolio_value=portfolio_value,
                cash_available=cash_available,
                risk_assessment=risk_assessment,
                ai_summary=ai_analysis["summary"],
                key_opportunities=ai_analysis["opportunities"],
                key_risks=ai_analysis["risks"],
                recommended_actions=ai_analysis["actions"],
                portfolio_adjustments=ai_analysis["adjustments"],
            )

            logger.info(f"Completed AI analysis for portfolio {portfolio_id}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing portfolio {portfolio_id}: {e}")
            raise

    async def generate_signals(self, analysis: TradingAnalysis) -> List[TradingSignal]:
        """
        Generate AI-powered trading signals based on portfolio analysis.

        Args:
            analysis: Portfolio analysis results

        Returns:
            List of trading signals with confidence scores
        """
        logger.info(f"Generating trading signals for portfolio {analysis.portfolio_id}")

        try:
            # Get symbols to analyze (current positions + potential new positions)
            current_symbols = [pos["symbol"] for pos in analysis.current_positions]

            # Add potential new positions based on market screening
            potential_symbols = await self._screen_market_opportunities(analysis)
            all_symbols = list(set(current_symbols + potential_symbols))

            # Generate signals for each symbol
            signals = []
            for symbol in all_symbols[: self.max_signals_per_analysis]:
                try:
                    signal = await self._generate_signal_for_symbol(symbol, analysis)
                    if signal and signal.confidence >= self.signal_confidence_threshold:
                        signals.append(signal)
                except Exception as e:
                    logger.warning(f"Error generating signal for {symbol}: {e}")
                    continue

            # Sort by confidence and return top signals
            signals.sort(key=lambda x: x.confidence, reverse=True)

            logger.info(f"Generated {len(signals)} trading signals for portfolio {analysis.portfolio_id}")
            return signals

        except Exception as e:
            logger.error(f"Error generating signals for portfolio {analysis.portfolio_id}: {e}")
            raise

    async def recommend_trades(self, signals: List[TradingSignal]) -> List[TradeRecommendation]:
        """
        Convert trading signals into specific trade recommendations.

        Args:
            signals: List of trading signals

        Returns:
            List of trade recommendations with position sizing and risk management
        """
        logger.info(f"Converting {len(signals)} signals to trade recommendations")

        try:
            recommendations = []

            for signal in signals:
                try:
                    recommendation = await self._create_trade_recommendation(signal)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    logger.warning(f"Error creating recommendation for signal {signal.id}: {e}")
                    continue

            # Validate and adjust recommendations for portfolio constraints
            validated_recommendations = await self._validate_recommendations(recommendations)

            logger.info(f"Created {len(validated_recommendations)} trade recommendations")
            return validated_recommendations

        except Exception as e:
            logger.error(f"Error creating trade recommendations: {e}")
            raise

    async def _assess_market_condition(self, market_data: Dict, technical_data: Dict) -> MarketCondition:
        """Assess overall market condition based on available data."""
        try:
            if not market_data:
                return MarketCondition.NEUTRAL

            # Simple market condition assessment
            # In production, this would be more sophisticated
            total_change = sum(price.change_percent for price in market_data.values()) / len(market_data)

            volatility = sum(tech.volatility or 0 for tech in technical_data.values()) / len(technical_data) if technical_data else 0

            if volatility > 0.3:  # High volatility threshold
                return MarketCondition.VOLATILE
            elif total_change > 2:
                return MarketCondition.BULLISH
            elif total_change < -2:
                return MarketCondition.BEARISH
            else:
                return MarketCondition.NEUTRAL

        except Exception:
            return MarketCondition.NEUTRAL

    async def _generate_ai_analysis(self, portfolio, positions, market_data, technical_data, market_sentiment, market_condition) -> Dict:
        """Generate AI-powered analysis using DeepSeek."""

        # Prepare context for AI analysis
        context = {
            "portfolio_id": portfolio.id if hasattr(portfolio, "id") else 1,
            "portfolio_type": getattr(portfolio, "portfolio_type", "Growth"),
            "positions": len(positions) if positions else 0,
            "market_condition": market_condition.value,
            "market_sentiment": market_sentiment.overall_sentiment,
            "current_positions": [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "current_value": float(pos.current_value),
                    "unrealized_pnl": float(pos.unrealized_pnl) if hasattr(pos, "unrealized_pnl") else 0,
                }
                for pos in positions
            ]
            if positions
            else [],
        }

        prompt = f"""
        As an expert AI trading analyst, analyze this portfolio and provide comprehensive insights:

        Portfolio Context:
        - Portfolio ID: {context['portfolio_id']}
        - Portfolio Type: {context['portfolio_type']}
        - Number of Positions: {context['positions']}
        - Market Condition: {context['market_condition']}
        - Market Sentiment: {context['market_sentiment']:.2f} (-1 to 1 scale)

        Current Positions:
        {self._format_positions_for_ai(context['current_positions'])}

        Please provide:
        1. A comprehensive summary of the portfolio's current state
        2. Key opportunities you identify for improvement or growth
        3. Key risks that need attention
        4. Specific recommended actions for the next trading session
        5. Portfolio adjustments to consider

        Focus on actionable insights that can improve risk-adjusted returns.
        Consider market conditions, position sizing, diversification, and risk management.
        """

        try:
            response = await self.deepseek.generate_response(prompt)

            # Parse AI response (simplified - in production would use more sophisticated parsing)
            return {
                "summary": response[:500] + "..." if len(response) > 500 else response,
                "opportunities": [
                    "Identify undervalued growth stocks in current market conditions",
                    "Consider sector rotation based on market sentiment",
                    "Optimize position sizing for better risk-adjusted returns",
                ],
                "risks": [
                    "Monitor portfolio concentration risk",
                    "Watch for market volatility increases",
                    "Consider defensive positioning if sentiment deteriorates",
                ],
                "actions": [
                    "Review and rebalance overweight positions",
                    "Consider taking profits on strong performers",
                    "Add defensive positions if market conditions warrant",
                ],
                "adjustments": [
                    "Reduce position sizes in high-volatility stocks",
                    "Increase cash allocation for opportunities",
                    "Consider adding dividend-paying stocks for stability",
                ],
            }

        except Exception as e:
            logger.warning(f"Error generating AI analysis: {e}")
            # Return default analysis
            return {
                "summary": "Portfolio analysis completed. Market conditions are being monitored.",
                "opportunities": ["Monitor market for entry opportunities"],
                "risks": ["General market risk"],
                "actions": ["Continue monitoring positions"],
                "adjustments": ["Maintain current allocation"],
            }

    def _format_positions_for_ai(self, positions: List[Dict]) -> str:
        """Format positions data for AI analysis."""
        if not positions:
            return "No current positions"

        formatted = []
        for pos in positions:
            formatted.append(f"- {pos['symbol']}: {pos['quantity']} shares, " f"Value: ${pos['current_value']:,.2f}, " f"P&L: ${pos['unrealized_pnl']:,.2f}")

        return "\n".join(formatted)

    async def _screen_market_opportunities(self, analysis: TradingAnalysis) -> List[str]:
        """Screen market for potential new investment opportunities."""
        # Simplified screening - in production would use more sophisticated screening
        # Based on market condition and portfolio type

        if analysis.market_condition == MarketCondition.BULLISH:
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Growth stocks
        elif analysis.market_condition == MarketCondition.BEARISH:
            return ["JNJ", "PG", "KO", "WMT", "VZ"]  # Defensive stocks
        else:
            return ["SPY", "QQQ", "VTI"]  # Index ETFs

    async def _generate_signal_for_symbol(self, symbol: str, analysis: TradingAnalysis) -> Optional[TradingSignal]:
        """Generate a trading signal for a specific symbol."""
        try:
            # Get market data
            price_data = await self.market_data.get_real_time_price(symbol)
            technical_data = await self.market_data.get_technical_indicators(symbol)
            sentiment_data = await self.market_data.get_market_sentiment([symbol])

            # Calculate scores
            technical_score = self._calculate_technical_score(technical_data)
            fundamental_score = 0.7  # Placeholder - would calculate from fundamental data
            sentiment_score = (sentiment_data.overall_sentiment + 1) / 2  # Convert -1,1 to 0,1

            # Overall confidence
            confidence = (technical_score + fundamental_score + sentiment_score) / 3

            # Determine signal type
            if confidence > 0.7:
                signal_type = SignalType.BUY
            elif confidence < 0.3:
                signal_type = SignalType.SELL
            else:
                signal_type = SignalType.HOLD

            # Generate AI reasoning
            reasoning = await self._generate_signal_reasoning(symbol, price_data, technical_data, sentiment_data, signal_type, confidence)

            return TradingSignal(
                portfolio_id=analysis.portfolio_id,
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                reasoning=reasoning,
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                sentiment_score=sentiment_score,
                current_price=price_data.current_price,
                target_price=price_data.current_price * Decimal("1.1") if signal_type == SignalType.BUY else None,
                stop_loss=price_data.current_price * Decimal("0.95") if signal_type == SignalType.BUY else None,
                expires_at=datetime.now() + timedelta(hours=24),
            )

        except Exception as e:
            logger.warning(f"Error generating signal for {symbol}: {e}")
            return None

    def _calculate_technical_score(self, technical_data: TechnicalIndicators) -> float:
        """Calculate technical analysis score from indicators."""
        score = 0.5  # Neutral starting point

        try:
            # RSI analysis
            if technical_data.rsi is not None:
                if technical_data.rsi < 30:  # Oversold
                    score += 0.2
                elif technical_data.rsi > 70:  # Overbought
                    score -= 0.2

            # Moving average analysis
            if technical_data.sma_20 and technical_data.sma_50 and technical_data.sma_20 > technical_data.sma_50:
                score += 0.1  # Bullish crossover

            # MACD analysis
            if technical_data.macd and technical_data.macd_signal and technical_data.macd > technical_data.macd_signal:
                score += 0.1  # Bullish MACD

            # Volatility consideration
            if technical_data.volatility and technical_data.volatility > 0.3:
                score -= 0.1  # High volatility penalty

        except Exception as e:
            logger.warning(f"Error calculating technical score: {e}")

        return max(0, min(1, score))  # Clamp to 0-1 range

    async def _generate_signal_reasoning(self, symbol, price_data, technical_data, sentiment_data, signal_type, confidence) -> str:
        """Generate AI reasoning for the trading signal."""

        prompt = f"""
        Provide a concise trading signal reasoning for {symbol}:

        Signal: {signal_type.value}
        Confidence: {confidence:.2f}
        Current Price: ${price_data.current_price}
        Price Change: {price_data.change_percent:.2f}%
        RSI: {technical_data.rsi or 'N/A'}
        Market Sentiment: {sentiment_data.overall_sentiment:.2f}

        Explain in 2-3 sentences why this signal was generated.
        """

        try:
            reasoning = await self.deepseek.generate_response(prompt)
            return reasoning[:200] + "..." if len(reasoning) > 200 else reasoning
        except Exception:
            return f"{signal_type.value} signal for {symbol} based on technical and sentiment analysis."

    async def _create_trade_recommendation(self, signal: TradingSignal) -> Optional[TradeRecommendation]:
        """Create a trade recommendation from a trading signal."""
        try:
            if signal.signal_type == SignalType.HOLD:
                return None  # No trade recommendation for HOLD signals

            # Determine trade action
            action = TradeAction.BUY if signal.signal_type == SignalType.BUY else TradeAction.SELL

            # Calculate position size (simplified)
            position_size_pct = min(self.max_position_size_pct, signal.confidence * 0.15)  # Max 15% based on confidence

            # Estimate portfolio value (would get from database in production)
            estimated_portfolio_value = Decimal("100000")  # $100k default
            position_value = estimated_portfolio_value * Decimal(str(position_size_pct))
            quantity = int(position_value / signal.current_price)

            if quantity <= 0:
                return None

            # Risk assessment
            risk_score = 1 - signal.confidence  # Higher confidence = lower risk
            expected_return = (signal.confidence - 0.5) * 20  # -10% to +10% based on confidence

            return TradeRecommendation(
                signal_id=signal.id or 0,
                portfolio_id=signal.portfolio_id,
                symbol=signal.symbol,
                action=action,
                quantity=quantity,
                order_type=OrderType.MARKET,  # Default to market orders
                reasoning=f"AI recommendation based on {signal.reasoning}",
                risk_score=risk_score,
                expected_return=expected_return,
                position_size_pct=position_size_pct,
                max_loss_pct=5.0,  # 5% max loss
                holding_period=30,  # 30 days expected holding
                expires_at=datetime.now() + timedelta(hours=4),  # 4 hour expiry
            )

        except Exception as e:
            logger.warning(f"Error creating trade recommendation for signal {signal.id}: {e}")
            return None

    async def _validate_recommendations(self, recommendations: List[TradeRecommendation]) -> List[TradeRecommendation]:
        """Validate and adjust recommendations for portfolio constraints."""
        validated = []

        total_position_size = 0
        for rec in recommendations:
            # Check if adding this position would exceed portfolio limits
            if total_position_size + rec.position_size_pct <= 0.8:  # Max 80% invested
                validated.append(rec)
                total_position_size += rec.position_size_pct
            else:
                # Adjust position size to fit within limits
                remaining_capacity = 0.8 - total_position_size
                if remaining_capacity > 0.02:  # Minimum 2% position
                    rec.position_size_pct = remaining_capacity
                    rec.quantity = int((Decimal("100000") * Decimal(str(remaining_capacity))) / (rec.limit_price or Decimal("100")))
                    validated.append(rec)
                    break  # No more positions can be added

        return validated
