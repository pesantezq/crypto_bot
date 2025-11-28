"""
Coinbase Advanced Trade API - Complete Implementation
Supports ECDSA authentication and real order execution
⚠️  THIS EXECUTES REAL TRADES WITH REAL MONEY
"""

import requests
import time
import json
import uuid
from datetime import datetime
from pathlib import Path


class CoinbaseAPI:
    """Coinbase Advanced Trade API wrapper"""
    
    def __init__(self, sandbox=False):
        """Initialize Coinbase API"""
        self.sandbox = sandbox
        
        # Coinbase Advanced Trade API
        self.base_url = "https://api.coinbase.com"
        
        # Credentials
        self.key_name = ""
        self.private_key = ""
        self.auth_type = None
        
        self._load_credentials()
        
    def _load_credentials(self):
        """Load ECDSA credentials from config"""
        try:
            creds_file = Path("config/credentials.json")
            
            if not creds_file.exists():
                print("⚠️  No credentials file found")
                return
            
            with open(creds_file, 'r') as f:
                creds = json.load(f)
            
            if 'coinbase' not in creds:
                print("⚠️  No coinbase section in credentials")
                return
            
            coinbase_creds = creds['coinbase']
            
            # Check for ECDSA credentials
            if 'key_name' in coinbase_creds and 'private_key' in coinbase_creds:
                self.key_name = coinbase_creds['key_name']
                self.private_key = coinbase_creds['private_key']
                self.auth_type = 'ecdsa'
                print("✓ ECDSA credentials loaded")
            else:
                print("⚠️  ECDSA credentials not found")
                print("   Need: key_name and private_key")
                
        except Exception as e:
            print(f"⚠️  Error loading credentials: {str(e)}")
            self.auth_type = None
    
    def _generate_jwt_token(self, request_method, request_path):
        """
        Generate JWT token for Coinbase Advanced Trade API
        Uses ECDSA (ES256) signature
        """
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            import jwt
            
            # Load private key
            if self.private_key.startswith('-----BEGIN'):
                # PEM format
                private_key_obj = serialization.load_pem_private_key(
                    self.private_key.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            else:
                print("⚠️  Private key must be in PEM format")
                return None
            
            # Create JWT payload
            timestamp = int(time.time())
            
            # URI for the request
            uri = f"{request_method} {request_path}"
            
            payload = {
                'sub': self.key_name,
                'iss': 'coinbase-cloud',
                'nbf': timestamp,
                'exp': timestamp + 120,  # Valid for 2 minutes
                'uri': uri
            }
            
            # Generate JWT token
            token = jwt.encode(
                payload,
                private_key_obj,
                algorithm='ES256',
                headers={'kid': self.key_name, 'nonce': str(timestamp)}
            )
            
            return token
            
        except ImportError:
            print("⚠️  Required libraries missing")
            print("   Install: pip install cryptography PyJWT")
            return None
        except Exception as e:
            print(f"⚠️  JWT generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _make_request(self, method, path, data=None):
        """Make authenticated API request"""
        if not self.auth_type:
            return None
        
        # Generate JWT token
        token = self._generate_jwt_token(method, path)
        
        if not token:
            return None
        
        # Headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Full URL
        url = f"{self.base_url}{path}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"⚠️  API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"⚠️  Request error: {str(e)}")
            return None
    
    def test_connection(self):
        """Test API connection"""
        try:
            response = requests.get("https://api.coinbase.com/v2/time", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_accounts(self):
        """Get all accounts"""
        path = '/api/v3/brokerage/accounts'
        return self._make_request('GET', path)
    
    def get_account(self, account_uuid):
        """Get specific account by UUID"""
        path = f'/api/v3/brokerage/accounts/{account_uuid}'
        return self._make_request('GET', path)
    
    def list_orders(self, product_id=None, limit=10):
        """List recent orders"""
        path = '/api/v3/brokerage/orders/batch'
        
        params = {'limit': limit}
        if product_id:
            params['product_id'] = product_id
        
        return self._make_request('GET', path)
    
    def get_product(self, product_id):
        """Get product details (e.g., BTC-USD)"""
        path = f'/api/v3/brokerage/products/{product_id}'
        return self._make_request('GET', path)
    
    def get_best_bid_ask(self, product_id):
        """Get current best bid/ask for a product"""
        path = f'/api/v3/brokerage/best_bid_ask'
        
        try:
            response = self._make_request('GET', f'{path}?product_ids={product_id}')
            
            if response and 'pricebooks' in response:
                for pricebook in response['pricebooks']:
                    if pricebook.get('product_id') == product_id:
                        return {
                            'bid': float(pricebook['bids'][0]['price']) if pricebook.get('bids') else None,
                            'ask': float(pricebook['asks'][0]['price']) if pricebook.get('asks') else None
                        }
            return None
        except:
            return None
    
    def place_market_order(self, product_id, side, quote_size=None, base_size=None):
        """
        Place a market order
        
        Args:
            product_id: e.g., 'BTC-USD'
            side: 'BUY' or 'SELL'
            quote_size: Amount in USD (for BUY)
            base_size: Amount in crypto (for SELL)
        
        Returns:
            dict with order details or error
        """
        if not self.auth_type:
            return {
                'success': False,
                'error': 'No credentials configured'
            }
        
        path = '/api/v3/brokerage/orders'
        
        # Generate unique client order ID
        client_order_id = str(uuid.uuid4())
        
        # Build order configuration
        order_config = {
            'market_market_ioc': {}
        }
        
        if side.upper() == 'BUY':
            if not quote_size:
                return {
                    'success': False,
                    'error': 'quote_size required for BUY orders'
                }
            order_config['market_market_ioc']['quote_size'] = str(quote_size)
        
        elif side.upper() == 'SELL':
            if not base_size:
                return {
                    'success': False,
                    'error': 'base_size required for SELL orders'
                }
            order_config['market_market_ioc']['base_size'] = str(base_size)
        
        else:
            return {
                'success': False,
                'error': 'side must be BUY or SELL'
            }
        
        # Order payload
        order_data = {
            'client_order_id': client_order_id,
            'product_id': product_id,
            'side': side.upper(),
            'order_configuration': order_config
        }
        
        print(f"📤 Placing {side.upper()} order for {product_id}...")
        
        # Make request
        response = self._make_request('POST', path, order_data)
        
        if not response:
            return {
                'success': False,
                'error': 'API request failed'
            }
        
        # Check if order was successful
        if response.get('success'):
            order_id = response.get('order_id')
            
            print(f"✅ Order placed! ID: {order_id}")
            
            # Wait a moment for order to fill
            time.sleep(2)
            
            # Get order details
            order_details = self.get_order(order_id)
            
            if order_details:
                return self._parse_order_response(order_details)
            else:
                return {
                    'success': True,
                    'order_id': order_id,
                    'status': 'PENDING',
                    'message': 'Order placed but details unavailable'
                }
        else:
            error_msg = response.get('error_response', {}).get('message', 'Unknown error')
            return {
                'success': False,
                'error': error_msg,
                'response': response
            }
    
    def get_order(self, order_id):
        """Get order details by ID"""
        path = f'/api/v3/brokerage/orders/historical/{order_id}'
        return self._make_request('GET', path)
    
    def _parse_order_response(self, order_data):
        """Parse order response into standardized format"""
        try:
            order = order_data.get('order', {})
            
            # Get fill details
            filled_size = float(order.get('filled_size', 0))
            filled_value = float(order.get('filled_value', 0))
            total_fees = float(order.get('total_fees', 0))
            
            # Calculate average price
            avg_price = filled_value / filled_size if filled_size > 0 else 0
            
            return {
                'success': True,
                'order_id': order.get('order_id'),
                'status': order.get('status'),
                'side': order.get('side'),
                'product_id': order.get('product_id'),
                'price': avg_price,
                'filled_size': filled_size,
                'filled_value': filled_value,
                'total_fees': total_fees,
                'created_time': order.get('created_time'),
                'completion_percentage': order.get('completion_percentage', '0'),
                
                # Standardized format for bot
                'amount_usd': filled_value,
                'fee_usd': total_fees,
                'quantity': filled_size
            }
            
        except Exception as e:
            print(f"⚠️  Error parsing order: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to parse order: {str(e)}',
                'raw_data': order_data
            }
    
    def place_order(self, coin, side, amount_usd):
        """
        Place order (standardized interface for bot)
        
        Args:
            coin: 'BTC-USD', 'ETH-USD', etc.
            side: 'buy' or 'sell'
            amount_usd: Amount in USD
        
        Returns:
            dict with success, price, amount_usd, fee_usd
        """
        
        # Validate minimum order size
        if amount_usd < 1:
            return {
                'success': False,
                'error': f'Order size too small: ${amount_usd:.2f} (minimum $1)',
                'price': 0,
                'amount_usd': 0,
                'fee_usd': 0
            }
        
        try:
            if side.lower() == 'buy':
                # Market buy with USD amount
                result = self.place_market_order(
                    product_id=coin,
                    side='BUY',
                    quote_size=amount_usd
                )
                
            elif side.lower() == 'sell':
                # For sell, need to calculate base_size from amount_usd
                # Get current price
                from services.price_api import PriceAPI
                price_api = PriceAPI()
                current_price = price_api.get_price(coin)
                
                if not current_price:
                    return {
                        'success': False,
                        'error': 'Could not fetch current price for sell calculation',
                        'price': 0,
                        'amount_usd': 0,
                        'fee_usd': 0
                    }
                
                # Calculate base size (amount of crypto)
                base_size = amount_usd / current_price
                
                result = self.place_market_order(
                    product_id=coin,
                    side='SELL',
                    base_size=base_size
                )
            
            else:
                return {
                    'success': False,
                    'error': f'Invalid side: {side}',
                    'price': 0,
                    'amount_usd': 0,
                    'fee_usd': 0
                }
            
            # Return in standardized format
            if result.get('success'):
                return {
                    'success': True,
                    'price': result.get('price', 0),
                    'amount_usd': result.get('filled_value', amount_usd),
                    'fee_usd': result.get('total_fees', 0),
                    'order_id': result.get('order_id'),
                    'status': result.get('status'),
                    'quantity': result.get('filled_size', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'price': 0,
                    'amount_usd': 0,
                    'fee_usd': 0
                }
                
        except Exception as e:
            print(f"⚠️  Order execution error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': f'Exception: {str(e)}',
                'price': 0,
                'amount_usd': 0,
                'fee_usd': 0
            }
    
    def get_usd_balance(self):
        """Get USD account balance"""
        accounts = self.get_accounts()
        
        if not accounts or 'accounts' not in accounts:
            return None
        
        for account in accounts['accounts']:
            if account.get('currency') == 'USD':
                return {
                    'available': float(account.get('available_balance', {}).get('value', 0)),
                    'hold': float(account.get('hold', {}).get('value', 0))
                }
        
        return None
    
    def get_crypto_balance(self, currency):
        """Get crypto balance (e.g., 'BTC', 'ETH')"""
        accounts = self.get_accounts()
        
        if not accounts or 'accounts' not in accounts:
            return None
        
        for account in accounts['accounts']:
            if account.get('currency') == currency:
                return {
                    'available': float(account.get('available_balance', {}).get('value', 0)),
                    'hold': float(account.get('hold', {}).get('value', 0))
                }
        
        return None
