"""
State Manager Service
Tracks portfolio state, balances, and allocation
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


class StateManager:
    """Manages portfolio state and allocation tracking."""
    
    def __init__(self, initial_capital: float = 10000, logger = None, state_file: str = "data/portfolio_state.json"):
        """
        Initialize state manager.
        
        Args:
            initial_capital: Starting capital amount
            logger: Logger instance for logging
            state_file: Path to state file
        """
        self.initial_capital = initial_capital
        self.logger = logger
        self.state_file = state_file
        self.state = self._load_state()
        
        # Initialize capital if not set
        if self.state.get("conservative_value", 0) == 0 and self.state.get("aggressive_value", 0) == 0:
            # Default 70/30 allocation
            self.state["conservative_value"] = initial_capital * 0.70
            self.state["aggressive_value"] = initial_capital * 0.30
            self.state["baseline_aggressive"] = initial_capital * 0.30
            self.save()
    
    def _load_state(self) -> Dict:
        """Load state from file or create new state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default state
        return {
            "conservative_value": 0,
            "aggressive_value": 0,
            "last_rebalance": None,
            "last_skim": None,
            "baseline_aggressive": 0,
            "positions": {},  # Track positions: {coin: {size, entry_price, entry_time}}
            "trades": []  # Trade history
        }
    
    def save(self):
        """Save state to file."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save state: {e}")
    
    def update(self):
        """Update portfolio state (called each cycle)."""
        # This would typically fetch current prices and update values
        # For now, just ensure state is current
        pass
    
    def log_snapshot(self):
        """Log a portfolio snapshot."""
        if self.logger:
            self.logger.log_snapshot(
                conservative_value=self.get_conservative_value(),
                aggressive_value=self.get_aggressive_value(),
                total_value=self.get_total_value(),
                allocation_pct=self.get_allocation_percent(),
                pnl_conservative=0,  # Would calculate from trades
                pnl_aggressive=0,
                rebalance_due_in_days=self.days_until_rebalance(),
                last_skim_date=self.state.get("last_skim")
            )
    
    def update_conservative_value(self, value: float):
        """Update conservative portfolio value."""
        self.state["conservative_value"] = value
        self.save()
    
    def update_aggressive_value(self, value: float):
        """Update aggressive portfolio value."""
        self.state["aggressive_value"] = value
        self.save()
    
    def get_conservative_value(self) -> float:
        """Get conservative portfolio value."""
        return self.state.get("conservative_value", 0)
    
    def get_aggressive_value(self) -> float:
        """Get aggressive portfolio value."""
        return self.state.get("aggressive_value", 0)
    
    def get_total_value(self) -> float:
        """Get total portfolio value."""
        return self.get_conservative_value() + self.get_aggressive_value()
    
    def get_allocation_percent(self) -> float:
        """Get current conservative allocation percentage."""
        total = self.get_total_value()
        if total == 0:
            return 0.70  # Default
        return self.get_conservative_value() / total
    
    def days_until_rebalance(self) -> int:
        """Calculate days until next quarterly rebalance."""
        last_rebalance = self.state.get("last_rebalance")
        if not last_rebalance:
            return 0  # Rebalance due
        
        try:
            last_date = datetime.fromisoformat(last_rebalance)
            days_since = (datetime.now() - last_date).days
            return max(0, 90 - days_since)  # Quarterly = 90 days
        except:
            return 0
    
    def should_rebalance(self) -> bool:
        """Check if quarterly rebalance is due."""
        return self.days_until_rebalance() == 0
    
    def should_skim(self) -> bool:
        """Check if profit skimming is triggered."""
        baseline = self.state.get("baseline_aggressive", 0)
        if baseline == 0:
            return False
        
        current = self.get_aggressive_value()
        # Skim if aggressive is 140% of baseline
        return current >= (baseline * 1.40)
    
    def record_rebalance(self):
        """Record that rebalancing occurred."""
        self.state["last_rebalance"] = datetime.now().isoformat()
        self.save()
    
    def record_skim(self):
        """Record that skimming occurred."""
        self.state["last_skim"] = datetime.now().isoformat()
        self.save()
    
    def execute_paper_trade(self, coin: str, action: str, price: float, amount_usd: float):
        """
        Execute a paper trade (simulation).
        
        Args:
            coin: Trading pair (e.g., "BTC-USD")
            action: "BUY" or "SELL"
            price: Execution price
            amount_usd: Trade amount in USD
        """
        positions = self.state.get("positions", {})
        
        if action.upper() == "BUY":
            # Calculate size
            size = amount_usd / price
            
            # Add to position
            if coin in positions:
                # Average into existing position
                existing = positions[coin]
                total_size = existing["size"] + size
                total_cost = (existing["size"] * existing["entry_price"]) + amount_usd
                positions[coin] = {
                    "size": total_size,
                    "entry_price": total_cost / total_size,
                    "entry_time": existing["entry_time"]
                }
            else:
                positions[coin] = {
                    "size": size,
                    "entry_price": price,
                    "entry_time": datetime.now().isoformat()
                }
        
        elif action.upper() == "SELL":
            if coin in positions:
                # Calculate P&L
                entry_price = positions[coin]["entry_price"]
                size = positions[coin]["size"]
                pnl = (price - entry_price) * size
                
                # Log the trade
                if self.logger:
                    self.logger.log_trade(
                        strategy="paper",
                        coin=coin,
                        action="SELL",
                        price=price,
                        quantity=size,
                        pnl=pnl,
                        trigger_reason="paper_trade"
                    )
                
                # Remove position
                del positions[coin]
        
        self.state["positions"] = positions
        self.save()
    
    def execute_live_trade(self, coin: str, action: str, price: float, amount_usd: float, fee_usd: float = 0):
        """
        Record a live trade execution.
        
        Args:
            coin: Trading pair (e.g., "BTC-USD")
            action: "BUY" or "SELL"
            price: Execution price
            amount_usd: Trade amount in USD
            fee_usd: Trading fee in USD
        """
        positions = self.state.get("positions", {})
        
        if action.upper() == "BUY":
            size = amount_usd / price
            
            if coin in positions:
                existing = positions[coin]
                total_size = existing["size"] + size
                total_cost = (existing["size"] * existing["entry_price"]) + amount_usd
                positions[coin] = {
                    "size": total_size,
                    "entry_price": total_cost / total_size,
                    "entry_time": existing["entry_time"]
                }
            else:
                positions[coin] = {
                    "size": size,
                    "entry_price": price,
                    "entry_time": datetime.now().isoformat()
                }
            
            if self.logger:
                self.logger.log_trade(
                    strategy="live",
                    coin=coin,
                    action="BUY",
                    price=price,
                    quantity=size,
                    pnl=0,
                    trigger_reason="live_trade",
                    fee_usd=fee_usd
                )
        
        elif action.upper() == "SELL":
            if coin in positions:
                entry_price = positions[coin]["entry_price"]
                size = positions[coin]["size"]
                pnl = (price - entry_price) * size - fee_usd
                
                if self.logger:
                    self.logger.log_trade(
                        strategy="live",
                        coin=coin,
                        action="SELL",
                        price=price,
                        quantity=size,
                        pnl=pnl,
                        trigger_reason="live_trade",
                        fee_usd=fee_usd
                    )
                
                del positions[coin]
        
        self.state["positions"] = positions
        self.save()
    
    def get_position(self, coin: str) -> Optional[Dict]:
        """Get current position for a coin."""
        return self.state.get("positions", {}).get(coin)
    
    def get_all_positions(self) -> Dict:
        """Get all current positions."""
        return self.state.get("positions", {})
