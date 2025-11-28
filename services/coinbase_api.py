"""
<<<<<<< HEAD
Coinbase API Service
Wrapper for Coinbase REST API with paper trading support

FIXED: Uses correct order_configuration structure:
- BUY: market_market_ioc with quote_size (USD to spend)
- SELL: market_market_ioc with base_size (crypto amount to sell)
=======
Coinbase API Wrapper - ECDSA Authentication Support
Supports both ECDSA (new) and Legacy (old) authentication
>>>>>>> 563997708e45861b54fbbf96c5ebd8669ad0a0a2
"""

import json
import time
<<<<<<< HEAD
import os
from typing import Dict, Optional

try:
    from coinbase.rest import RESTClient
    COINBASE_AVAILABLE = True
except ImportError:
    COINBASE_AVAILABLE = False
    print("⚠️  WARNING: coinbase module not installed")
    print("   Install with: pip install coinbase-advanced-py")
    print("   Paper trading will still work without it")


class CoinbaseAPI:
    """Coinbase API wrapper with paper/live mode support."""
=======
import hmac
import hashlib
import base64
import json
from datetime import datetime


class CoinbaseAPI:
    """Coinbase API wrapper with ECDSA and Legacy support"""
>>>>>>> 563997708e45861b54fbbf96c5ebd8669ad0a0a2
    
    def __init__(self, paper_mode: bool = False, credentials_path: str = "config/credentials.json", sandbox: bool = False):
        """
        Initialize Coinbase API client.
        
        Args:
            paper_mode: If True, simulate trades without real execution
            credentials_path: Path to credentials JSON file
            sandbox: Ignored (for backward compatibility)
        """
        self.paper_mode = paper_mode
        self.credentials_path = credentials_path
        self.client = None
        self.paper_balances = {}  # Simulated balances for paper trading
        self.positions = {}  # Track positions: {product_id: base_size}
        
        # Note: sandbox parameter ignored - Coinbase Advanced Trade API doesn't use sandbox mode
        if sandbox:
            print("[INFO] Sandbox parameter ignored - using paper_mode instead")
        
        if not paper_mode:
            self._initialize_client()
        else:
            print("[PAPER MODE] Coinbase API in simulation mode")
    
    def _initialize_client(self):
        """Initialize real Coinbase REST client."""
        if not COINBASE_AVAILABLE:
            raise RuntimeError(
                "Coinbase SDK not installed.\n"
                "Install with: pip install coinbase-advanced-py\n"
                "Or use --paper mode for testing"
            )
        
<<<<<<< HEAD
        try:
            creds = self._load_credentials()
            coinbase = creds.get("coinbase", {})
            key_name = coinbase.get("key_name")
            private_key = coinbase.get("private_key")
            
            if not key_name or not private_key:
                raise ValueError("Missing key_name or private_key in credentials")
            
            self.client = RESTClient(api_key=key_name, api_secret=private_key)
            print("[*] Coinbase REST Client initialized")
            print(f"    Key Name: {key_name}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Coinbase client: {e}")
    
    def test_connection(self) -> bool:
        if self.paper_mode:
            print("[PAPER MODE] Connection test skipped")
            return True
        
        if not COINBASE_AVAILABLE:
            print("❌ Coinbase SDK not installed")
            return False
        
        try:
            if not self.client:
                print("❌ Client not initialized")
                return False
            
            accounts = self.client.get_accounts()
            # If the call succeeds, consider the connection healthy
            return True
        except Exception as e:
            print(f"❌ Coinbase API: Connection failed - {e}")
            return False
    
    def _load_credentials(self) -> Dict:
        """Load credentials from JSON file."""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}\n"
                f"Create it by copying config/credentials.example.json"
            )
        
        with open(self.credentials_path, 'r') as f:
            return json.load(f)
    
    def validate_credentials(self) -> bool:
=======
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
>>>>>>> 563997708e45861b54fbbf96c5ebd8669ad0a0a2
        """
        Validate API credentials are configured.
        
        Returns:
            True if credentials are valid
        """
