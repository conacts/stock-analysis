#!/usr/bin/env python3
"""
Data Storage and Management
Handles storing daily analysis, decisions, and tracking performance
"""

import json
import logging
import sqlite3
from datetime import date
from pathlib import Path
from typing import Dict, List

import pandas as pd


class AnalysisStorage:
    """
    Manages storage and retrieval of stock analysis data
    Tracks daily decisions, reasoning, and performance
    """

    def __init__(self, db_path: str = "data/stock_analysis.db"):
        """Initialize storage system"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Daily analysis table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    analysis_data TEXT NOT NULL,
                    composite_score REAL,
                    rating TEXT,
                    confidence TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, symbol)
                )
            """
            )

            # Daily decisions table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    selected_stocks TEXT,
                    market_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            """
            )

            # Performance tracking table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    recommendation_date TEXT NOT NULL,
                    entry_price REAL,
                    current_price REAL,
                    target_price REAL,
                    rating TEXT,
                    days_held INTEGER,
                    return_pct REAL,
                    status TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Market context table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS market_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    market_sentiment TEXT,
                    vix_level REAL,
                    sector_rotation TEXT,
                    economic_indicators TEXT,
                    news_themes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            """
            )

            conn.commit()

    def store_daily_analysis(self, analysis_data: Dict) -> bool:
        """
        Store daily stock analysis

        Args:
            analysis_data: Complete analysis dictionary from StockAnalyzer

        Returns:
            Success status
        """
        try:
            today = date.today().isoformat()
            symbol = analysis_data["symbol"]

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO daily_analysis
                    (date, symbol, analysis_data, composite_score, rating, confidence)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        today,
                        symbol,
                        json.dumps(analysis_data),
                        analysis_data["score"]["composite_score"],
                        analysis_data["recommendation"]["rating"],
                        analysis_data["recommendation"]["confidence"],
                    ),
                )
                conn.commit()

            self.logger.info(f"Stored analysis for {symbol} on {today}")
            return True

        except Exception as e:
            self.logger.error(f"Error storing analysis: {e}")
            return False

    def store_daily_decision(self, decision_data: Dict) -> bool:
        """
        Store daily investment decision and reasoning

        Args:
            decision_data: Dictionary containing decision details

        Returns:
            Success status
        """
        try:
            today = date.today().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO daily_decisions
                    (date, decision_type, reasoning, selected_stocks, market_context)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        today,
                        decision_data.get("decision_type", "daily_pick"),
                        decision_data.get("reasoning", ""),
                        json.dumps(decision_data.get("selected_stocks", [])),
                        json.dumps(decision_data.get("market_context", {})),
                    ),
                )
                conn.commit()

            self.logger.info(f"Stored daily decision for {today}")
            return True

        except Exception as e:
            self.logger.error(f"Error storing decision: {e}")
            return False

    def get_analysis_history(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Get historical analysis for a symbol

        Args:
            symbol: Stock ticker
            days: Number of days to look back

        Returns:
            List of historical analysis data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT date, analysis_data, composite_score, rating, confidence
                    FROM daily_analysis
                    WHERE symbol = ?
                    ORDER BY date DESC
                    LIMIT ?
                """,
                    (symbol, days),
                )

                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "date": row[0],
                            "analysis_data": json.loads(row[1]),
                            "composite_score": row[2],
                            "rating": row[3],
                            "confidence": row[4],
                        }
                    )

                return results

        except Exception as e:
            self.logger.error(f"Error retrieving history for {symbol}: {e}")
            return []

    def get_daily_decisions(self, days: int = 30) -> List[Dict]:
        """Get recent daily decisions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT date, decision_type, reasoning, selected_stocks, market_context
                    FROM daily_decisions
                    ORDER BY date DESC
                    LIMIT ?
                """,
                    (days,),
                )

                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "date": row[0],
                            "decision_type": row[1],
                            "reasoning": row[2],
                            "selected_stocks": json.loads(row[3]),
                            "market_context": json.loads(row[4]),
                        }
                    )

                return results

        except Exception as e:
            self.logger.error(f"Error retrieving decisions: {e}")
            return []

    def update_performance(self, symbol: str, current_price: float) -> bool:
        """Update performance tracking for a symbol"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get latest recommendation
                cursor = conn.execute(
                    """
                    SELECT entry_price, target_price, recommendation_date, rating
                    FROM performance_tracking
                    WHERE symbol = ? AND status = 'active'
                    ORDER BY recommendation_date DESC
                    LIMIT 1
                """,
                    (symbol,),
                )

                row = cursor.fetchone()
                if not row:
                    return False

                entry_price, target_price, rec_date, rating = row

                # Calculate performance
                return_pct = ((current_price - entry_price) / entry_price) * 100
                days_held = (date.today() - date.fromisoformat(rec_date)).days

                # Update performance
                conn.execute(
                    """
                    UPDATE performance_tracking
                    SET current_price = ?, return_pct = ?, days_held = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE symbol = ? AND status = 'active'
                """,
                    (current_price, return_pct, days_held, symbol),
                )

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error updating performance for {symbol}: {e}")
            return False

    def get_performance_summary(self) -> Dict:
        """Get overall performance summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get active positions
                cursor = conn.execute(
                    """
                    SELECT symbol, entry_price, current_price, return_pct, days_held, rating
                    FROM performance_tracking
                    WHERE status = 'active'
                """
                )

                active_positions = []
                total_return = 0
                count = 0

                for row in cursor.fetchall():
                    (
                        symbol,
                        entry_price,
                        current_price,
                        return_pct,
                        days_held,
                        rating,
                    ) = row
                    active_positions.append(
                        {
                            "symbol": symbol,
                            "entry_price": entry_price,
                            "current_price": current_price,
                            "return_pct": return_pct,
                            "days_held": days_held,
                            "rating": rating,
                        }
                    )

                    if return_pct:
                        total_return += return_pct
                        count += 1

                avg_return = total_return / count if count > 0 else 0

                return {
                    "active_positions": active_positions,
                    "total_positions": len(active_positions),
                    "average_return": avg_return,
                    "total_return": total_return,
                }

        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {}

    def store_market_context(self, context_data: Dict) -> bool:
        """Store daily market context"""
        try:
            today = date.today().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO market_context
                    (date, market_sentiment, vix_level, sector_rotation, economic_indicators, news_themes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        today,
                        context_data.get("market_sentiment", "Neutral"),
                        context_data.get("vix_level", 0),
                        json.dumps(context_data.get("sector_rotation", {})),
                        json.dumps(context_data.get("economic_indicators", {})),
                        json.dumps(context_data.get("news_themes", [])),
                    ),
                )
                conn.commit()

            return True

        except Exception as e:
            self.logger.error(f"Error storing market context: {e}")
            return False

    def export_to_csv(self, table_name: str, output_path: str) -> bool:
        """Export table data to CSV"""
        try:
            # Validate table name to prevent SQL injection
            valid_tables = [
                "daily_analysis",
                "daily_decisions",
                "market_context",
                "performance_tracking",
            ]

            if table_name not in valid_tables:
                self.logger.error(f"Invalid table name: {table_name}")
                return False

            with sqlite3.connect(self.db_path) as conn:
                # Use validated table name (safe since it's from whitelist)
                query = f"SELECT * FROM {table_name}"  # nosec B608
                df = pd.read_sql_query(query, conn)
                df.to_csv(output_path, index=False)

            self.logger.info(f"Exported {table_name} to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting {table_name}: {e}")
            return False

    def cleanup_old_data(self, days_to_keep: int = 365) -> bool:
        """Clean up old data beyond specified days"""
        try:
            cutoff_date = (date.today() - pd.Timedelta(days=days_to_keep)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                # Clean up old analysis data
                conn.execute(
                    "DELETE FROM daily_analysis WHERE date < ?", (cutoff_date,)
                )

                # Clean up old decisions
                conn.execute(
                    "DELETE FROM daily_decisions WHERE date < ?", (cutoff_date,)
                )

                # Clean up old market context
                conn.execute(
                    "DELETE FROM market_context WHERE date < ?", (cutoff_date,)
                )

                conn.commit()

            self.logger.info(f"Cleaned up data older than {cutoff_date}")
            return True

        except Exception as e:
            self.logger.error(f"Error cleaning up data: {e}")
            return False


class DecisionTracker:
    """
    Tracks and analyzes decision-making patterns
    """

    def __init__(self, storage: AnalysisStorage):
        """Initialize with storage backend"""
        self.storage = storage
        self.logger = logging.getLogger(__name__)

    def analyze_decision_patterns(self) -> Dict:
        """Analyze historical decision patterns"""
        try:
            decisions = self.storage.get_daily_decisions(90)  # Last 90 days

            if not decisions:
                return {}

            # Analyze patterns
            decision_types = {}
            sector_preferences = {}
            rating_distribution = {}

            for decision in decisions:
                # Decision type frequency
                dtype = decision["decision_type"]
                decision_types[dtype] = decision_types.get(dtype, 0) + 1

                # Analyze selected stocks
                for stock_data in decision["selected_stocks"]:
                    if isinstance(stock_data, dict):
                        sector = stock_data.get("sector", "Unknown")
                        rating = stock_data.get("rating", "Unknown")

                        sector_preferences[sector] = (
                            sector_preferences.get(sector, 0) + 1
                        )
                        rating_distribution[rating] = (
                            rating_distribution.get(rating, 0) + 1
                        )

            return {
                "total_decisions": len(decisions),
                "decision_types": decision_types,
                "sector_preferences": sector_preferences,
                "rating_distribution": rating_distribution,
                "analysis_period_days": 90,
            }

        except Exception as e:
            self.logger.error(f"Error analyzing decision patterns: {e}")
            return {}

    def generate_decision_summary(
        self, selected_stocks: List[Dict], reasoning: str
    ) -> Dict:
        """Generate a comprehensive decision summary"""
        try:
            summary = {
                "decision_type": "daily_stock_selection",
                "reasoning": reasoning,
                "selected_stocks": selected_stocks,
                "market_context": {
                    "analysis_date": date.today().isoformat(),
                    "total_stocks_analyzed": len(selected_stocks),
                    "selection_criteria": "Composite score + risk assessment",
                },
                "decision_metadata": {
                    "avg_score": (
                        sum(s.get("score", 0) for s in selected_stocks)
                        / len(selected_stocks)
                        if selected_stocks
                        else 0
                    ),
                    "sectors_represented": list(
                        set(s.get("sector", "Unknown") for s in selected_stocks)
                    ),
                    "risk_levels": list(
                        set(s.get("risk_level", "Unknown") for s in selected_stocks)
                    ),
                },
            }

            return summary

        except Exception as e:
            self.logger.error(f"Error generating decision summary: {e}")
            return {}
