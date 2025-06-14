"""
Portfolio Analyzer

Analyzes portfolio positions to generate sell signals, rebalancing recommendations,
and portfolio-aware buy signals.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.analyzer import StockAnalyzer
from ..db.models import PortfolioPosition
from .portfolio_manager import PortfolioManager


class PortfolioAnalyzer:
    """
    Analyzes portfolio positions and generates actionable recommendations

    Features:
    - Sell signal generation for existing positions
    - Position sizing recommendations for new buys
    - Portfolio rebalancing suggestions
    - Risk management alerts
    """

    def __init__(self, portfolio_manager: PortfolioManager, stock_analyzer: StockAnalyzer):
        """Initialize portfolio analyzer"""
        self.portfolio_manager = portfolio_manager
        self.stock_analyzer = stock_analyzer
        self.logger = logging.getLogger(__name__)

    def analyze_portfolio_for_sells(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        Analyze all positions in portfolio for sell opportunities

        Args:
            portfolio_id: Portfolio to analyze

        Returns:
            List of sell recommendations with details
        """
        try:
            positions = self.portfolio_manager.get_portfolio_positions(portfolio_id)
            sell_recommendations = []

            for position in positions:
                sell_analysis = self._analyze_position_for_sell(position)
                if sell_analysis:
                    sell_recommendations.append(sell_analysis)

            # Sort by urgency/strength of sell signal
            sell_recommendations.sort(key=lambda x: x.get("sell_score", 0), reverse=True)

            self.logger.info(f"Generated {len(sell_recommendations)} sell recommendations for portfolio {portfolio_id}")
            return sell_recommendations

        except Exception as e:
            self.logger.error(f"Failed to analyze portfolio for sells: {e}")
            return []

    def _analyze_position_for_sell(self, position: PortfolioPosition) -> Optional[Dict[str, Any]]:
        """
        Analyze individual position for sell signals

        Args:
            position: Portfolio position to analyze

        Returns:
            Sell recommendation dict or None
        """
        try:
            # Get fresh analysis for the stock
            analysis = self.stock_analyzer.analyze_stock(position.symbol)
            if not analysis:
                return None

            recommendation = analysis.get("recommendation", {})
            rating = recommendation.get("rating", "Hold")
            score = analysis.get("score", {}).get("composite_score", 50)
            confidence = recommendation.get("confidence", "Low")

            # Determine sell signals
            sell_signals = []
            sell_score = 0

            # 1. Rating-based sell signals
            if rating in ["Strong Sell", "Sell"]:
                sell_signals.append(f"Analyst rating downgraded to {rating}")
                sell_score += 40
            elif rating == "Hold" and score < 40:
                sell_signals.append(f"Weak Hold rating with low score ({score:.1f})")
                sell_score += 20

            # 2. Performance-based sell signals
            unrealized_pnl_pct = float(position.unrealized_pnl_pct)
            if unrealized_pnl_pct < -20:  # Down more than 20%
                sell_signals.append(f"Position down {unrealized_pnl_pct:.1f}% from cost basis")
                sell_score += 25
            elif unrealized_pnl_pct > 50:  # Up more than 50% - consider taking profits
                sell_signals.append(f"Strong gains ({unrealized_pnl_pct:.1f}%) - consider profit taking")
                sell_score += 15

            # 3. Technical sell signals
            technical = analysis.get("technical", {})
            if technical.get("trend") == "bearish":
                sell_signals.append("Technical trend turned bearish")
                sell_score += 15

            # 4. Risk-based sell signals
            portfolio_summary = self.portfolio_manager.get_portfolio_summary(position.portfolio_id)
            total_value = portfolio_summary.get("total_value", 0)

            if total_value > 0:
                # Convert to float for calculation
                market_value = float(position.market_value)
                position_allocation = (market_value / total_value) * 100
                if position_allocation > 15:  # Over-concentrated position
                    sell_signals.append(f"Over-concentrated position ({position_allocation:.1f}% of portfolio)")
                    sell_score += 10

            # Only return recommendation if there are meaningful sell signals
            if sell_score >= 20:  # Minimum threshold for sell recommendation
                # Calculate suggested sell quantity
                suggested_quantity = self._calculate_sell_quantity(position, sell_score, sell_signals)

                return {
                    "symbol": position.symbol,
                    "current_position": {"quantity": position.quantity, "average_cost": position.average_cost, "current_price": position.current_price, "market_value": position.market_value, "unrealized_pnl": position.unrealized_pnl, "unrealized_pnl_pct": position.unrealized_pnl_pct},
                    "sell_recommendation": {"rating": rating, "score": score, "confidence": confidence, "sell_score": sell_score, "sell_signals": sell_signals, "suggested_quantity": suggested_quantity, "suggested_action": self._get_sell_action(sell_score)},
                    "analysis_date": datetime.now().isoformat(),
                }

            return None

        except Exception as e:
            self.logger.error(f"Failed to analyze position {position.symbol} for sell: {e}")
            return None

    def _calculate_sell_quantity(self, position: PortfolioPosition, sell_score: int, sell_signals: List[str]) -> float:
        """Calculate suggested quantity to sell based on sell signals"""

        # Base sell percentage based on sell score
        if sell_score >= 60:  # Strong sell
            base_pct = 0.75  # Sell 75%
        elif sell_score >= 40:  # Moderate sell
            base_pct = 0.50  # Sell 50%
        else:  # Weak sell
            base_pct = 0.25  # Sell 25%

        # Adjust based on specific signals
        for signal in sell_signals:
            if "Strong Sell" in signal:
                base_pct = min(1.0, base_pct + 0.25)
            elif "down" in signal and "20%" in signal:
                base_pct = min(1.0, base_pct + 0.15)  # Stop loss
            elif "profit taking" in signal:
                base_pct = min(0.5, base_pct)  # Don't sell everything on profit taking

        return round(float(position.quantity) * base_pct, 2)

    def _get_sell_action(self, sell_score: int) -> str:
        """Get recommended action based on sell score"""
        if sell_score >= 60:
            return "STRONG_SELL"
        elif sell_score >= 40:
            return "SELL"
        else:
            return "TRIM_POSITION"

    def check_buy_against_portfolio(self, portfolio_id: int, symbol: str, suggested_allocation: float) -> Dict[str, Any]:
        """
        Check if a buy recommendation makes sense given current portfolio

        Args:
            portfolio_id: Portfolio to check against
            symbol: Stock symbol to potentially buy
            suggested_allocation: Suggested allocation percentage

        Returns:
            Portfolio-aware buy recommendation
        """
        try:
            # Get current position if exists
            existing_position = self.portfolio_manager.get_position(portfolio_id, symbol)
            portfolio_summary = self.portfolio_manager.get_portfolio_summary(portfolio_id)

            total_value = portfolio_summary.get("total_value", 0)
            current_allocation = 0.0

            if existing_position and total_value > 0:
                current_allocation = (float(existing_position.market_value) / total_value) * 100

            # Check for over-concentration
            max_single_position = 20.0  # Max 20% in single stock
            available_allocation = max_single_position - current_allocation

            # Adjust suggested allocation
            final_allocation = min(suggested_allocation, available_allocation)

            recommendation = {"symbol": symbol, "current_allocation": current_allocation, "suggested_allocation": suggested_allocation, "final_allocation": final_allocation, "existing_position": existing_position is not None, "action": "BUY" if final_allocation > 0 else "SKIP", "reason": ""}

            # Determine reason
            if final_allocation <= 0:
                recommendation["reason"] = f"Already at max allocation ({current_allocation:.1f}%)"
                recommendation["action"] = "SKIP"
            elif current_allocation > 0:
                recommendation["reason"] = f"Adding to existing position ({current_allocation:.1f}% → {current_allocation + final_allocation:.1f}%)"
                recommendation["action"] = "ADD"
            else:
                recommendation["reason"] = f"New position ({final_allocation:.1f}% allocation)"
                recommendation["action"] = "BUY"

            return recommendation

        except Exception as e:
            self.logger.error(f"Failed to check buy against portfolio: {e}")
            return {"action": "ERROR", "reason": str(e)}

    def generate_rebalancing_recommendations(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        Generate portfolio rebalancing recommendations

        Args:
            portfolio_id: Portfolio to analyze

        Returns:
            List of rebalancing recommendations
        """
        try:
            positions = self.portfolio_manager.get_portfolio_positions(portfolio_id)
            portfolio_summary = self.portfolio_manager.get_portfolio_summary(portfolio_id)

            if not positions or portfolio_summary.get("total_value", 0) == 0:
                return []

            total_value = portfolio_summary["total_value"]
            recommendations = []

            # Check for over-concentrated positions
            for position in positions:
                allocation_pct = (float(position.market_value) / total_value) * 100

                if allocation_pct > 20:  # Over 20% in single stock
                    trim_amount = float(position.market_value) - (total_value * 0.15)  # Trim to 15%
                    trim_shares = trim_amount / float(position.current_price)

                    recommendations.append({"type": "TRIM_OVERWEIGHT", "symbol": position.symbol, "current_allocation": allocation_pct, "target_allocation": 15.0, "action": f"Trim {trim_shares:.0f} shares to reduce concentration", "priority": "HIGH" if allocation_pct > 25 else "MEDIUM"})

            # Check sector concentration
            sector_allocation = portfolio_summary.get("sector_allocation", {})
            for sector, allocation in sector_allocation.items():
                if allocation > 40:  # Over 40% in single sector
                    recommendations.append({"type": "SECTOR_REBALANCE", "sector": sector, "current_allocation": allocation, "target_allocation": 35.0, "action": f"Reduce {sector} exposure from {allocation:.1f}% to ~35%", "priority": "MEDIUM"})

            return recommendations

        except Exception as e:
            self.logger.error(f"Failed to generate rebalancing recommendations: {e}")
            return []

    def get_portfolio_health_score(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Calculate overall portfolio health score

        Args:
            portfolio_id: Portfolio to analyze

        Returns:
            Portfolio health metrics and score
        """
        try:
            positions = self.portfolio_manager.get_portfolio_positions(portfolio_id)
            portfolio_summary = self.portfolio_manager.get_portfolio_summary(portfolio_id)

            if not positions:
                return {"health_score": 0, "status": "EMPTY", "issues": ["No positions in portfolio"]}

            health_score = 100
            issues = []

            # Check diversification
            if len(positions) < 5:
                health_score -= 15
                issues.append(f"Under-diversified: Only {len(positions)} positions")

            # Check concentration risk
            total_value = portfolio_summary.get("total_value", 0)
            if total_value > 0:
                max_allocation = max((float(pos.market_value) / total_value * 100) for pos in positions)
                if max_allocation > 25:
                    health_score -= 20
                    issues.append(f"Over-concentrated: {max_allocation:.1f}% in single stock")
                elif max_allocation > 20:
                    health_score -= 10
                    issues.append(f"High concentration: {max_allocation:.1f}% in single stock")

            # Check sector diversification
            sector_allocation = portfolio_summary.get("sector_allocation", {})
            if sector_allocation:
                max_sector = max(sector_allocation.values())
                if max_sector > 50:
                    health_score -= 15
                    issues.append(f"Sector over-concentration: {max_sector:.1f}% in single sector")

            # Check performance
            avg_performance = sum(float(pos.unrealized_pnl_pct) for pos in positions) / len(positions)
            if avg_performance < -15:
                health_score -= 20
                issues.append(f"Poor performance: Average {avg_performance:.1f}% unrealized loss")
            elif avg_performance < -5:
                health_score -= 10
                issues.append(f"Underperforming: Average {avg_performance:.1f}% unrealized loss")

            # Determine status
            if health_score >= 80:
                status = "EXCELLENT"
            elif health_score >= 60:
                status = "GOOD"
            elif health_score >= 40:
                status = "FAIR"
            else:
                status = "POOR"

            return {"health_score": max(0, health_score), "status": status, "issues": issues, "total_positions": len(positions), "total_value": total_value, "avg_performance": avg_performance}

        except Exception as e:
            self.logger.error(f"Failed to calculate portfolio health score: {e}")
            return {"health_score": 0, "status": "ERROR", "issues": [str(e)]}
