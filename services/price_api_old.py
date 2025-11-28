"""
Price API - Fetch cryptocurrency prices
Primary: CryptoCompare, Fallback: CoinGecko
"""

import requests
import time


class PriceAPI:
    """Fetch cryptocurrency prices"""
    
    def __init__(self):
        """Initialize price API"""
        self.cryptocompare_url = "https://min-api.cryptocompare.com/data/price"
        self.coingecko_url = "https://api.coingecko.com/api/v3/simple/price"
        self.last_call_time = 0
        self.rate_limit_delay = 1  # seconds between calls
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_call_time = time.time()
        
    def get_price(self, coin_pair):
        """
        Get current price for a coin pair (e.g., 'BTC-USD')
        Returns: float price or None
        """
        self._rate_limit()
        
        # Parse coin pair
        coin, currency = coin_pair.split('-')
        
        # Try CryptoCompare first
        try:
            params = {
                'fsym': coin,
                'tsyms': currency
            }
            response = requests.get(self.cryptocompare_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return float(data.get(currency, 0))
        except:
            pass
        
        # Fallback to CoinGecko
        try:
            coin_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'SOL': 'solana',
                'AVAX': 'avalanche-2',
                'DOGE': 'dogecoin'
            }
            
            coingecko_id = coin_map.get(coin, coin.lower())
            params = {
                'ids': coingecko_id,
                'vs_currencies': currency.lower()
            }
            response = requests.get(self.coingecko_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return float(data.get(coingecko_id, {}).get(currency.lower(), 0))
        except:
            pass
        
        return None
    
    def get_historical_prices(self, coin_pair, days=90):
        """Get historical prices (for backtesting)"""
        # Simplified - in production, use cryptocompare historical API
        return []
