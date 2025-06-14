"""
Tests for Portfolio Manager

Tests portfolio CRUD operations, position management, and analytics
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.db.models import Portfolio, PortfolioPosition, PortfolioSnapshot, PortfolioTransaction
from src.portfolio.portfolio_manager import PortfolioManager


class TestPortfolioManager:
    """Test portfolio manager functionality"""

    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection"""
        mock_db = Mock()
        mock_session = Mock()
        mock_db.get_session.return_value = mock_session
        return mock_db, mock_session

    @pytest.fixture
    def mock_stock_data(self):
        """Mock stock data provider"""
        mock_provider = Mock()
        mock_provider.get_current_price.return_value = 150.0
        return mock_provider

    @pytest.fixture
    def portfolio_manager(self, mock_db_connection, mock_stock_data):
        """Create portfolio manager with mocked dependencies"""
        mock_db, mock_session = mock_db_connection

        with patch("src.portfolio.portfolio_manager.DatabaseConnection", return_value=mock_db):
            with patch("src.portfolio.portfolio_manager.StockDataProvider", return_value=mock_stock_data):
                manager = PortfolioManager()
                manager.db = mock_db
                manager.stock_data = mock_stock_data
                return manager, mock_session

    def test_create_portfolio_success(self, portfolio_manager):
        """Test successful portfolio creation"""
        manager, mock_session = portfolio_manager

        # Mock successful database insert
        mock_result = Mock()
        mock_result.fetchone.return_value = [1]  # Portfolio ID
        mock_session.execute.return_value = mock_result

        portfolio_id = manager.create_portfolio("Test Portfolio", "Test description", "personal")

        assert portfolio_id == 1
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_create_portfolio_failure(self, portfolio_manager):
        """Test portfolio creation failure"""
        manager, mock_session = portfolio_manager

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        portfolio_id = manager.create_portfolio("Test Portfolio", "Test description")

        assert portfolio_id is None
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_portfolio_success(self, portfolio_manager):
        """Test successful portfolio retrieval"""
        manager, mock_session = portfolio_manager

        # Mock database result
        mock_result = Mock()
        mock_result.fetchone.return_value = [1, "Test Portfolio", "Description", "personal", "USD", datetime.now(), datetime.now(), True]
        mock_session.execute.return_value = mock_result

        portfolio = manager.get_portfolio(1)

        assert portfolio is not None
        assert portfolio.id == 1
        assert portfolio.name == "Test Portfolio"
        assert portfolio.description == "Description"
        assert portfolio.portfolio_type == "personal"

    def test_get_portfolio_not_found(self, portfolio_manager):
        """Test portfolio not found"""
        manager, mock_session = portfolio_manager

        # Mock empty result
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_session.execute.return_value = mock_result

        portfolio = manager.get_portfolio(999)

        assert portfolio is None

    def test_list_portfolios(self, portfolio_manager):
        """Test listing all portfolios"""
        manager, mock_session = portfolio_manager

        # Mock database results
        mock_result = Mock()
        mock_result.fetchall.return_value = [[1, "Portfolio 1", "Desc 1", "personal", "USD", datetime.now(), datetime.now(), True], [2, "Portfolio 2", "Desc 2", "ira", "USD", datetime.now(), datetime.now(), True]]
        mock_session.execute.return_value = mock_result

        portfolios = manager.list_portfolios()

        assert len(portfolios) == 2
        assert portfolios[0].name == "Portfolio 1"
        assert portfolios[1].name == "Portfolio 2"

    def test_add_position_new(self, portfolio_manager):
        """Test adding a new position"""
        manager, mock_session = portfolio_manager

        # Mock no existing position
        with patch.object(manager, "get_position", return_value=None):
            with patch.object(manager, "update_position_prices", return_value=True):
                result = manager.add_position(1, "AAPL", 100.0, 150.0, "Technology")

                assert result is True
                mock_session.execute.assert_called()
                mock_session.commit.assert_called_once()

    def test_add_position_update_existing(self, portfolio_manager):
        """Test updating an existing position"""
        manager, mock_session = portfolio_manager

        # Mock existing position
        existing_position = Mock()
        existing_position.quantity = Decimal("50.0")
        existing_position.average_cost = Decimal("140.0")

        with patch.object(manager, "get_position", return_value=existing_position):
            with patch.object(manager, "update_position_prices", return_value=True):
                result = manager.add_position(1, "AAPL", 50.0, 160.0, "Technology")

                assert result is True
                # Should calculate new average: (50*140 + 50*160) / 100 = 150
                mock_session.execute.assert_called()

    def test_get_position_success(self, portfolio_manager):
        """Test successful position retrieval"""
        manager, mock_session = portfolio_manager

        # Mock database result
        mock_result = Mock()
        mock_result.fetchone.return_value = [1, 1, "AAPL", Decimal("100.0"), Decimal("150.0"), Decimal("155.0"), Decimal("15500.0"), Decimal("500.0"), Decimal("3.33"), "Technology", datetime.now()]
        mock_session.execute.return_value = mock_result

        position = manager.get_position(1, "AAPL")

        assert position is not None
        assert position.symbol == "AAPL"
        assert position.quantity == Decimal("100.0")
        assert position.average_cost == Decimal("150.0")

    def test_get_portfolio_positions(self, portfolio_manager):
        """Test getting all positions for a portfolio"""
        manager, mock_session = portfolio_manager

        # Mock database results
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            [1, 1, "AAPL", Decimal("100.0"), Decimal("150.0"), Decimal("155.0"), Decimal("15500.0"), Decimal("500.0"), Decimal("3.33"), "Technology", datetime.now()],
            [2, 1, "GOOGL", Decimal("50.0"), Decimal("120.0"), Decimal("125.0"), Decimal("6250.0"), Decimal("250.0"), Decimal("4.17"), "Technology", datetime.now()],
        ]
        mock_session.execute.return_value = mock_result

        positions = manager.get_portfolio_positions(1)

        assert len(positions) == 2
        assert positions[0].symbol == "AAPL"
        assert positions[1].symbol == "GOOGL"

    def test_update_position_prices_success(self, portfolio_manager):
        """Test successful position price update"""
        manager, mock_session = portfolio_manager

        # Mock existing position
        existing_position = Mock()
        existing_position.quantity = Decimal("100.0")
        existing_position.average_cost = Decimal("150.0")

        with patch.object(manager, "get_position", return_value=existing_position):
            # Mock current price from stock data
            manager.stock_data.get_current_price.return_value = 155.0

            result = manager.update_position_prices(1, "AAPL")

            assert result is True
            mock_session.execute.assert_called()
            mock_session.commit.assert_called_once()

    def test_update_position_prices_no_position(self, portfolio_manager):
        """Test price update when position doesn't exist"""
        manager, mock_session = portfolio_manager

        with patch.object(manager, "get_position", return_value=None):
            result = manager.update_position_prices(1, "AAPL")

            assert result is False

    def test_update_position_prices_no_current_price(self, portfolio_manager):
        """Test price update when current price unavailable"""
        manager, mock_session = portfolio_manager

        existing_position = Mock()
        existing_position.quantity = Decimal("100.0")
        existing_position.average_cost = Decimal("150.0")

        with patch.object(manager, "get_position", return_value=existing_position):
            # Mock no current price available
            manager.stock_data.get_current_price.return_value = None

            result = manager.update_position_prices(1, "AAPL")

            assert result is False

    def test_update_all_positions(self, portfolio_manager):
        """Test updating all positions in a portfolio"""
        manager, mock_session = portfolio_manager

        # Mock positions
        positions = [Mock(symbol="AAPL"), Mock(symbol="GOOGL")]

        with patch.object(manager, "get_portfolio_positions", return_value=positions):
            with patch.object(manager, "update_position_prices", return_value=True) as mock_update:
                result = manager.update_all_positions(1)

                assert result is True
                assert mock_update.call_count == 2

    def test_record_transaction_success(self, portfolio_manager):
        """Test successful transaction recording"""
        manager, mock_session = portfolio_manager

        with patch.object(manager, "add_position", return_value=True):
            result = manager.record_transaction(1, "AAPL", "buy", 100.0, 150.0, 5.0, "2023-01-01", "Test transaction")

            assert result is True
            mock_session.execute.assert_called()
            mock_session.commit.assert_called_once()

    def test_record_transaction_sell(self, portfolio_manager):
        """Test recording a sell transaction"""
        manager, mock_session = portfolio_manager

        with patch.object(manager, "add_position", return_value=True) as mock_add:
            result = manager.record_transaction(1, "AAPL", "sell", 50.0, 160.0, 5.0)

            assert result is True
            # Should call add_position with negative quantity for sell
            mock_add.assert_called_with(1, "AAPL", -50.0, 160.0)

    def test_get_portfolio_summary_empty(self, portfolio_manager):
        """Test portfolio summary with no positions"""
        manager, mock_session = portfolio_manager

        with patch.object(manager, "get_portfolio_positions", return_value=[]):
            summary = manager.get_portfolio_summary(1)

            assert summary["total_value"] == 0.0
            assert summary["total_cost"] == 0.0
            assert summary["unrealized_pnl"] == 0.0
            assert summary["positions_count"] == 0
            assert summary["top_holdings"] == []
            assert summary["sector_allocation"] == {}

    def test_get_portfolio_summary_with_positions(self, portfolio_manager):
        """Test portfolio summary with positions"""
        manager, mock_session = portfolio_manager

        # Mock positions
        position1 = Mock()
        position1.symbol = "AAPL"
        position1.market_value = Decimal("15500.0")
        position1.quantity = Decimal("100.0")
        position1.average_cost = Decimal("150.0")
        position1.sector = "Technology"

        position2 = Mock()
        position2.symbol = "GOOGL"
        position2.market_value = Decimal("6250.0")
        position2.quantity = Decimal("50.0")
        position2.average_cost = Decimal("120.0")
        position2.sector = "Technology"

        positions = [position1, position2]

        with patch.object(manager, "get_portfolio_positions", return_value=positions):
            summary = manager.get_portfolio_summary(1)

            assert summary["total_value"] == 21750.0  # 15500 + 6250
            assert summary["total_cost"] == 21000.0  # (100*150) + (50*120)
            assert summary["unrealized_pnl"] == 750.0  # 21750 - 21000
            assert summary["positions_count"] == 2

            # Check top holdings
            assert len(summary["top_holdings"]) == 2
            assert summary["top_holdings"][0]["symbol"] == "AAPL"
            assert summary["top_holdings"][0]["allocation_pct"] > 70  # AAPL is larger

            # Check sector allocation
            assert summary["sector_allocation"]["Technology"] == 100.0

    def test_create_snapshot_success(self, portfolio_manager):
        """Test successful snapshot creation"""
        manager, mock_session = portfolio_manager

        # Mock portfolio summary
        mock_summary = {"total_value": 21750.0, "total_cost": 21000.0, "unrealized_pnl": 750.0, "unrealized_pnl_pct": 3.57, "positions_count": 2, "top_holdings": [{"symbol": "AAPL", "value": 15500.0}], "sector_allocation": {"Technology": 100.0}}

        with patch.object(manager, "get_portfolio_summary", return_value=mock_summary):
            result = manager.create_snapshot(1, "2023-01-01")

            assert result is True
            mock_session.execute.assert_called()
            mock_session.commit.assert_called_once()

    def test_create_snapshot_default_date(self, portfolio_manager):
        """Test snapshot creation with default date"""
        manager, mock_session = portfolio_manager

        mock_summary = {"total_value": 0.0, "total_cost": 0.0, "unrealized_pnl": 0.0, "unrealized_pnl_pct": 0.0, "positions_count": 0, "top_holdings": [], "sector_allocation": {}}

        with patch.object(manager, "get_portfolio_summary", return_value=mock_summary):
            result = manager.create_snapshot(1)  # No date provided

            assert result is True
            # Should use today's date - check that execute was called
            mock_session.execute.assert_called()
            mock_session.commit.assert_called_once()

    def test_error_handling_database_exception(self, portfolio_manager):
        """Test error handling for database exceptions"""
        manager, mock_session = portfolio_manager

        # Mock database error
        mock_session.execute.side_effect = Exception("Database connection lost")

        # Test various methods handle errors gracefully
        assert manager.create_portfolio("Test") is None
        assert manager.get_portfolio(1) is None
        assert manager.list_portfolios() == []
        assert manager.add_position(1, "AAPL", 100, 150) is False
        assert manager.get_position(1, "AAPL") is None
        assert manager.get_portfolio_positions(1) == []
        assert manager.update_position_prices(1, "AAPL") is False
        assert manager.record_transaction(1, "AAPL", "buy", 100, 150) is False
        # get_portfolio_summary returns default values on error, not empty dict
        summary = manager.get_portfolio_summary(1)
        assert isinstance(summary, dict)
        assert manager.create_snapshot(1) is False

    def test_decimal_float_conversion(self, portfolio_manager):
        """Test proper handling of Decimal/float conversions"""
        manager, mock_session = portfolio_manager

        # Test with Decimal values from database
        existing_position = Mock()
        existing_position.quantity = Decimal("100.000000")
        existing_position.average_cost = Decimal("150.500000")

        with patch.object(manager, "get_position", return_value=existing_position):
            manager.stock_data.get_current_price.return_value = 155.75

            result = manager.update_position_prices(1, "AAPL")

            assert result is True
            # Verify that execute was called (calculations work with mixed Decimal/float types)
            mock_session.execute.assert_called()
            mock_session.commit.assert_called_once()


