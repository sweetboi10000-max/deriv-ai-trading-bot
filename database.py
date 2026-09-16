import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    """SQLite database for storing trades and bot statistics"""
    
    def __init__(self, db_path: str = 'trading_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE,
                    symbol TEXT NOT NULL,
                    contract_type TEXT,
                    entry_time TIMESTAMP,
                    exit_time TIMESTAMP,
                    stake REAL,
                    profit_loss REAL,
                    status TEXT,
                    win_probability REAL,
                    signal TEXT,
                    notes TEXT
                )
            ''')
            
            # Account balance history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    balance REAL,
                    daily_trades INTEGER,
                    daily_profit_loss REAL
                )
            ''')
            
            # Bot statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    win_rate REAL,
                    current_balance REAL,
                    total_profit_loss REAL,
                    recovery_trades INTEGER,
                    loss_streak INTEGER,
                    win_streak INTEGER
                )
            ''')
            
            # Predictions history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    symbol TEXT,
                    direction TEXT,
                    probability REAL,
                    confidence REAL,
                    signal TEXT,
                    accuracy BOOLEAN
                )
            ''')
            
            # Bot sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT,
                    total_trades INTEGER,
                    total_profit_loss REAL,
                    notes TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def add_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Add a trade record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades 
                (trade_id, symbol, contract_type, entry_time, stake, win_probability, signal, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('trade_id'),
                trade_data.get('symbol'),
                trade_data.get('contract_type'),
                datetime.now().isoformat(),
                trade_data.get('stake'),
                trade_data.get('win_probability'),
                trade_data.get('signal'),
                'OPEN'
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Trade recorded: {trade_data.get('trade_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Add trade error: {e}")
            return False
    
    def close_trade(self, trade_id: str, profit_loss: float, status: str = 'CLOSED') -> bool:
        """Close a trade and record result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trades 
                SET exit_time = ?, profit_loss = ?, status = ?
                WHERE trade_id = ?
            ''', (datetime.now().isoformat(), profit_loss, status, trade_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Trade closed: {trade_id} - P/L: ${profit_loss:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Close trade error: {e}")
            return False
    
    def record_prediction(self, prediction: Dict[str, Any]) -> bool:
        """Record AI prediction"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictions 
                (timestamp, symbol, direction, probability, confidence, signal)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                prediction.get('symbol'),
                prediction.get('direction'),
                prediction.get('probability'),
                prediction.get('confidence'),
                prediction.get('signal')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Record prediction error: {e}")
            return False
    
    def record_balance(self, balance: float, daily_trades: int, daily_pl: float) -> bool:
        """Record balance snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO balance_history (timestamp, balance, daily_trades, daily_profit_loss)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), balance, daily_trades, daily_pl))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Record balance error: {e}")
            return False
    
    def record_session_stats(self, stats: Dict[str, Any]) -> bool:
        """Record bot session statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bot_stats 
                (timestamp, total_trades, winning_trades, losing_trades, win_rate, current_balance, 
                 total_profit_loss, recovery_trades, loss_streak, win_streak)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                stats.get('total_trades'),
                stats.get('winning_trades'),
                stats.get('losing_trades'),
                stats.get('win_rate_percent'),
                stats.get('current_balance'),
                stats.get('balance_change'),
                stats.get('recovery_trades'),
                stats.get('loss_streak'),
                stats.get('win_streak')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Record stats error: {e}")
            return False
    
    def get_trade_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve trade history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades ORDER BY id DESC LIMIT ?
            ''', (limit,))
            
            trades = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return trades
            
        except Exception as e:
            logger.error(f"Get trade history error: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get trade stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN profit_loss <= 0 THEN 1 ELSE 0 END) as losses,
                    SUM(profit_loss) as total_pl
                FROM trades WHERE status = 'CLOSED'
            ''')
            
            stats = cursor.fetchone()
            conn.close()
            
            total = stats[0] if stats[0] else 0
            wins = stats[1] if stats[1] else 0
            losses = stats[2] if stats[2] else 0
            total_pl = stats[3] if stats[3] else 0
            
            win_rate = (wins / total * 100) if total > 0 else 0
            
            return {
                'total_trades': total,
                'winning_trades': wins,
                'losing_trades': losses,
                'win_rate': win_rate,
                'total_profit_loss': total_pl
            }
            
        except Exception as e:
            logger.error(f"Get statistics error: {e}")
            return {}
    
    def clear_old_records(self, days: int = 30) -> bool:
        """Clear records older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now().timestamp() - (days * 86400)
            
            cursor.execute('DELETE FROM trades WHERE datetime(entry_time) < datetime(?, "unixepoch")', (cutoff_date,))
            cursor.execute('DELETE FROM predictions WHERE datetime(timestamp) < datetime(?, "unixepoch")', (cutoff_date,))
            cursor.execute('DELETE FROM balance_history WHERE datetime(timestamp) < datetime(?, "unixepoch")', (cutoff_date,))
            
            conn.commit()
            conn.close()
            logger.info(f"Cleared records older than {days} days")
            return True
            
        except Exception as e:
            logger.error(f"Clear old records error: {e}")
            return False
