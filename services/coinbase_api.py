"""
Coinbase API Wrapper - ECDSA Authentication Support
Supports both ECDSA (new) and Legacy (old) authentication
"""

import requests
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime


class CoinbaseAPI:
    """Coinbase API wrapper with ECDSA and Legacy support"""
    
    def __init__(self, sandbox=False):
        """Initialize Coinbase API"""
        self.sandbox = sandbox
        
        if sandbox:
            self.base_url = "https://api-public.sandbox.pro.coinbase.com"
        else:
            self.base_url = "https://api.coinbase.com"
        
        # These will be loaded from credentials
        # For ECDSA: key_name and private_key
        # For Legacy: api_key, api_secret, passphrase
        self.key_name = ""
        self.private_key = ""
        self.api_key = ""
        self.api_secret = ""
        self.passphrase = ""
        self.auth_type = None  # 'ecdsa' or 'legacy'
        
        self._load_credentials()
        
    def _load_credentials(self):
        """Load and detect credential type"""
        try:
            from services.credentials import CredentialManager
            creds = CredentialManager.get_coinbase_credentials()
            
            # Detect ECDSA credentials
            if 'key_name' in creds and 'private_key' in creds:
                self.key_name = creds['key_name']
                self.private_key = creds['private_key']
                self.auth_type = 'ecdsa'
                print("✓ Using ECDSA authentication")
                
            # Detect Legacy credentials
            elif 'api_key' in creds and 'api_secret' in creds and 'passphrase' in creds:
                self.api_key = creds['api_key']
                self.api_secret = creds['api_secret']
                self.passphrase = creds['passphrase']
                self.auth_type = 'legacy'
                print("✓ Using Legacy (HMAC) authentication")
                
            else:
                print("⚠️  Warning: Credentials not found or incomplete")
                self.auth_type = None
                
        except Exception as e:
            print(f"⚠️  Error loading credentials: {str(e)}")
            self.auth_type = None
    
    def test_connection(self):
        """Test API connection"""
        try:
            # Simple time endpoint doesn't require authentication
            response = requests.get("https://api.coinbase.com/v2/time", timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
    
    def _sign_ecdsa(self, method, path, body=""):
        """
        Create ECDSA signature for Coinbase Advanced Trade API
        Uses JWT (JSON Web Token) with ES256 algorithm
        """
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.backends import default_backend
            import jwt
            
            # Parse the private key
            if self.private_key.startswith('-----BEGIN'):
                # PEM format
                private_key_obj = serialization.load_pem_private_key(
                    self.private_key.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            else:
                # Base64 encoded format
                private_key_bytes = base64.b64decode(self.private_key)
                private_key_obj = serialization.load_der_private_key(
                    private_key_bytes,
                    password=None,
                    backend=default_backend()
                )
            
            # Create JWT token
            uri = f"{method} {self.base_url.replace('https://api.coinbase.com', '')}{path}"
            
            # JWT payload
            timestamp = int(time.time())
            payload = {
                'sub': self.key_name,
                'iss': 'coinbase-cloud',
                'nbf': timestamp,
                'exp': timestamp + 120,  # Valid for 2 minutes
                'aud': ['public_websocket_api'],
            }
            
            # Sign with ECDSA (ES256)
            token = jwt.encode(
                payload,
                private_key_obj,
                algorithm='ES256',
                headers={'kid': self.key_name, 'nonce': str(timestamp)}
            )
            
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
        except ImportError as e:
            print("⚠️  Error: Required libraries not found")
            print("   Install: pip install cryptography PyJWT")
            return None
        except Exception as e:
            print(f"⚠️  ECDSA signing error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _sign_legacy(self, method, path, body=""):
        """Create HMAC-SHA256 signature for legacy API"""
        timestamp = str(int(time.time()))
        message = timestamp + method + path + body
        
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_accounts(self):
        """Get account information"""
        if not self.auth_type:
            return None
        
        try:
            if self.auth_type == 'ecdsa':
                path = '/api/v3/brokerage/accounts'
                headers = self._sign_ecdsa('GET', path)
                
                if headers:
                    response = requests.get(
                        f"{self.base_url}{path}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    else:
                        print(f"API Error: {response.status_code}")
                        print(f"Response: {response.text}")
                        
            elif self.auth_type == 'legacy':
                # Legacy API implementation
                pass
                
        except Exception as e:
            print(f"Error getting accounts: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def place_order(self, coin, side, amount_usd):
        """
        Place a market order
        Returns: dict with success, price, amount_usd, fee_usd
        """
        
        if not self.auth_type:
            return {
                'success': False,
                'error': 'No credentials configured',
                'price': 0,
                'amount_usd': 0,
                'fee_usd': 0
            }
        
        # For ECDSA, use Advanced Trade API
        if self.auth_type == 'ecdsa':
            return self._place_order_advanced_trade(coin, side, amount_usd)
        
        # For Legacy, use old API
        elif self.auth_type == 'legacy':
            return self._place_order_legacy(coin, side, amount_usd)
        
        return {
            'success': False,
            'error': 'Invalid authentication type',
            'price': 0,
            'amount_usd': 0,
            'fee_usd': 0
        }
    
    def _place_order_advanced_trade(self, coin, side, amount_usd):
        """
        Place order using Coinbase Advanced Trade API (ECDSA)
        
        IMPORTANT: This is a simplified placeholder
        Production implementation needs:
        1. Proper order creation via /api/v3/brokerage/orders
        2. Account balance checking
        3. Order status verification
        4. Fee calculation
        """
        
        try:
            print(f"⚠️  Advanced Trade API order placement not fully implemented")
            print(f"   Would place: {side} {coin} for ${amount_usd}")
            print(f"   Testing account access...")
            
            # Test if we can access accounts
            accounts = self.get_accounts()
            if accounts:
                print(f"   ✓ API authentication working!")
                print(f"   Connected to account successfully")
            else:
                print(f"   ✗ Could not access account")
            
            return {
                'success': False,
                'error': 'Advanced Trade API integration in progress - use paper trading',
                'price': 0,
                'amount_usd': 0,
                'fee_usd': 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'price': 0,
                'amount_usd': 0,
                'fee_usd': 0
            }
    
    def _place_order_legacy(self, coin, side, amount_usd):
        """Place order using legacy Coinbase Pro API"""
        
        try:
            print(f"⚠️  Legacy API order placement not fully implemented")
            print(f"   Would place: {side} {coin} for ${amount_usd}")
            
            return {
                'success': False,
                'error': 'Legacy API integration in progress - use paper trading',
                'price': 0,
                'amount_usd': 0,
                'fee_usd': 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'price': 0,
                'amount_usd': 0,
                'fee_usd': 0
            }