<<<<<<< HEAD
        if self.paper_mode:
            return True
        
        try:
            return self.client is not None
        except Exception as e:
            print(f"❌ Credential validation failed: {e}")
            return False
    
    def set_paper_balance(self, currency: str, amount: float):
        """Set paper trading balance for a currency."""
        if self.paper_mode:
            self.paper_balances[currency] = amount
            print(f"[PAPER MODE] Set balance: {currency} = {amount}")
    
    def get_balance(self, currency: str = "USD") -> float:
        """
        Get balance for a currency.
        
        Args:
            currency: Currency code (e.g., "USD", "BTC")
            
        Returns:
            Balance as float
        """
        if self.paper_mode:
            return self.paper_balances.get(currency, 0.0)
        
        try:
            # Use Coinbase API to get real balance
            accounts = self.client.get_accounts()
            accounts_dict = accounts.to_dict()
            
            for account in accounts_dict.get("accounts", []):
                if account.get("currency") == currency:
                    available = account.get("available_balance", {})
                    return float(available.get("value", 0))
            
            return 0.0
            
        except Exception as e:
            print(f"❌ Error getting balance for {currency}: {e}")
            return 0.0
    
    def get_position(self, product_id: str) -> float:
        """
        Get current position size for a product.
        
        Args:
            product_id: Trading pair (e.g., "BTC-USD")
            
        Returns:
            Position size in base currency
        """
        return self.positions.get(product_id, 0.0)
    
    def place_order(self, coin: str, side: str, amount_usd: float) -> Dict:
        """
        Place a market order (unified interface for main.py).
        
        Args:
            coin: Trading pair (e.g., "BTC-USD")
            side: "buy" or "sell"
            amount_usd: Amount in USD (for buy) or position value to sell
            
        Returns:
            Dict with success status and order details
        """
        try:
            if side.lower() == "buy":
                order = self.market_buy(coin, str(amount_usd))
                if order:
                    # Track the position
                    filled_size = float(order.get("filled_size", 0))
                    current_position = self.positions.get(coin, 0.0)
                    self.positions[coin] = current_position + filled_size
                    
                    return {
                        "success": True,
                        "order_id": order.get("order_id"),
                        "price": float(order.get("average_filled_price", 0)) or self.get_product_price(coin),
                        "amount_usd": amount_usd,
                        "filled_size": filled_size,
                        "fee_usd": float(order.get("total_fees", 0))
                    }
                else:
                    return {"success": False, "error": "Buy order failed"}
                    
            elif side.lower() == "sell":
                # Get the position to sell
                position = self.positions.get(coin, 0.0)
                
                if position <= 0:
                    return {"success": False, "error": f"No position to sell for {coin}"}
                
                # Sell the entire position (or calculate based on amount_usd)
                order = self.market_sell(coin, str(position))
                if order:
                    # Clear the position
                    filled_size = float(order.get("filled_size", 0))
                    self.positions[coin] = max(0, self.positions.get(coin, 0) - filled_size)
                    
                    filled_value = float(order.get("filled_value", 0))
                    avg_price = float(order.get("average_filled_price", 0)) or self.get_product_price(coin)
                    
                    return {
                        "success": True,
                        "order_id": order.get("order_id"),
                        "price": avg_price,
                        "amount_usd": filled_value or (filled_size * avg_price),
                        "filled_size": filled_size,
                        "fee_usd": float(order.get("total_fees", 0))
                    }
                else:
                    return {"success": False, "error": "Sell order failed"}
            else:
                return {"success": False, "error": f"Invalid side: {side}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def market_buy(self, product_id: str, quote_size: str) -> Optional[Dict]:
        """
        Place a market buy order.
        
        Args:
            product_id: Trading pair (e.g., "BTC-USD")
            quote_size: Amount of quote currency to spend (e.g., "10.00")
            
        Returns:
            Order details dict or None if failed
        """
        if self.paper_mode:
            return self._simulate_buy(product_id, quote_size)
        
        try:
            print(f"[*] Placing MARKET BUY on {product_id} for ${quote_size}...")
            
            resp = self.client.create_order(
                client_order_id=f"buy-{int(time.time())}",
                product_id=product_id,
                side="BUY",
                order_configuration={
                    "market_market_ioc": {
                        "quote_size": quote_size
                    }
                }
            )
            
            order = resp.to_dict()
            print(f"[BUY RESPONSE] {order}")
            
            # Check for errors
            error_resp = order.get("error_response")
            if error_resp:
                print(f"[BUY ERROR] {error_resp}")
                return None
            
            success_resp = order.get("success_response", {})
            order_id = success_resp.get("order_id")
            
            if not order_id:
                print("[BUY ERROR] No order_id in response")
                return None
            
            # Wait for fill and get details
            filled_order = self._wait_for_fill(order_id)
            return filled_order
            
        except Exception as e:
            print(f"❌ Market buy error: {e}")
            return None
    
    def market_sell(self, product_id: str, base_size: str) -> Optional[Dict]:
        """
        Place a market sell order.
        
        Args:
            product_id: Trading pair (e.g., "BTC-USD")
            base_size: Amount of base currency to sell (e.g., "0.001")
            
        Returns:
            Order details dict or None if failed
        """
        if self.paper_mode:
            return self._simulate_sell(product_id, base_size)
        
        try:
            print(f"[*] Placing MARKET SELL on {product_id} for {base_size}...")
            
            resp = self.client.create_order(
                client_order_id=f"sell-{int(time.time())}",
                product_id=product_id,
                side="SELL",
                order_configuration={
                    "market_market_ioc": {
                        "base_size": base_size
                    }
                }
            )
            
            order = resp.to_dict()
            print(f"[SELL RESPONSE] {order}")
            
            # Check for errors
            error_resp = order.get("error_response")
            if error_resp:
                print(f"[SELL ERROR] {error_resp}")
                return None
            
            success_resp = order.get("success_response", {})
            order_id = success_resp.get("order_id")
            
            if not order_id:
                print("[SELL ERROR] No order_id in response")
                return None
            
            # Wait for fill and get details
            filled_order = self._wait_for_fill(order_id)
            return filled_order
            
        except Exception as e:
            print(f"❌ Market sell error: {e}")
            return None
    
    def _wait_for_fill(self, order_id: str, max_attempts: int = 10, sleep_time: int = 2) -> Optional[Dict]:
        """
        Wait for order to be filled.
        
        Args:
            order_id: Order ID to check
            max_attempts: Maximum number of status checks
            sleep_time: Seconds between checks
            
        Returns:
            Filled order details or None
        """
        for attempt in range(1, max_attempts + 1):
            try:
                resp = self.client.get_order(order_id=order_id)
                order_details = resp.to_dict()
                order = order_details.get("order", {})
                
                status = order.get("status")
                filled_size = order.get("filled_size")
                
                print(f"[*] Order status check {attempt}/{max_attempts}: {status}")
                
                if status == "FILLED":
                    print(f"[*] Order FILLED: {filled_size} units")
                    return order
                
                if status in ["CANCELLED", "EXPIRED", "FAILED"]:
                    print(f"[*] Order {status}")
                    return None
                
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"[WARN] Error checking order status: {e}")
                time.sleep(sleep_time)
        
        print("[WARN] Order did not fill in time")
        return None
    
    def _simulate_buy(self, product_id: str, quote_size: str) -> Dict:
        """Simulate a buy order in paper mode."""
        quote_amount = float(quote_size)
        
        # Deduct from USD balance
        usd_balance = self.paper_balances.get("USD", 0)
        if usd_balance < quote_amount:
            print(f"[PAPER MODE] Insufficient balance: ${usd_balance:.2f}")
            return None
        
        self.paper_balances["USD"] = usd_balance - quote_amount
        
        # Get simulated price
        price = self.get_product_price(product_id) or 50000.0
        filled_size = quote_amount / price
        
        # Track position
        current_position = self.positions.get(product_id, 0.0)
        self.positions[product_id] = current_position + filled_size
        
        return {
            "order_id": f"paper-buy-{int(time.time())}",
            "product_id": product_id,
            "side": "BUY",
            "status": "FILLED",
            "filled_size": str(filled_size),
            "filled_value": quote_size,
            "average_filled_price": str(price),
            "total_fees": "0",
            "paper_mode": True
        }
    
    def _simulate_sell(self, product_id: str, base_size: str) -> Dict:
        """Simulate a sell order in paper mode."""
        base_amount = float(base_size)
        
        # Get simulated price
        price = self.get_product_price(product_id) or 50000.0
        filled_value = base_amount * price
        
        # Update USD balance
        self.paper_balances["USD"] = self.paper_balances.get("USD", 0) + filled_value
        
        # Clear position
        current_position = self.positions.get(product_id, 0.0)
        self.positions[product_id] = max(0, current_position - base_amount)
        
        return {
            "order_id": f"paper-sell-{int(time.time())}",
            "product_id": product_id,
            "side": "SELL",
            "status": "FILLED",
            "filled_size": base_size,
            "filled_value": str(filled_value),
            "average_filled_price": str(price),
            "total_fees": "0",
            "paper_mode": True
        }
    
    def get_product_price(self, product_id: str) -> Optional[float]:
        """
        Get current price for a product.
        
        Args:
            product_id: Trading pair (e.g., "BTC-USD")
            
        Returns:
            Current price or None
        """
        if self.paper_mode:
            # Return mock prices for paper trading
            mock_prices = {
                "BTC-USD": 95000.0,
                "ETH-USD": 3500.0,
                "SOL-USD": 180.0,
                "AVAX-USD": 35.0,
                "DOGE-USD": 0.35
            }
            return mock_prices.get(product_id, 100.0)
        
        try:
            product = self.client.get_product(product_id=product_id)
            product_dict = product.to_dict()
            price = product_dict.get("price")
            return float(price) if price else None
            
        except Exception as e:
            print(f"❌ Error getting price for {product_id}: {e}")
            return None
=======
        
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
>>>>>>> 563997708e45861b54fbbf96c5ebd8669ad0a0a2
