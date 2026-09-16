import logging
from typing import Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class RiskManager:
    """Low-risk money management and position sizing"""
    
    def __init__(self, initial_balance: float, config: Dict[str, Any]):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.config = config
        
        # Position management
        self.current_stake = config.get('INITIAL_STAKE', 10)
        self.loss_streak = 0
        self.win_streak = 0
        self.daily_loss = 0
        self.trades_today = []
        
        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.recovery_trades = 0
        
    def calculate_stake(self) -> float:
        """Calculate stake for next trade (with recovery multiplier on losses)"""
        
        # If on a loss streak, apply recovery multiplier (X2)
        if self.loss_streak > 0:
            recovery_stake = self.current_stake * (self.config.get('RECOVERY_MULTIPLIER', 2.0) ** self.loss_streak)
            recovery_stake = min(recovery_stake, self.config.get('MAX_STAKE', 500))
            return recovery_stake
        
        # Reset to initial stake after win streak
        return self.config.get('INITIAL_STAKE', 10)
    
    def can_trade(self, win_probability: float) -> Dict[str, Any]:
        """Check if trade should be executed based on risk parameters"""
        
        min_prob = self.config.get('MIN_WIN_PROBABILITY', 0.70)
        max_prob = self.config.get('MAX_WIN_PROBABILITY', 0.80)
        
        reasons = []
        
        # Check win probability threshold
        if win_probability < min_prob or win_probability > max_prob:
            reasons.append(f"Win probability {win_probability:.2%} outside range [{min_prob:.0%}, {max_prob:.0%}]")
        
        # Check daily loss limit
        if self.daily_loss >= self.config.get('MAX_DAILY_LOSS', 500):
            reasons.append(f"Daily loss limit reached: ${self.daily_loss:.2f}")
        
        # Check loss streak limit
        if self.loss_streak >= self.config.get('MAX_LOSS_STREAK', 3):
            reasons.append(f"Max loss streak ({self.config.get('MAX_LOSS_STREAK', 3)}) reached")
        
        # Check max position size
        stake = self.calculate_stake()
        if stake > self.config.get('MAX_POSITION_SIZE', 1000):
            reasons.append(f"Calculated stake ${stake:.2f} exceeds max ${self.config.get('MAX_POSITION_SIZE', 1000):.2f}")
        
        # Check available balance
        if stake > self.current_balance * 0.1:  # Max 10% of balance per trade
            reasons.append(f"Stake ${stake:.2f} exceeds 10% of balance")
        
        # Check max trades per day
        if len(self.trades_today) >= self.config.get('MAX_TRADES_PER_DAY', 50):
            reasons.append(f"Max daily trades ({self.config.get('MAX_TRADES_PER_DAY', 50)}) reached")
        
        can_trade = len(reasons) == 0 and (min_prob <= win_probability <= max_prob)
        
        return {
            'can_trade': can_trade,
            'stake': self.calculate_stake() if can_trade else 0,
            'win_probability': win_probability,
            'reasons': reasons
        }
    
    def record_win(self, stake: float, profit: float):
        """Record a winning trade"""
        self.current_balance += profit
        self.winning_trades += 1
        self.total_trades += 1
        self.loss_streak = 0
        self.win_streak += 1
        self.current_stake = self.config.get('INITIAL_STAKE', 10)  # Reset to initial
        
        self.trades_today.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'WIN',
            'stake': stake,
            'profit': profit
        })
        
        logger.info(f"Trade WON - Stake: ${stake:.2f}, Profit: ${profit:.2f}, Balance: ${self.current_balance:.2f}")
    
    def record_loss(self, stake: float, loss: float):
        """Record a losing trade with recovery strategy"""
        self.current_balance -= loss
        self.losing_trades += 1
        self.total_trades += 1
        self.loss_streak += 1
        self.win_streak = 0
        self.daily_loss += loss
        
        if self.loss_streak > 1:
            self.recovery_trades += 1
        
        self.trades_today.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'LOSS',
            'stake': stake,
            'loss': loss
        })
        
        next_stake = self.calculate_stake()
        logger.warning(
            f"Trade LOST - Streak: {self.loss_streak}, Loss: ${loss:.2f}, "
            f"Next Stake (X{self.config.get('RECOVERY_MULTIPLIER', 2.0)}): ${next_stake:.2f}, "
            f"Balance: ${self.current_balance:.2f}"
        )
    
    def get_win_rate(self) -> float:
        """Calculate current win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive risk and performance statistics"""
        
        balance_change = self.current_balance - self.initial_balance
        balance_change_pct = (balance_change / self.initial_balance) * 100 if self.initial_balance > 0 else 0
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'balance_change': balance_change,
            'balance_change_percent': balance_change_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate_percent': self.get_win_rate(),
            'loss_streak': self.loss_streak,
            'win_streak': self.win_streak,
            'recovery_trades': self.recovery_trades,
            'daily_loss': self.daily_loss,
            'daily_loss_limit': self.config.get('MAX_DAILY_LOSS', 500),
            'current_stake': self.current_stake,
            'max_stake': self.config.get('MAX_STAKE', 500),
            'next_stake': self.calculate_stake()
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_loss = 0
        self.trades_today = []
        logger.info("Daily statistics reset")
    
    def get_risk_summary(self) -> str:
        """Get risk management summary"""
        stats = self.get_statistics()
        
        summary = f"""
        === RISK MANAGEMENT SUMMARY ===
        Balance: ${stats['current_balance']:.2f} ({stats['balance_change_percent']:+.2f}%)
        Trades: {stats['total_trades']} (Win: {stats['winning_trades']}, Loss: {stats['losing_trades']})
        Win Rate: {stats['win_rate_percent']:.2f}%
        Loss Streak: {stats['loss_streak']}
        Daily Loss: ${stats['daily_loss']:.2f} / ${stats['daily_loss_limit']:.2f}
        Next Stake: ${stats['next_stake']:.2f}
        ==============================
        """
        return summary
