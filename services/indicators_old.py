"""
Technical Indicators - RSI, EMA, ATR, Volume analysis
"""

import numpy as np


class Indicators:
    """Calculate technical indicators"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50  # Neutral if insufficient data
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_ema(prices, period):
        """Calculate EMA (Exponential Moving Average)"""
        if len(prices) < period:
            return np.mean(prices)  # Use SMA if insufficient data
        
        multiplier = 2 / (period + 1)
        ema = prices[0]  # Start with first price
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def calculate_atr(high_prices, low_prices, close_prices, period=14):
        """Calculate ATR (Average True Range)"""
        if len(close_prices) < period + 1:
            return 0
        
        tr_list = []
        for i in range(1, len(close_prices)):
            tr = max(
                high_prices[i] - low_prices[i],
                abs(high_prices[i] - close_prices[i-1]),
                abs(low_prices[i] - close_prices[i-1])
            )
            tr_list.append(tr)
        
        atr = np.mean(tr_list[-period:])
        return atr
    
    @staticmethod
    def detect_breakout(prices, window=20):
        """Detect price breakout above window high"""
        if len(prices) < window + 1:
            return False
        
        current_price = prices[-1]
        window_high = max(prices[-window-1:-1])
        
        return current_price > window_high
    
    @staticmethod
    def calculate_volume_ratio(volumes, period=20):
        """Calculate current volume vs average volume"""
        if len(volumes) < period + 1:
            return 1.0
        
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[-period-1:-1])
        
        if avg_volume == 0:
            return 1.0
        
        return current_volume / avg_volume
