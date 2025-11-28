"""
Technical Indicators - RSI, EMA, ATR, Volume analysis
Updated with full breakout detection and simplified ATR
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
    def calculate_atr(prices, period=14):
        """
        Calculate ATR (Average True Range) - Simplified version
        Uses price ranges as approximation when OHLC data not available
        
        Args:
            prices: List of closing prices
            period: Lookback period (default: 14)
        
        Returns:
            float: ATR value
        """
        if len(prices) < period + 1:
            return 0
        
        # Calculate true ranges using price differences
        tr_list = []
        for i in range(1, len(prices)):
            # Simplified TR: just use absolute price changes
            tr = abs(prices[i] - prices[i-1])
            tr_list.append(tr)
        
        # Average True Range
        atr = np.mean(tr_list[-period:])
        return atr
    
    @staticmethod
    def detect_breakout(prices, window=20, min_percent=0.5):
        """
        Detect price breakout above window high
        
        Args:
            prices: List of historical prices
            window: Lookback window for high detection (default: 20)
            min_percent: Minimum percent above high to qualify (default: 0.5%)
        
        Returns:
            dict: {
                'is_breakout': bool,
                'current_price': float,
                'window_high': float,
                'percent_above': float
            }
        """
        if len(prices) < window + 1:
            return {
                'is_breakout': False,
                'current_price': 0,
                'window_high': 0,
                'percent_above': 0
            }
        
        current_price = prices[-1]
        window_high = max(prices[-window-1:-1])
        
        if window_high == 0:
            return {
                'is_breakout': False,
                'current_price': current_price,
                'window_high': 0,
                'percent_above': 0
            }
        
        percent_above = ((current_price - window_high) / window_high) * 100
        is_breakout = percent_above >= min_percent
        
        return {
            'is_breakout': is_breakout,
            'current_price': current_price,
            'window_high': window_high,
            'percent_above': percent_above
        }
    
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
