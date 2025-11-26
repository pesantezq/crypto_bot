"""
Credential Manager - Secure credential loading
Supports Windows Credential Manager, environment variables, and JSON file
"""

import os
import json
from pathlib import Path


class CredentialManager:
    """Manage API credentials securely"""
    
    @staticmethod
    def load_credentials():
        """Load credentials from available sources"""
        credentials = {}
        
        # Try JSON file first
        cred_file = Path("config") / "credentials.json"
        if cred_file.exists():
            with open(cred_file, 'r') as f:
                credentials = json.load(f)
                # Remove comment field if present
                credentials.pop('_comment', None)
                return credentials
        
        # Fallback to environment variables
        coinbase_key = os.getenv('COINBASE_API_KEY')
        coinbase_secret = os.getenv('COINBASE_API_SECRET')
        coinbase_pass = os.getenv('COINBASE_PASSPHRASE')
        
        if coinbase_key and coinbase_secret and coinbase_pass:
            credentials['coinbase'] = {
                'api_key': coinbase_key,
                'api_secret': coinbase_secret,
                'passphrase': coinbase_pass
            }
        
        return credentials
    
    @staticmethod
    def get_coinbase_credentials():
        """Get Coinbase API credentials"""
        creds = CredentialManager.load_credentials()
        return creds.get('coinbase', {})
    
    @staticmethod
    def get_cryptocompare_key():
        """Get CryptoCompare API key (optional)"""
        creds = CredentialManager.load_credentials()
        return creds.get('cryptocompare', {}).get('api_key', '')
