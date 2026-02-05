"""Database module for storing trading signals and performance tracking."""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class TradingDatabase:
    """SQLite database for paper trading tracker."""

    def __init__(self, db_path: str = "data/trading.db"):
        """Initialize database connection."""
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                asset VARCHAR(20) NOT NULL,
                signal_type VARCHAR(10) NOT NULL,
                confidence_score REAL NOT NULL,
                sentiment_score REAL NOT NULL,
                source_subreddit VARCHAR(50),
                post_count INTEGER,
                reasoning TEXT,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)

        # Paper trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                asset VARCHAR(20) NOT NULL,
                trade_type VARCHAR(10) NOT NULL,
                entry_price REAL,
                exit_price REAL,
                position_size REAL DEFAULT 1000.0,
                pnl REAL,
                status VARCHAR(20) DEFAULT 'open',
                closed_at DATETIME,
                FOREIGN KEY (signal_id) REFERENCES signals(id)
            )
        """)

        # Posts analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyzed_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                post_id VARCHAR(50) UNIQUE,
                subreddit VARCHAR(50),
                title TEXT,
                content TEXT,
                sentiment VARCHAR(20),
                sentiment_score REAL,
                mentioned_assets TEXT,
                url TEXT
            )
        """)

        conn.commit()
        conn.close()

    def add_signal(self, asset: str, signal_type: str, confidence_score: float,
                   sentiment_score: float, source_subreddit: str = None,
                   post_count: int = 0, reasoning: str = None) -> int:
        """Add a new trading signal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO signals (asset, signal_type, confidence_score, sentiment_score,
                               source_subreddit, post_count, reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset, signal_type, confidence_score, sentiment_score,
              source_subreddit, post_count, reasoning))

        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return signal_id

    def add_paper_trade(self, signal_id: int, asset: str, trade_type: str,
                       entry_price: float, position_size: float = 1000.0) -> int:
        """Add a new paper trade."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO paper_trades (signal_id, asset, trade_type, entry_price, position_size)
            VALUES (?, ?, ?, ?, ?)
        """, (signal_id, asset, trade_type, entry_price, position_size))

        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return trade_id

    def close_paper_trade(self, trade_id: int, exit_price: float):
        """Close a paper trade and calculate PnL."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get trade details
        cursor.execute("SELECT entry_price, position_size, trade_type FROM paper_trades WHERE id = ?", (trade_id,))
        result = cursor.fetchone()

        if result:
            entry_price, position_size, trade_type = result

            # Calculate PnL
            if trade_type.upper() == 'BUY':
                pnl = (exit_price - entry_price) / entry_price * position_size
            else:  # SELL/SHORT
                pnl = (entry_price - exit_price) / entry_price * position_size

            cursor.execute("""
                UPDATE paper_trades
                SET exit_price = ?, pnl = ?, status = 'closed', closed_at = ?
                WHERE id = ?
            """, (exit_price, pnl, datetime.now(), trade_id))

            conn.commit()

        conn.close()

    def add_analyzed_post(self, post_id: str, subreddit: str, title: str,
                         content: str, sentiment: str, sentiment_score: float,
                         mentioned_assets: str, url: str = None):
        """Add an analyzed post to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO analyzed_posts (post_id, subreddit, title, content,
                                          sentiment, sentiment_score, mentioned_assets, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (post_id, subreddit, title, content, sentiment, sentiment_score,
                  mentioned_assets, url))
            conn.commit()
        except sqlite3.IntegrityError:
            # Post already exists
            pass

        conn.close()

    def get_recent_signals(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent trading signals."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM signals
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        signals = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return signals

    def get_recent_trades(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent paper trades."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM paper_trades
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return trades

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total signals
        cursor.execute("SELECT COUNT(*) FROM signals")
        total_signals = cursor.fetchone()[0]

        # Total trades
        cursor.execute("SELECT COUNT(*) FROM paper_trades")
        total_trades = cursor.fetchone()[0]

        # Open trades
        cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE status = 'open'")
        open_trades = cursor.fetchone()[0]

        # Closed trades stats
        cursor.execute("""
            SELECT
                COUNT(*) as closed_count,
                COALESCE(SUM(pnl), 0) as total_pnl,
                COALESCE(AVG(pnl), 0) as avg_pnl,
                COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades
            FROM paper_trades
            WHERE status = 'closed'
        """)

        closed_stats = cursor.fetchone()

        # Recent posts analyzed
        cursor.execute("SELECT COUNT(*) FROM analyzed_posts WHERE timestamp > datetime('now', '-24 hours')")
        posts_24h = cursor.fetchone()[0]

        conn.close()

        return {
            'total_signals': total_signals,
            'total_trades': total_trades,
            'open_trades': open_trades,
            'closed_trades': closed_stats[0] if closed_stats else 0,
            'total_pnl': closed_stats[1] if closed_stats else 0,
            'avg_pnl': closed_stats[2] if closed_stats else 0,
            'winning_trades': closed_stats[3] if closed_stats else 0,
            'win_rate': (closed_stats[3] / closed_stats[0] * 100) if closed_stats and closed_stats[0] > 0 else 0,
            'posts_analyzed_24h': posts_24h
        }

    def get_recent_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recently analyzed posts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM analyzed_posts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return posts