class TestPortfolioManagerIntegration:
    """Integration tests for portfolio manager"""

    @pytest.mark.integration
    def test_full_portfolio_workflow(self):
        """Test complete portfolio workflow"""
        # This would test with real database connection
        # Skip for now as it requires database setup
        pytest.skip("Integration test requires database setup")

    @pytest.mark.integration
    def test_real_stock_data_integration(self):
        """Test integration with real stock data"""
        # This would test with real stock data API
        pytest.skip("Integration test requires API setup")


class TestPortfolioModels:
    """Test portfolio data models"""

    def test_portfolio_model_creation(self):
        """Test Portfolio model creation"""
        portfolio = Portfolio(id=1, name="Test Portfolio", description="Test description", portfolio_type="personal", base_currency="USD", created_at=datetime.now(), updated_at=datetime.now(), is_active=True)

        assert portfolio.id == 1
        assert portfolio.name == "Test Portfolio"
        assert portfolio.portfolio_type == "personal"
        assert portfolio.is_active is True

    def test_portfolio_position_model_creation(self):
        """Test PortfolioPosition model creation"""
        position = PortfolioPosition(id=1, portfolio_id=1, symbol="AAPL", quantity=Decimal("100.0"), average_cost=Decimal("150.0"), current_price=Decimal("155.0"), market_value=Decimal("15500.0"), unrealized_pnl=Decimal("500.0"), unrealized_pnl_pct=Decimal("3.33"), sector="Technology", last_updated=datetime.now())

        assert position.symbol == "AAPL"
        assert position.quantity == Decimal("100.0")
        assert position.sector == "Technology"

    def test_portfolio_transaction_model_creation(self):
        """Test PortfolioTransaction model creation"""
        transaction = PortfolioTransaction(id=1, portfolio_id=1, symbol="AAPL", transaction_type="buy", quantity=Decimal("100.0"), price=Decimal("150.0"), total_amount=Decimal("15005.0"), fees=Decimal("5.0"), transaction_date=date.today(), notes="Test transaction", created_at=datetime.now())

        assert transaction.symbol == "AAPL"
        assert transaction.transaction_type == "buy"
        assert transaction.quantity == Decimal("100.0")
        assert transaction.fees == Decimal("5.0")

    def test_portfolio_snapshot_model_creation(self):
        """Test PortfolioSnapshot model creation"""
        snapshot = PortfolioSnapshot(
            id=1,
            portfolio_id=1,
            snapshot_date=date.today(),
            total_value=Decimal("21750.0"),
            cash_balance=Decimal("1000.0"),
            invested_amount=Decimal("21000.0"),
            unrealized_pnl=Decimal("750.0"),
            unrealized_pnl_pct=Decimal("3.57"),
            day_change=Decimal("250.0"),
            day_change_pct=Decimal("1.16"),
            positions_count=2,
            top_holdings='[{"symbol": "AAPL", "value": 15500.0}]',
            sector_allocation='{"Technology": 100.0}',
            created_at=datetime.now(),
        )

        assert snapshot.portfolio_id == 1
        assert snapshot.total_value == Decimal("21750.0")
        assert snapshot.positions_count == 2
