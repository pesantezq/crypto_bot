"""
Conservative Strategy - BTC-USD, ETH-USD
Lower risk, higher allocation (70%)
"""

import json
from pathlib import Path
from services.indicators import Indicators


class ConservativeStrategy:
    """Conservative trading strategy"""
    
    def __init__(self, logger, price_api):
        """Initialize strategy"""
        self.logger = logger
        self.price_api = price_api
        
        # Load settings
        with open(Path("config") / "settings_conservative.json", 'r') as f:
            self.settings = json.load(f)
        
        self.coins = self.settings['coins']
        self.indicators = Indicators()
        
    def evaluate_all(self):
        """Evaluate all coins and return signals"""
        signals = []
        
        for coin in self.coins:
            signal = self.evaluate(coin)
            signals.append(signal)
        
        return signals
    
    def evaluate(self, coin):
        """Evaluate a single coin"""
        # Get current price
        price = self.price_api.get_price(coin)
        
        if not price:
            return self._hold_signal(coin, 0)
        
        # For demo purposes, generate hold signal
        # Real implementation would:
        # 1. Fetch historical prices
        # 2. Calculate RSI, EMA
        # 3. Check all buy/sell triggers
        # 4. Return appropriate signal
        
        signal = {
            'coin': coin,
            'action': 'HOLD',
            'price': price,
            'amount_usd': 0,
            'rsi': 50,
            'ema_fast': price,
            'ema_slow': price,
            'atr': 0,
            'volume': 0,
            'reason': 'Demo mode - no trades'
        }
        
        # Log signal
        self.logger.log_signal(
            strategy='conservative',
            coin=coin,
            signal=signal['action'],
            rsi=signal['rsi'],
            ema_fast=signal['ema_fast'],
            ema_slow=signal['ema_slow'],
            atr=signal['atr'],
            price=price,
            volume=signal['volume'],
            trigger_met=False,
            blocked_reason="demo_mode"
        )
        
        return signal
    
    def _hold_signal(self, coin, price):
        """Generate hold signal"""
        return {
            'coin': coin,
            'action': 'HOLD',
            'price': price,
            'amount_usd': 0,
            'reason': 'No triggers met'
        }
