"""
Risk Manager - Risk controls and position sizing
"""

from datetime import datetime, timezone, timedelta


class RiskManager:
    """Manage trading risk"""
    
    def __init__(self, max_daily_loss, max_total_loss, max_position_size, logger=None):
        """Initialize risk manager"""
        self.max_daily_loss = max_daily_loss
        self.max_total_loss = max_total_loss
        self.max_position_size = max_position_size
        self.logger = logger
        
        # Track losses
        self.daily_loss = 0
        self.total_loss = 0
        self.last_reset_date = datetime.now(timezone.utc).date()
        
        # Track trades per coin
        self.last_trade_time = {}
        self.min_trade_interval = timedelta(minutes=5)
        
    def can_trade(self, coin, amount_usd):
        """Check if trade is allowed"""
        # Reset daily loss at UTC midnight
        today = datetime.now(timezone.utc).date()
        if today > self.last_reset_date:
            self.daily_loss = 0
            self.last_reset_date = today
        
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            if self.logger:
                self.logger.warning(f"Daily loss limit reached: ${self.daily_loss:.2f}")
            return False
        
        # Check total loss limit
        if self.total_loss >= self.max_total_loss:
            if self.logger:
                self.logger.error(f"Total loss limit reached: ${self.total_loss:.2f}")
            return False
        
        # Check position size
        if amount_usd > self.max_position_size:
            if self.logger:
                self.logger.warning(f"Position size ${amount_usd:.2f} exceeds max ${self.max_position_size:.2f}")
            return False
        
        # Check min interval between trades on same coin
        now = datetime.now(timezone.utc)
        if coin in self.last_trade_time:
            elapsed = now - self.last_trade_time[coin]
            if elapsed < self.min_trade_interval:
                if self.logger:
                    self.logger.info(f"Trade on {coin} too soon (wait {self.min_trade_interval.seconds}s)")
                return False
        
        return True
    
    def record_trade(self, coin, pnl):
        """Record trade result for risk tracking"""
        if pnl < 0:
            self.daily_loss += abs(pnl)
            self.total_loss += abs(pnl)
        
        # Update last trade time
        self.last_trade_time[coin] = datetime.now(timezone.utc)
    
    def get_position_size(self, allocation_value, available_cash):
        """Calculate position size for trade"""
        # Max 10% of allocation per trade
        max_from_allocation = allocation_value * 0.10
        
        # Cap at max position size
        size = min(
            max_from_allocation,
            self.max_position_size,
            available_cash
        )
        
        return max(size, 5)  # Minimum $5 trade
