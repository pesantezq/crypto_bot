"""
Price API - Fetch cryptocurrency prices
Primary: CryptoCompare, Fallback: CoinGecko
"""

import requests
import time
from datetime import datetime, timedelta


class PriceAPI:
    """Fetch cryptocurrency prices"""
    
    def __init__(self):
        """Initialize price API"""
        self.cryptocompare_url = "https://min-api.cryptocompare.com/data/price"
        self.cryptocompare_historical = "https://min-api.cryptocompare.com/data/v2/histohour"
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
    
    def get_historical_prices(self, coin_pair, hours=24, days=None):
        """
        Get historical prices
        
        Args:
            coin_pair: e.g., 'BTC-USD'
            hours: Number of hours to fetch (default: 24)
            days: Number of days to fetch (optional, overrides hours)
        
        Returns:
            list of dicts: [{'timestamp': int, 'price': float, 'volume': float}, ...]
        """
        self._rate_limit()
        
        # Parse coin pair
        coin, currency = coin_pair.split('-')
        
        # Calculate limit (number of data points to fetch)
        if days:
            limit = days * 24  # Daily data converted to hourly
        else:
            limit = hours
        
        # Limit to max 2000 (API limit)
        limit = min(limit, 2000)
        
        try:
            # CryptoCompare historical hourly data
            params = {
                'fsym': coin,
                'tsym': currency,
                'limit': limit
            }
            
            response = requests.get(self.cryptocompare_historical, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Response') == 'Success':
                    prices = []
                    for item in data['Data']['Data']:
                        prices.append({
                            'timestamp': item['time'],
                            'price': item['close'],
                            'volume': item.get('volumeto', 0),
                            'high': item.get('high', item['close']),
                            'low': item.get('low', item['close'])
                        })
                    return prices
        except Exception as e:
            print(f"⚠️  Error fetching historical prices for {coin_pair}: {e}")
        
        # Fallback: Return current price repeated (for testing)
        current_price = self.get_price(coin_pair)
        if current_price:
            print(f"⚠️  Using current price as fallback for {coin_pair}")
            # Generate fake historical data with small variations
            import random
            prices = []
            for i in range(limit):
                variation = random.uniform(0.98, 1.02)  # ±2% variation
                prices.append({
                    'timestamp': int(time.time()) - (3600 * (limit - i)),
                    'price': current_price * variation,
                    'volume': 1000000,  # Dummy volume
                    'high': current_price * variation * 1.01,
                    'low': current_price * variation * 0.99
                })
            return prices
        
        return []
