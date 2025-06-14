"""
Portfolio Manager

Main interface for portfolio operations including CRUD operations,
position management, and portfolio-level analytics.
"""

import json
import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from ..data.stock_data import StockDataProvider
from ..db.connection import DatabaseConnection
from ..db.models import Portfolio, PortfolioPosition


class PortfolioManager:
    """
    Manages portfolio operations and data persistence

    Handles multiple portfolios, positions, transactions, and snapshots
    """

    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """Initialize portfolio manager"""
        self.db = db_connection or DatabaseConnection()
        self.stock_data = StockDataProvider()
        self.logger = logging.getLogger(__name__)

    # Portfolio CRUD Operations

    def create_portfolio(self, name: str, description: str = "", portfolio_type: str = "personal") -> Optional[int]:
        """
        Create a new portfolio

        Args:
            name: Portfolio name (must be unique)
            description: Optional description
            portfolio_type: Type of portfolio (personal, ira, 401k, etc.)

        Returns:
            Portfolio ID if successful, None otherwise
        """
        try:
            session = self.db.get_session()
            now = datetime.now().isoformat()

            # Use raw SQL since we don't have SQLAlchemy models for portfolio tables yet
            query = text("""
                INSERT INTO portfolios (name, description, portfolio_type, created_at, updated_at)
                VALUES (:name, :description, :portfolio_type, :created_at, :updated_at)
                RETURNING id
            """)

            result = session.execute(query, {"name": name, "description": description, "portfolio_type": portfolio_type, "created_at": now, "updated_at": now})

            portfolio_id = result.fetchone()[0]
            session.commit()
            session.close()

            self.logger.info(f"Created portfolio '{name}' with ID {portfolio_id}")
            return portfolio_id

        except Exception as e:
            self.logger.error(f"Failed to create portfolio '{name}': {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return None

    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        try:
            session = self.db.get_session()
            query = text("SELECT * FROM portfolios WHERE id = :portfolio_id AND is_active = true")
            result = session.execute(query, {"portfolio_id": portfolio_id}).fetchone()
            session.close()

            if result:
                return Portfolio(id=result[0], name=result[1], description=result[2], portfolio_type=result[3], base_currency=result[4], created_at=result[5], updated_at=result[6], is_active=bool(result[7]))
            return None

        except Exception as e:
            self.logger.error(f"Failed to get portfolio {portfolio_id}: {e}")
            if "session" in locals():
                session.close()
            return None

    def list_portfolios(self) -> List[Portfolio]:
        """Get all active portfolios"""
        try:
            session = self.db.get_session()
            query = text("SELECT * FROM portfolios WHERE is_active = true ORDER BY created_at DESC")
            results = session.execute(query).fetchall()
            session.close()

            portfolios = []
            for row in results:
                portfolios.append(Portfolio(id=row[0], name=row[1], description=row[2], portfolio_type=row[3], base_currency=row[4], created_at=row[5], updated_at=row[6], is_active=bool(row[7])))

            return portfolios

        except Exception as e:
            self.logger.error(f"Failed to list portfolios: {e}")
            if "session" in locals():
                session.close()
            return []

    # Position Management

    def add_position(self, portfolio_id: int, symbol: str, quantity: float, average_cost: float, sector: str = "") -> bool:
        """
        Add or update a position in the portfolio

        Args:
            portfolio_id: Portfolio ID
            symbol: Stock symbol
            quantity: Number of shares
            average_cost: Average cost per share
            sector: Stock sector

        Returns:
            True if successful
        """
        try:
            session = self.db.get_session()

            # Check if position already exists
            existing = self.get_position(portfolio_id, symbol)

            if existing:
                # Update existing position
                existing_quantity = float(existing.quantity)
                existing_avg_cost = float(existing.average_cost)
                new_quantity_add = float(quantity)
                new_avg_cost_add = float(average_cost)

                new_quantity = existing_quantity + new_quantity_add
                new_avg_cost = ((existing_quantity * existing_avg_cost) + (new_quantity_add * new_avg_cost_add)) / new_quantity if new_quantity > 0 else 0

                query = text("""
                    UPDATE portfolio_positions
                    SET quantity = :quantity, average_cost = :average_cost, last_updated = :last_updated
                    WHERE portfolio_id = :portfolio_id AND symbol = :symbol
                """)
                session.execute(query, {"quantity": new_quantity, "average_cost": new_avg_cost, "last_updated": datetime.now().isoformat(), "portfolio_id": portfolio_id, "symbol": symbol})
            else:
                # Create new position
                query = text("""
                    INSERT INTO portfolio_positions
                    (portfolio_id, symbol, quantity, average_cost, sector, last_updated)
                    VALUES (:portfolio_id, :symbol, :quantity, :average_cost, :sector, :last_updated)
                """)
                session.execute(query, {"portfolio_id": portfolio_id, "symbol": symbol, "quantity": quantity, "average_cost": average_cost, "sector": sector, "last_updated": datetime.now().isoformat()})

            session.commit()
            session.close()

            # Update current prices
            self.update_position_prices(portfolio_id, symbol)

            self.logger.info(f"Added/updated position: {symbol} in portfolio {portfolio_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add position {symbol}: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    def get_position(self, portfolio_id: int, symbol: str) -> Optional[PortfolioPosition]:
        """Get a specific position"""
        try:
            session = self.db.get_session()
            query = text("""
                SELECT * FROM portfolio_positions
                WHERE portfolio_id = :portfolio_id AND symbol = :symbol
            """)
            result = session.execute(query, {"portfolio_id": portfolio_id, "symbol": symbol}).fetchone()
            session.close()

            if result:
                return PortfolioPosition(id=result[0], portfolio_id=result[1], symbol=result[2], quantity=result[3], average_cost=result[4], current_price=result[5], market_value=result[6], unrealized_pnl=result[7], unrealized_pnl_pct=result[8], sector=result[9], last_updated=result[10])
            return None

        except Exception as e:
            self.logger.error(f"Failed to get position {symbol}: {e}")
            if "session" in locals():
                session.close()
            return None

    def get_portfolio_positions(self, portfolio_id: int) -> List[PortfolioPosition]:
        """Get all positions for a portfolio"""
        try:
            session = self.db.get_session()
            query = text("""
                SELECT * FROM portfolio_positions
                WHERE portfolio_id = :portfolio_id AND quantity > 0
                ORDER BY market_value DESC
            """)
            results = session.execute(query, {"portfolio_id": portfolio_id}).fetchall()
            session.close()

            positions = []
            for row in results:
                positions.append(PortfolioPosition(id=row[0], portfolio_id=row[1], symbol=row[2], quantity=row[3], average_cost=row[4], current_price=row[5], market_value=row[6], unrealized_pnl=row[7], unrealized_pnl_pct=row[8], sector=row[9], last_updated=row[10]))

            return positions

        except Exception as e:
            self.logger.error(f"Failed to get portfolio positions: {e}")
            if "session" in locals():
                session.close()
            return []

    def update_position_prices(self, portfolio_id: int, symbol: str) -> bool:
        """Update current price and P&L for a position"""
        try:
            position = self.get_position(portfolio_id, symbol)
            if not position:
                return False

            # Get current price
            current_price = self.stock_data.get_current_price(symbol)
            if not current_price:
                return False

            # Convert to float for calculations
            quantity = float(position.quantity)
            average_cost = float(position.average_cost)
            current_price = float(current_price)

            # Calculate metrics
            market_value = quantity * current_price
            unrealized_pnl = market_value - (quantity * average_cost)
            unrealized_pnl_pct = (unrealized_pnl / (quantity * average_cost)) * 100 if (quantity * average_cost) > 0 else 0

            # Update database
            session = self.db.get_session()
            query = text("""
                UPDATE portfolio_positions
                SET current_price = :current_price, market_value = :market_value,
                    unrealized_pnl = :unrealized_pnl, unrealized_pnl_pct = :unrealized_pnl_pct,
                    last_updated = :last_updated
                WHERE portfolio_id = :portfolio_id AND symbol = :symbol
            """)

            session.execute(query, {"current_price": current_price, "market_value": market_value, "unrealized_pnl": unrealized_pnl, "unrealized_pnl_pct": unrealized_pnl_pct, "last_updated": datetime.now().isoformat(), "portfolio_id": portfolio_id, "symbol": symbol})

            session.commit()
            session.close()
            return True

        except Exception as e:
            self.logger.error(f"Failed to update prices for {symbol}: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    def update_all_positions(self, portfolio_id: int) -> bool:
        """Update prices for all positions in a portfolio"""
        try:
            positions = self.get_portfolio_positions(portfolio_id)

            for position in positions:
                self.update_position_prices(portfolio_id, position.symbol)

            self.logger.info(f"Updated prices for {len(positions)} positions")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update all positions: {e}")
            return False

    # Transaction Management

    def record_transaction(self, portfolio_id: int, symbol: str, transaction_type: str, quantity: float, price: float, fees: float = 0.0, transaction_date: str = None, notes: str = "") -> bool:
        """
        Record a buy/sell transaction

        Args:
            portfolio_id: Portfolio ID
            symbol: Stock symbol
            transaction_type: 'buy' or 'sell'
            quantity: Number of shares
            price: Price per share
            fees: Transaction fees
            transaction_date: Date of transaction (defaults to today)
            notes: Optional notes

        Returns:
            True if successful
        """
        try:
            if not transaction_date:
                transaction_date = date.today().isoformat()

            total_amount = quantity * price + fees

            session = self.db.get_session()
            query = text("""
                INSERT INTO portfolio_transactions
                (portfolio_id, symbol, transaction_type, quantity, price,
                 total_amount, fees, transaction_date, notes, created_at)
                VALUES (:portfolio_id, :symbol, :transaction_type, :quantity, :price,
                        :total_amount, :fees, :transaction_date, :notes, :created_at)
            """)

            session.execute(query, {"portfolio_id": portfolio_id, "symbol": symbol, "transaction_type": transaction_type, "quantity": quantity, "price": price, "total_amount": total_amount, "fees": fees, "transaction_date": transaction_date, "notes": notes, "created_at": datetime.now().isoformat()})

            session.commit()
            session.close()

            # Update position based on transaction
            if transaction_type.lower() == "buy":
                self.add_position(portfolio_id, symbol, quantity, price)
            elif transaction_type.lower() == "sell":
                self.add_position(portfolio_id, symbol, -quantity, price)

            self.logger.info(f"Recorded {transaction_type} transaction: {quantity} {symbol} @ ${price}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to record transaction: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    # Portfolio Analytics

    def get_portfolio_summary(self, portfolio_id: int) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        try:
            positions = self.get_portfolio_positions(portfolio_id)

            if not positions:
                return {"total_value": 0.0, "total_cost": 0.0, "unrealized_pnl": 0.0, "unrealized_pnl_pct": 0.0, "positions_count": 0, "top_holdings": [], "sector_allocation": {}}

            # Calculate totals
            total_value = sum(float(pos.market_value) for pos in positions)
            total_cost = sum(float(pos.quantity) * float(pos.average_cost) for pos in positions)
            unrealized_pnl = total_value - total_cost
            unrealized_pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0

            # Top holdings (by value)
            top_holdings = [{"symbol": pos.symbol, "value": float(pos.market_value), "allocation_pct": (float(pos.market_value) / total_value * 100) if total_value > 0 else 0} for pos in sorted(positions, key=lambda x: float(x.market_value), reverse=True)[:5]]

            # Sector allocation
            sector_allocation = {}
            for pos in positions:
                sector = pos.sector or "Unknown"
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0.0
                sector_allocation[sector] += float(pos.market_value)

            # Convert to percentages
            for sector in sector_allocation:
                sector_allocation[sector] = (sector_allocation[sector] / total_value * 100) if total_value > 0 else 0

            return {"total_value": total_value, "total_cost": total_cost, "unrealized_pnl": unrealized_pnl, "unrealized_pnl_pct": unrealized_pnl_pct, "positions_count": len(positions), "top_holdings": top_holdings, "sector_allocation": sector_allocation}

        except Exception as e:
            self.logger.error(f"Failed to get portfolio summary: {e}")
            return {}

    def create_snapshot(self, portfolio_id: int, snapshot_date: str = None) -> bool:
        """Create a daily portfolio snapshot"""
        try:
            if not snapshot_date:
                snapshot_date = date.today().isoformat()

            summary = self.get_portfolio_summary(portfolio_id)

            session = self.db.get_session()
            query = text("""
                INSERT INTO portfolio_snapshots
                (portfolio_id, snapshot_date, total_value, invested_amount,
                 unrealized_pnl, unrealized_pnl_pct, positions_count,
                 top_holdings, sector_allocation, created_at)
                VALUES (:portfolio_id, :snapshot_date, :total_value, :invested_amount,
                        :unrealized_pnl, :unrealized_pnl_pct, :positions_count,
                        :top_holdings, :sector_allocation, :created_at)
                ON CONFLICT (portfolio_id, snapshot_date)
                DO UPDATE SET
                    total_value = EXCLUDED.total_value,
                    invested_amount = EXCLUDED.invested_amount,
                    unrealized_pnl = EXCLUDED.unrealized_pnl,
                    unrealized_pnl_pct = EXCLUDED.unrealized_pnl_pct,
                    positions_count = EXCLUDED.positions_count,
                    top_holdings = EXCLUDED.top_holdings,
                    sector_allocation = EXCLUDED.sector_allocation,
                    created_at = EXCLUDED.created_at
            """)

            session.execute(
                query,
                {
                    "portfolio_id": portfolio_id,
                    "snapshot_date": snapshot_date,
                    "total_value": summary["total_value"],
                    "invested_amount": summary["total_cost"],
                    "unrealized_pnl": summary["unrealized_pnl"],
                    "unrealized_pnl_pct": summary["unrealized_pnl_pct"],
                    "positions_count": summary["positions_count"],
                    "top_holdings": json.dumps(summary["top_holdings"]),
                    "sector_allocation": json.dumps(summary["sector_allocation"]),
                    "created_at": datetime.now().isoformat(),
                },
            )

            session.commit()
            session.close()

            self.logger.info(f"Created snapshot for portfolio {portfolio_id} on {snapshot_date}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create snapshot: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False
