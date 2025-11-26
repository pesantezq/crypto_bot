"""
State Manager - Portfolio state persistence
Handles portfolio tracking, trade execution, and state persistence
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone


class StateManager:
    """Manage portfolio state"""
    
    def __init__(self, initial_capital=10000, logger=None):
        """Initialize state manager"""
        self.logger = logger
        self.state_file = Path("data") / "portfolio_state.json"
        
        # Load or create state
        if self.state_file.exists():
            self.load()
        else:
            self.state = {
                'initial_capital': initial_capital,
                'cash': initial_capital,
                'positions': {},
                'conservative_value': initial_capital * 0.70,
                'aggressive_value': initial_capital * 0.30,
                'total_trades': 0,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            self.save()
    
    def load(self):
        """Load state from file"""
        with open(self.state_file, 'r') as f:
            self.state = json.load(f)
    
    def save(self):
        """Save state to file"""
        self.state['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # Atomic write: write to temp file, then rename
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        
        # Replace old file
        temp_file.replace(self.state_file)
    
    def update(self):
        """Update portfolio values"""
        # This would fetch current prices and recalculate portfolio value
        pass
    
    def execute_paper_trade(self, coin, action, price, amount_usd):
        """Execute a simulated paper trade"""
        if action == 'BUY':
            # Deduct from cash
            if self.state['cash'] >= amount_usd:
                self.state['cash'] -= amount_usd
                quantity = amount_usd / price
                
                # Add to positions
                if coin not in self.state['positions']:
                    self.state['positions'][coin] = {'quantity': 0, 'avg_price': 0}
                
                pos = self.state['positions'][coin]
                total_cost = (pos['quantity'] * pos['avg_price']) + amount_usd
                pos['quantity'] += quantity
                pos['avg_price'] = total_cost / pos['quantity']
                
                self.state['total_trades'] += 1
                
        elif action == 'SELL':
            # Add to cash
            if coin in self.state['positions']:
                pos = self.state['positions'][coin]
                quantity = amount_usd / price
                
                if pos['quantity'] >= quantity:
                    self.state['cash'] += amount_usd
                    pos['quantity'] -= quantity
                    
                    if pos['quantity'] < 0.0001:  # Clean up tiny positions
                        del self.state['positions'][coin]
                    
                    self.state['total_trades'] += 1
        
        self.save()
    
    def execute_live_trade(self, coin, action, price, amount_usd, fee_usd):
        """Execute a real live trade"""
        # Similar to paper trade but includes fees
        if action == 'BUY':
            total_cost = amount_usd + fee_usd
            if self.state['cash'] >= total_cost:
                self.state['cash'] -= total_cost
                quantity = amount_usd / price
                
                if coin not in self.state['positions']:
                    self.state['positions'][coin] = {'quantity': 0, 'avg_price': 0}
                
                pos = self.state['positions'][coin]
                total_investment = (pos['quantity'] * pos['avg_price']) + amount_usd + fee_usd
                pos['quantity'] += quantity
                pos['avg_price'] = total_investment / pos['quantity']
                
                self.state['total_trades'] += 1
                
        elif action == 'SELL':
            if coin in self.state['positions']:
                pos = self.state['positions'][coin]
                quantity = amount_usd / price
                
                if pos['quantity'] >= quantity:
                    self.state['cash'] += (amount_usd - fee_usd)
                    pos['quantity'] -= quantity
                    
                    if pos['quantity'] < 0.0001:
                        del self.state['positions'][coin]
                    
                    self.state['total_trades'] += 1
        
        self.save()
    
    def get_total_value(self):
        """Get total portfolio value"""
        # Simplified - would need current prices
        return self.state['cash']
    
    def log_snapshot(self):
        """Log current portfolio snapshot"""
        if self.logger:
            self.logger.log_snapshot(
                conservative_value=self.state.get('conservative_value', 0),
                aggressive_value=self.state.get('aggressive_value', 0),
                total_value=self.get_total_value(),
                allocation_pct=0,
                pnl_conservative=0,
                pnl_aggressive=0,
                rebalance_due_in_days=90
            )
