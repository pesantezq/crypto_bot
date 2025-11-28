"""
Conservative Trading Strategy
BTC and ETH with stable allocation (70%)
"""

import json
import os
from typing import Dict, Optional
from services.coinbase_api import CoinbaseAPI
from services.logger import Logger


class ConservativeStrategy:
    """Conservative strategy for BTC/ETH trading."""
    
    def __init__(self, paper_mode: bool = False, initial_capital: float = 1000, phase_config: Optional[Dict] = None):
        """
        Initialize conservative strategy.
        
        Args:
            paper_mode: If True, simulate trades
            initial_capital: Starting capital for this strategy
            phase_config: Phase configuration
        """
        self.paper_mode = paper_mode
        self.initial_capital = initial_capital
        self.phase_config = phase_config or {}
        
        # Load settings
        self.settings = self._load_settings()
        
        # Initialize services
        self.coinbase = CoinbaseAPI(paper_mode=paper_mode)
        self.logger = Logger()
        
        # Set paper balance if in paper mode
        if paper_mode:
            self.coinbase.set_paper_balance("USD", initial_capital)
        
        print(f"✅ Conservative Strategy initialized (${initial_capital:,.2f})")
    
    def _load_settings(self) -> Dict:
        """Load strategy settings from JSON."""
        settings_path = os.path.join('config', 'settings_conservative.json')
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default settings
        return {
            "strategy_version": "1.0",
            "coins": ["BTC-USD", "ETH-USD"],
            "rsi_buy": 30,
            "rsi_sell": 70,
            "dca_dip_percent": 2.5,
            "take_profit_percent": 8.0,
            "stop_loss_percent": 5.0
        }
    
    def execute(self):
        """Execute trading strategy."""
        print("\n📊 Running Conservative Strategy...")
        
        # Get coins to trade
        coins = self.settings.get("coins", ["BTC-USD", "ETH-USD"])
        
        for coin in coins:
            try:
                # Get current price
                price = self.coinbase.get_product_price(coin)
                if price:
                    print(f"   {coin}: ${price:,.2f}")
                
                # Strategy logic would go here
                # For now, just log the check
                
            except Exception as e:
                print(f"   ❌ Error checking {coin}: {e}")
        
        print("   ✅ Conservative strategy execution complete")
