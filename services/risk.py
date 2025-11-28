"""
Risk Manager Service
Manages risk limits and safety checks
"""

from typing import Dict, Optional
from datetime import datetime, date


class RiskManager:
    """Manages risk limits and trading safety."""
    
    def __init__(self, max_daily_loss: float = 100, max_total_loss: float = 200, 
                 max_position_size: float = 500, logger = None,
                 paper_mode: bool = False, phase_config: Optional[Dict] = None):
        """
        Initialize risk manager.
        
        Args:
            max_daily_loss: Maximum loss allowed per day in USD
            max_total_loss: Maximum total loss allowed in USD
            max_position_size: Maximum position size in USD
            logger: Logger instance for logging
            paper_mode: If True, relaxed safety checks
            phase_config: Phase configuration with risk limits (legacy)
        """
        self.logger = logger
        self.paper_mode = paper_mode
        
        # Use direct parameters or fall back to phase_config
        if phase_config:
            self.max_daily_loss = phase_config.get('max_daily_loss_usd', max_daily_loss)
            self.max_total_loss = phase_config.get('max_total_loss_usd', max_total_loss)
            self.max_position_size = phase_config.get('max_position_usd', max_position_size)
        else:
            self.max_daily_loss = max_daily_loss
            self.max_total_loss = max_total_loss
            self.max_position_size = max_position_size
        
        # Track losses
        self.daily_loss = 0.0
        self.total_loss = 0.0
        self.last_reset_date = date.today()
        
        # Track trades per coin
        self.daily_trades = {}  # {coin: count}
        self.max_daily_trades_per_coin = 5
    
    def can_trade(self, coin: str = None, amount_usd: float = 0) -> bool:
        """
        Check if trading is allowed based on risk limits.
        
        Args:
            coin: Trading pair (e.g., "BTC-USD")
            amount_usd: Proposed trade amount in USD
            
        Returns:
            True if trade is allowed
        """
        # Reset daily counters if new day
        self._check_daily_reset()
        
        if self.paper_mode:
            return True
        
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            self._log_blocked(coin, amount_usd, "daily_loss_limit")
            print(f"⚠️  Daily loss limit reached: ${self.daily_loss:.2f} / ${self.max_daily_loss:.2f}")
            return False
        
        # Check total loss limit
        if self.total_loss >= self.max_total_loss:
            self._log_blocked(coin, amount_usd, "total_loss_limit")
            print(f"⚠️  Total loss limit reached: ${self.total_loss:.2f} / ${self.max_total_loss:.2f}")
            return False
        
        # Check position size
        if amount_usd > self.max_position_size:
            self._log_blocked(coin, amount_usd, "position_size_limit")
            print(f"⚠️  Position too large: ${amount_usd:.2f} > ${self.max_position_size:.2f}")
            return False
        
        # Check daily trade count per coin
        if coin:
            trades_today = self.daily_trades.get(coin, 0)
            if trades_today >= self.max_daily_trades_per_coin:
                self._log_blocked(coin, amount_usd, "max_trades_per_coin")
                print(f"⚠️  Max daily trades for {coin}: {trades_today} / {self.max_daily_trades_per_coin}")
                return False
        
        return True
    
    def _check_daily_reset(self):
        """Reset daily counters if it's a new day."""
        today = date.today()
        if today > self.last_reset_date:
            self.daily_loss = 0.0
            self.daily_trades = {}
            self.last_reset_date = today
            if self.logger:
                self.logger.info("Daily risk counters reset")
    
    def _log_blocked(self, coin: str, amount_usd: float, reason: str):
        """Log a blocked trade."""
        if self.logger:
            self.logger.warning(f"Trade blocked for {coin} (${amount_usd:.2f}): {reason}")
    
    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit exceeded."""
        return self.daily_loss >= self.max_daily_loss
    
    def check_total_loss_limit(self) -> bool:
        """Check if total loss limit exceeded."""
        return self.total_loss >= self.max_total_loss
    
    def record_trade(self, coin: str):
        """Record a trade for rate limiting."""
        self._check_daily_reset()
        self.daily_trades[coin] = self.daily_trades.get(coin, 0) + 1
    
    def record_loss(self, amount: float):
        """
        Record a loss.
        
        Args:
            amount: Loss amount (positive number)
        """
        self.daily_loss += abs(amount)
        self.total_loss += abs(amount)
        
        if self.logger:
            self.logger.warning(f"Loss recorded: ${amount:.2f} (Daily: ${self.daily_loss:.2f}, Total: ${self.total_loss:.2f})")
    
    def record_profit(self, amount: float):
        """
        Record a profit (reduces total loss tracker).
        
        Args:
            amount: Profit amount (positive number)
        """
        # Profits can offset total loss but not below zero
        self.total_loss = max(0, self.total_loss - abs(amount))
    
    def reset_daily_loss(self):
        """Reset daily loss counter (call at start of new day)."""
        self.daily_loss = 0
        self.daily_trades = {}
    
    def reset_all(self):
        """Reset all loss counters."""
        self.daily_loss = 0
        self.total_loss = 0
        self.daily_trades = {}
    
    def is_critical_error(self, error: Exception) -> bool:
        """
        Determine if an error is critical enough to stop trading.
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if trading should stop
        """
        critical_errors = [
            "insufficient funds",
            "invalid api key",
            "rate limit",
            "authentication failed",
            "account suspended"
        ]
        
        error_str = str(error).lower()
        return any(critical in error_str for critical in critical_errors)
    
    def can_enter_position(self, position_size_usd: float) -> bool:
        """
        Check if a position size is within limits.
        
        Args:
            position_size_usd: Proposed position size in USD
            
        Returns:
            True if position size is allowed
        """
        if position_size_usd > self.max_position_size:
            print(f"⚠️  Position too large: ${position_size_usd:.2f} > ${self.max_position_size:.2f}")
            return False
        return True
    
    def get_status(self) -> Dict:
        """Get current risk status."""
        return {
            "daily_loss": self.daily_loss,
            "max_daily_loss": self.max_daily_loss,
            "daily_loss_pct": (self.daily_loss / self.max_daily_loss * 100) if self.max_daily_loss > 0 else 0,
            "total_loss": self.total_loss,
            "max_total_loss": self.max_total_loss,
            "total_loss_pct": (self.total_loss / self.max_total_loss * 100) if self.max_total_loss > 0 else 0,
            "max_position_size": self.max_position_size,
            "daily_trades": self.daily_trades,
            "can_trade": self.can_trade()
        }
