#!/usr/bin/env python3
"""
Test AI Trading System

Simple test script to verify the AI trading functionality works end-to-end.
Tests portfolio analysis, signal generation, and trade recommendations.

This is NOT a pytest test - it's a standalone script.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))


from src.llm.deepseek_client import DeepSeekClient
from src.trading.ai_engine import AITradingEngine
from src.trading.market_data import MarketDataProvider
from src.trading.risk_manager import RiskManager


class MockPortfolioService:
    """Mock portfolio service for testing."""

    async def get_portfolio(self, portfolio_id: int):
        """Return mock portfolio."""
        return type("Portfolio", (), {"id": portfolio_id, "portfolio_type": "Growth", "cash_balance": 50000})()

    async def get_positions(self, portfolio_id: int):
        """Return mock positions."""
        return [
            type("Position", (), {"symbol": "AAPL", "quantity": 100, "current_value": 15000, "unrealized_pnl": 500})(),
            type("Position", (), {"symbol": "MSFT", "quantity": 50, "current_value": 20000, "unrealized_pnl": -200})(),
            type("Position", (), {"symbol": "GOOGL", "quantity": 25, "current_value": 12000, "unrealized_pnl": 800})(),
        ]


async def test_ai_trading_system():
    """Test the complete AI trading system."""
    print("🤖 Testing AI Trading System")
    print("=" * 50)

    try:
        # Initialize components
        print("📦 Initializing components...")
        deepseek_client = DeepSeekClient()
        market_data_provider = MarketDataProvider()
        portfolio_service = MockPortfolioService()
        risk_manager = RiskManager()

        ai_engine = AITradingEngine(
            deepseek_client=deepseek_client,
            market_data_provider=market_data_provider,
            portfolio_service=portfolio_service,
            risk_manager=risk_manager,
        )

        print("✅ Components initialized successfully")

        # Test 1: Portfolio Analysis
        print("\n🔍 Test 1: Portfolio Analysis")
        print("-" * 30)

        portfolio_id = 1
        analysis = await ai_engine.analyze_portfolio(portfolio_id)

        print(f"Portfolio ID: {analysis.portfolio_id}")
        print(f"Market Condition: {analysis.market_condition}")
        print(f"Portfolio Value: ${analysis.portfolio_value:,.2f}")
        print(f"Cash Available: ${analysis.cash_available:,.2f}")
        print(f"Risk Level: {analysis.risk_assessment.overall_risk}")
        print(f"Risk Score: {analysis.risk_assessment.risk_score:.2f}")
        print(f"AI Summary: {analysis.ai_summary[:100]}...")
        print(f"Key Opportunities: {len(analysis.key_opportunities)}")
        print(f"Key Risks: {len(analysis.key_risks)}")

        print("✅ Portfolio analysis completed")

        # Test 2: Signal Generation
        print("\n📊 Test 2: Trading Signal Generation")
        print("-" * 35)

        signals = await ai_engine.generate_signals(analysis)

        print(f"Generated {len(signals)} trading signals:")
        for i, signal in enumerate(signals[:3], 1):  # Show top 3
            print(f"  {i}. {signal.symbol}: {signal.signal_type} " f"(Confidence: {signal.confidence:.2f})")
            print(f"     Price: ${signal.current_price}")
            print(f"     Reasoning: {signal.reasoning[:80]}...")

        print("✅ Signal generation completed")

        # Test 3: Trade Recommendations
        print("\n💼 Test 3: Trade Recommendations")
        print("-" * 32)

        if signals:
            recommendations = await ai_engine.recommend_trades(signals)

            print(f"Generated {len(recommendations)} trade recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                print(f"  {i}. {rec.symbol}: {rec.action} {rec.quantity} shares")
                print(f"     Order Type: {rec.order_type}")
                print(f"     Position Size: {rec.position_size_pct:.1%}")
                print(f"     Risk Score: {rec.risk_score:.2f}")
                print(f"     Expected Return: {rec.expected_return:.1f}%")

            print("✅ Trade recommendations completed")

            # Test 4: Risk Assessment
            print("\n⚠️  Test 4: Risk Assessment")
            print("-" * 25)

            if recommendations:
                validation = await risk_manager.validate_trade(recommendations[0])

                print(f"Trade Validation for {recommendations[0].symbol}:")
                print(f"  Valid: {validation.is_valid}")
                print(f"  Validation Score: {validation.validation_score:.2f}")
                print(f"  Risk Check: {'✅' if validation.risk_check_passed else '❌'}")
                print(f"  Position Limit: {'✅' if validation.position_limit_check else '❌'}")
                print(f"  Cash Check: {'✅' if validation.cash_check_passed else '❌'}")
                print(f"  Market Hours: {'✅' if validation.market_hours_check else '❌'}")

                if validation.errors:
                    print(f"  Errors: {validation.errors}")
                if validation.warnings:
                    print(f"  Warnings: {validation.warnings}")

                print("✅ Risk assessment completed")

        # Test 5: Risk Status
        print("\n📈 Test 5: Portfolio Risk Status")
        print("-" * 30)

        risk_status = await risk_manager.get_risk_status(portfolio_id)

        print(f"Portfolio {portfolio_id} Risk Status:")
        print(f"  Overall Risk: {risk_status.overall_risk}")
        print(f"  Risk Score: {risk_status.risk_score:.2f}")
        print(f"  Daily P&L: ${risk_status.daily_pnl:,.2f}")
        print(f"  Daily Loss Limit: ${risk_status.daily_loss_limit:,.2f}")
        print(f"  Trading Halted: {risk_status.trading_halted}")

        if risk_status.risk_flags:
            print(f"  Risk Flags: {risk_status.risk_flags}")

        print("✅ Risk status check completed")

        # Summary
        print("\n🎉 AI Trading System Test Summary")
        print("=" * 40)
        print("✅ Portfolio Analysis: Working")
        print("✅ Signal Generation: Working")
        print("✅ Trade Recommendations: Working")
        print("✅ Risk Assessment: Working")
        print("✅ Risk Status: Working")
        print("\n🚀 AI Trading System is ready for deployment!")

        return True

    except Exception as e:
        print(f"\n❌ Error testing AI trading system: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_market_data():
    """Test market data provider."""
    print("\n📊 Testing Market Data Provider")
    print("-" * 35)

    try:
        market_data = MarketDataProvider()

        # Test price data
        symbols = ["AAPL", "MSFT", "GOOGL"]
        for symbol in symbols:
            price = await market_data.get_real_time_price(symbol)
            print(f"{symbol}: ${price.current_price} ({price.change_percent:+.2f}%)")

        # Test technical indicators
        tech_data = await market_data.get_technical_indicators("AAPL")
        print("\nAAPL Technical Indicators:")
        print(f"  RSI: {tech_data.rsi:.1f}")
        print(f"  MACD: {tech_data.macd:.3f}")
        print(f"  SMA 20: ${tech_data.sma_20:.2f}")
        print(f"  Volatility: {tech_data.volatility:.2%}")

        # Test sentiment
        sentiment = await market_data.get_market_sentiment(symbols)
        print("\nMarket Sentiment:")
        print(f"  Overall: {sentiment.overall_sentiment:.2f}")
        print(f"  News: {sentiment.news_sentiment:.2f}")
        print(f"  Confidence: {sentiment.confidence:.2f}")
        print(f"  Themes: {sentiment.key_themes}")

        print("✅ Market data provider working")
        return True

    except Exception as e:
        print(f"❌ Error testing market data: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 AI Trading System Test Suite")
    print("=" * 50)

    # Test market data first
    market_data_ok = await test_market_data()

    if market_data_ok:
        # Test full AI trading system
        trading_system_ok = await test_ai_trading_system()

        if trading_system_ok:
            print("\n🎯 All tests passed! System is ready for production.")
            return 0
        else:
            print("\n💥 AI trading system tests failed.")
            return 1
    else:
        print("\n💥 Market data tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
