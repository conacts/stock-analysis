"""
Risk Manager

Comprehensive risk management system for AI trading including position limits,
portfolio risk assessment, and trade validation.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from src.models.trading_models import (
    RiskAssessment,
    RiskLevel,
    RiskStatus,
    TradeRecommendation,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Comprehensive risk management system for AI trading.

    Features:
    - Portfolio risk assessment
    - Position size limits
    - Daily loss limits
    - Trade validation
    - Emergency stop mechanisms
    """

    def __init__(self):
        # Risk configuration
        self.max_position_size_pct = 0.10  # 10% max position size
        self.max_portfolio_risk_pct = 0.80  # 80% max invested
        self.daily_loss_limit_pct = 0.02  # 2% daily loss limit
        self.max_drawdown_pct = 0.05  # 5% max drawdown from peak
        self.min_cash_reserve_pct = 0.20  # 20% minimum cash reserve

        # Volatility thresholds
        self.high_volatility_threshold = 0.30
        self.extreme_volatility_threshold = 0.50

        # Risk tracking
        self._daily_pnl_tracking = {}
        self._portfolio_peaks = {}
        self._risk_flags = {}

    async def assess_portfolio_risk(self, portfolio_id: int, positions: List, market_data: Dict) -> RiskAssessment:
        """
        Perform comprehensive portfolio risk assessment.

        Args:
            portfolio_id: Portfolio to assess
            positions: Current portfolio positions
            market_data: Current market data

        Returns:
            RiskAssessment with detailed risk analysis
        """
        logger.info(f"Assessing risk for portfolio {portfolio_id}")

        try:
            # Calculate portfolio metrics
            total_value = sum(pos.current_value for pos in positions) if positions else Decimal("0")

            # Position concentration risk
            concentration_risk = self._calculate_concentration_risk(positions, total_value)

            # Market risk assessment
            market_risk = self._calculate_market_risk(positions, market_data)

            # Volatility risk
            volatility_risk = self._calculate_volatility_risk(positions, market_data)

            # Liquidity risk
            liquidity_risk = self._calculate_liquidity_risk(positions, market_data)

            # Overall risk score (weighted average)
            risk_score = concentration_risk * 0.3 + market_risk * 0.25 + volatility_risk * 0.25 + liquidity_risk * 0.20

            # Determine risk level
            overall_risk = self._determine_risk_level(risk_score)

            # Generate risk warnings and mitigation strategies
            risk_warnings = self._generate_risk_warnings(concentration_risk, market_risk, volatility_risk, liquidity_risk)
            risk_mitigation = self._generate_risk_mitigation(concentration_risk, market_risk, volatility_risk, liquidity_risk)

            # Calculate portfolio beta (simplified)
            portfolio_beta = self._calculate_portfolio_beta(positions, market_data)

            # Calculate Value at Risk (simplified)
            var_1day = self._calculate_var_1day(positions, market_data)

            # Calculate max drawdown
            max_drawdown = self._calculate_max_drawdown(portfolio_id, total_value)

            return RiskAssessment(
                overall_risk=overall_risk,
                risk_score=risk_score,
                position_concentration_risk=concentration_risk,
                market_risk=market_risk,
                volatility_risk=volatility_risk,
                liquidity_risk=liquidity_risk,
                portfolio_beta=portfolio_beta,
                var_1day=var_1day,
                max_drawdown=max_drawdown,
                daily_loss_limit=float(total_value) * self.daily_loss_limit_pct,
                position_limit=float(total_value) * self.max_position_size_pct,
                risk_warnings=risk_warnings,
                risk_mitigation=risk_mitigation,
            )

        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {e}")
            # Return conservative risk assessment
            return RiskAssessment(
                overall_risk=RiskLevel.HIGH,
                risk_score=0.8,
                position_concentration_risk=0.8,
                market_risk=0.7,
                volatility_risk=0.7,
                liquidity_risk=0.6,
                daily_loss_limit=2000.0,  # $2000 default
                position_limit=10000.0,  # $10000 default
                risk_warnings=["Unable to assess risk properly"],
                risk_mitigation=["Manual review required"],
            )

    async def validate_trade(self, trade: TradeRecommendation) -> ValidationResult:
        """
        Validate a trade recommendation against risk parameters.

        Args:
            trade: Trade recommendation to validate

        Returns:
            ValidationResult with validation status and suggestions
        """
        logger.info(f"Validating trade: {trade.symbol} {trade.action} {trade.quantity}")

        errors = []
        warnings = []
        suggested_adjustments = []

        try:
            # Position size check
            position_limit_check = self._check_position_limits(trade)
            if not position_limit_check:
                errors.append(f"Position size {trade.position_size_pct:.1%} exceeds limit {self.max_position_size_pct:.1%}")
                suggested_adjustments.append(f"Reduce position size to {self.max_position_size_pct:.1%}")

            # Risk score check
            risk_check_passed = trade.risk_score <= 0.7  # Max 70% risk score
            if not risk_check_passed:
                warnings.append(f"High risk score: {trade.risk_score:.2f}")
                suggested_adjustments.append("Consider reducing position size due to high risk")

            # Cash availability check (simplified)
            estimated_cost = trade.quantity * (trade.limit_price or Decimal("100"))
            cash_check_passed = estimated_cost <= Decimal("50000")  # Assume $50k available
            if not cash_check_passed:
                errors.append("Insufficient cash for trade")
                suggested_adjustments.append("Reduce quantity or wait for cash availability")

            # Market hours check (simplified)
            market_hours_check = self._is_market_open()
            if not market_hours_check:
                warnings.append("Market is closed - order will be queued")

            # Overall validation
            is_valid = len(errors) == 0
            validation_score = 1.0 - (len(errors) * 0.3 + len(warnings) * 0.1)
            validation_score = max(0, min(1, validation_score))

            return ValidationResult(
                is_valid=is_valid,
                validation_score=validation_score,
                risk_check_passed=risk_check_passed,
                position_limit_check=position_limit_check,
                cash_check_passed=cash_check_passed,
                market_hours_check=market_hours_check,
                errors=errors,
                warnings=warnings,
                suggested_adjustments=suggested_adjustments,
            )

        except Exception as e:
            logger.error(f"Error validating trade: {e}")
            return ValidationResult(
                is_valid=False,
                validation_score=0.0,
                risk_check_passed=False,
                position_limit_check=False,
                cash_check_passed=False,
                market_hours_check=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                suggested_adjustments=["Manual review required"],
            )

    async def get_risk_status(self, portfolio_id: int) -> RiskStatus:
        """
        Get current risk status for a portfolio.

        Args:
            portfolio_id: Portfolio to check

        Returns:
            RiskStatus with current risk metrics
        """
        try:
            # Get daily P&L (simplified)
            daily_pnl = self._daily_pnl_tracking.get(portfolio_id, Decimal("0"))
            portfolio_value = Decimal("100000")  # Default portfolio value
            daily_pnl_pct = float(daily_pnl / portfolio_value) * 100

            # Calculate remaining daily loss budget
            daily_loss_limit = portfolio_value * Decimal(str(self.daily_loss_limit_pct))
            daily_loss_remaining = daily_loss_limit + daily_pnl  # Add because daily_pnl is negative for losses

            # Risk flags
            risk_flags = []
            if daily_pnl_pct < -self.daily_loss_limit_pct * 100:
                risk_flags.append("Daily loss limit exceeded")

            if daily_loss_remaining < Decimal("0"):
                risk_flags.append("No remaining loss budget")

            # Determine overall risk level
            if len(risk_flags) > 0:
                overall_risk = RiskLevel.HIGH
                risk_score = 0.8
            else:
                overall_risk = RiskLevel.MEDIUM
                risk_score = 0.5

            # Check if trading should be halted
            trading_halted = len([flag for flag in risk_flags if "limit exceeded" in flag]) > 0

            return RiskStatus(
                portfolio_id=portfolio_id,
                overall_risk=overall_risk,
                risk_score=risk_score,
                daily_pnl=daily_pnl,
                daily_pnl_pct=daily_pnl_pct,
                daily_loss_limit=daily_loss_limit,
                daily_loss_remaining=daily_loss_remaining,
                largest_position_pct=10.0,  # Mock data
                position_concentration=0.3,  # Mock data
                risk_flags=risk_flags,
                trading_halted=trading_halted,
            )

        except Exception as e:
            logger.error(f"Error getting risk status: {e}")
            return RiskStatus(
                portfolio_id=portfolio_id,
                overall_risk=RiskLevel.HIGH,
                risk_score=0.9,
                daily_pnl=Decimal("0"),
                daily_pnl_pct=0.0,
                daily_loss_limit=Decimal("2000"),
                daily_loss_remaining=Decimal("2000"),
                largest_position_pct=0.0,
                position_concentration=0.0,
                risk_flags=["Error calculating risk status"],
                trading_halted=True,
            )

    def _calculate_concentration_risk(self, positions: List, total_value: Decimal) -> float:
        """Calculate position concentration risk."""
        if not positions or total_value <= 0:
            return 0.0

        # Calculate position sizes as percentages
        position_pcts = [float(pos.current_value / total_value) for pos in positions]

        # Concentration risk based on largest positions
        largest_position = max(position_pcts) if position_pcts else 0

        # Risk increases exponentially with concentration
        if largest_position > self.max_position_size_pct:
            return min(1.0, largest_position * 2)  # Cap at 1.0
        else:
            return largest_position / self.max_position_size_pct * 0.5  # Scale to 0-0.5

    def _calculate_market_risk(self, positions: List, market_data: Dict) -> float:
        """Calculate market risk based on correlations and beta."""
        if not positions or not market_data:
            return 0.5  # Neutral risk

        # Simplified market risk calculation
        # In production, would calculate portfolio beta and correlation to market

        # Average price change as proxy for market risk
        price_changes = []
        for pos in positions:
            if pos.symbol in market_data:
                price_changes.append(abs(market_data[pos.symbol].change_percent))

        if not price_changes:
            return 0.5

        avg_volatility = sum(price_changes) / len(price_changes)

        # Scale to 0-1 range
        return min(1.0, avg_volatility / 10.0)  # 10% change = 1.0 risk

    def _calculate_volatility_risk(self, positions: List, market_data: Dict) -> float:
        """Calculate volatility risk."""
        if not positions:
            return 0.0

        # Mock volatility calculation
        # In production, would use actual volatility data
        volatilities = []
        for pos in positions:
            # Generate mock volatility based on position
            mock_volatility = 0.15 + (hash(pos.symbol) % 30) / 100  # 0.15-0.45
            volatilities.append(mock_volatility)

        if not volatilities:
            return 0.5

        avg_volatility = sum(volatilities) / len(volatilities)

        # Scale based on thresholds
        if avg_volatility > self.extreme_volatility_threshold:
            return 1.0
        elif avg_volatility > self.high_volatility_threshold:
            return 0.7
        else:
            return avg_volatility / self.high_volatility_threshold * 0.5

    def _calculate_liquidity_risk(self, positions: List, market_data: Dict) -> float:
        """Calculate liquidity risk based on volume and market cap."""
        if not positions:
            return 0.0

        # Simplified liquidity risk
        # In production, would use actual volume and market cap data

        liquidity_scores = []
        for pos in positions:
            if pos.symbol in market_data:
                volume = market_data[pos.symbol].volume
                # Higher volume = lower liquidity risk
                if volume > 5000000:  # High volume
                    liquidity_scores.append(0.1)
                elif volume > 1000000:  # Medium volume
                    liquidity_scores.append(0.3)
                else:  # Low volume
                    liquidity_scores.append(0.7)
            else:
                liquidity_scores.append(0.5)  # Unknown = medium risk

        return sum(liquidity_scores) / len(liquidity_scores) if liquidity_scores else 0.5

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score."""
        if risk_score >= 0.8:
            return RiskLevel.EXTREME
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_risk_warnings(self, concentration_risk: float, market_risk: float, volatility_risk: float, liquidity_risk: float) -> List[str]:
        """Generate risk warnings based on risk factors."""
        warnings = []

        if concentration_risk > 0.7:
            warnings.append("High position concentration detected")

        if market_risk > 0.7:
            warnings.append("Elevated market risk conditions")

        if volatility_risk > 0.7:
            warnings.append("High volatility environment")

        if liquidity_risk > 0.7:
            warnings.append("Liquidity concerns in some positions")

        return warnings

    def _generate_risk_mitigation(self, concentration_risk: float, market_risk: float, volatility_risk: float, liquidity_risk: float) -> List[str]:
        """Generate risk mitigation suggestions."""
        mitigation = []

        if concentration_risk > 0.6:
            mitigation.append("Consider reducing position sizes")
            mitigation.append("Diversify across more positions")

        if market_risk > 0.6:
            mitigation.append("Add defensive positions")
            mitigation.append("Consider hedging strategies")

        if volatility_risk > 0.6:
            mitigation.append("Reduce position sizes in volatile stocks")
            mitigation.append("Use limit orders instead of market orders")

        if liquidity_risk > 0.6:
            mitigation.append("Monitor position sizes in low-volume stocks")
            mitigation.append("Plan exit strategies for illiquid positions")

        return mitigation

    def _calculate_portfolio_beta(self, positions: List, market_data: Dict) -> Optional[float]:
        """Calculate portfolio beta (simplified)."""
        # Mock beta calculation
        # In production, would calculate actual beta vs market index
        return 1.2  # Slightly more volatile than market

    def _calculate_var_1day(self, positions: List, market_data: Dict) -> Optional[float]:
        """Calculate 1-day Value at Risk (simplified)."""
        if not positions:
            return 0.0

        # Simplified VaR calculation
        total_value = sum(pos.current_value for pos in positions)

        # Assume 95% confidence, 2% daily volatility
        var_1day = float(total_value) * 0.02 * 1.65  # 1.65 = 95% confidence z-score

        return var_1day

    def _calculate_max_drawdown(self, portfolio_id: int, current_value: Decimal) -> Optional[float]:
        """Calculate maximum drawdown from peak."""
        # Track portfolio peak
        if portfolio_id not in self._portfolio_peaks:
            self._portfolio_peaks[portfolio_id] = current_value
        else:
            self._portfolio_peaks[portfolio_id] = max(self._portfolio_peaks[portfolio_id], current_value)

        peak_value = self._portfolio_peaks[portfolio_id]

        if peak_value > 0:
            drawdown = float((peak_value - current_value) / peak_value)
            return max(0, drawdown)

        return 0.0

    def _check_position_limits(self, trade: TradeRecommendation) -> bool:
        """Check if trade violates position limits."""
        return trade.position_size_pct <= self.max_position_size_pct

    def _is_market_open(self) -> bool:
        """Check if market is currently open (simplified)."""
        # Simplified market hours check
        # In production, would check actual market hours and holidays
        now = datetime.now()

        # Check if weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Check if during market hours (9:30 AM - 4:00 PM ET)
        # This is simplified and doesn't account for timezone
        hour = now.hour
        return 9 <= hour <= 16
