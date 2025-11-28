"""
Coinbase API Diagnostic Tool
Helps identify authentication issues
"""

import json
from pathlib import Path
import requests


def check_credentials_file():
    """Check credentials file format"""
    print("\n" + "=" * 70)
    print("  STEP 1: Checking Credentials File")
    print("=" * 70)
    
    creds_file = Path("config/credentials.json")
    
    if not creds_file.exists():
        print("\n❌ credentials.json not found!")
        return None
    
    print("✅ File exists")
    
    try:
        with open(creds_file, 'r') as f:
            creds = json.load(f)
        
        print("✅ Valid JSON")
        
        if 'coinbase' not in creds:
            print("❌ No 'coinbase' section")
            return None
        
        print("✅ Has 'coinbase' section")
        
        cb = creds['coinbase']
        
        if 'key_name' not in cb or 'private_key' not in cb:
            print("❌ Missing key_name or private_key")
            return None
        
        print("✅ Has key_name and private_key")
        
        # Check key_name format
        key_name = cb['key_name']
        print(f"\n📋 Key Name: {key_name}")
        
        if 'organizations/' in key_name and 'apiKeys/' in key_name:
            print("✅ Key name format looks correct")
        else:
            print("⚠️  Key name format might be wrong")
            print("   Expected: organizations/{uuid}/apiKeys/{uuid}")
        
        # Check private key format
        private_key = cb['private_key']
        print(f"\n🔑 Private Key: {len(private_key)} characters")
        
        if '-----BEGIN EC PRIVATE KEY-----' in private_key:
            print("✅ Has EC PRIVATE KEY header")
        else:
            print("❌ Missing EC PRIVATE KEY header")
            print("   Must start with: -----BEGIN EC PRIVATE KEY-----")
            return None
        
        if '-----END EC PRIVATE KEY-----' in private_key:
            print("✅ Has EC PRIVATE KEY footer")
        else:
            print("❌ Missing EC PRIVATE KEY footer")
            return None
        
        # Check for newlines
        if '\\n' in private_key or '\n' in private_key:
            print("✅ Has line breaks (good)")
        else:
            print("⚠️  No line breaks detected - might need \\n")
        
        return cb
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_jwt_generation(creds):
    """Test JWT token generation"""
    print("\n" + "=" * 70)
    print("  STEP 2: Testing JWT Generation")
    print("=" * 70)
    
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        import jwt
        import time
        
        print("✅ Required libraries imported")
        
        # Try to load private key
        private_key_str = creds['private_key']
        key_name = creds['key_name']
        
        print(f"\n🔑 Attempting to load private key...")
        
        try:
            private_key_obj = serialization.load_pem_private_key(
                private_key_str.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            print("✅ Private key loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load private key: {str(e)}")
            print("\n💡 Common issues:")
            print("   1. Make sure key starts with -----BEGIN EC PRIVATE KEY-----")
            print("   2. Make sure key ends with -----END EC PRIVATE KEY-----")
            print("   3. Make sure newlines are preserved (use \\n in JSON)")
            return None
        
        # Generate JWT
        print(f"\n🔐 Generating JWT token...")
        
        timestamp = int(time.time())
        
        payload = {
            'sub': key_name,
            'iss': 'coinbase-cloud',
            'nbf': timestamp,
            'exp': timestamp + 120,
            'uri': 'GET /api/v3/brokerage/accounts'
        }
        
        print(f"   Payload:")
        print(f"   - sub: {key_name}")
        print(f"   - iss: coinbase-cloud")
        print(f"   - uri: GET /api/v3/brokerage/accounts")
        
        try:
            token = jwt.encode(
                payload,
                private_key_obj,
                algorithm='ES256',
                headers={'kid': key_name, 'nonce': str(timestamp)}
            )
            print("✅ JWT token generated successfully")
            print(f"   Token length: {len(token)} characters")
            return token
            
        except Exception as e:
            print(f"❌ Failed to generate JWT: {str(e)}")
            return None
        
    except ImportError as e:
        print(f"❌ Missing library: {str(e)}")
        print("\n💡 Install with:")
        print("   pip install cryptography PyJWT --break-system-packages")
        return None


def test_api_call(token, key_name):
    """Test actual API call"""
    print("\n" + "=" * 70)
    print("  STEP 3: Testing API Call")
    print("=" * 70)
    
    url = "https://api.coinbase.com/api/v3/brokerage/accounts"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n📡 Calling: {url}")
    print(f"   Authorization: Bearer {token[:50]}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"\n📊 Response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! API call worked!")
            
            data = response.json()
            if 'accounts' in data:
                print(f"\n📋 Accounts found: {len(data['accounts'])}")
                for i, account in enumerate(data['accounts'][:3]):
                    currency = account.get('currency', 'Unknown')
                    available = account.get('available_balance', {}).get('value', '0')
                    print(f"   {i+1}. {currency}: {available}")
            
            return True
            
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED (401)")
            print(f"   Response: {response.text}")
            
            print("\n💡 Possible issues:")
            print("   1. API key permissions - need View + Trade")
            print("   2. API key not activated yet")
            print("   3. Wrong API key (using wrong account?)")
            print("   4. Key revoked or expired")
            print("   5. Wrong key_name format")
            
            return False
            
        elif response.status_code == 403:
            print("❌ FORBIDDEN (403)")
            print(f"   Response: {response.text}")
            print("\n💡 Likely issue: Insufficient permissions")
            print("   Make sure API has View + Trade permissions")
            return False
            
        else:
            print(f"❌ ERROR ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False


def check_api_key_on_coinbase():
    """Instructions for checking API key on Coinbase"""
    print("\n" + "=" * 70)
    print("  STEP 4: Check API Key on Coinbase")
    print("=" * 70)
    
    print("\n📋 Manual checks to perform:")
    print("\n1. Go to: https://www.coinbase.com/settings/api")
    print("\n2. Find your API key in the list")
    print("\n3. Verify:")
    print("   ✓ Type: ECDSA (NOT Ed25519)")
    print("   ✓ Status: Active (not pending or disabled)")
    print("   ✓ Permissions:")
    print("      ✓ View: YES")
    print("      ✓ Trade: YES")
    print("      ✗ Transfer: NO (security)")
    print("      ✗ Withdraw: NO (security)")
    print("\n4. Key name format:")
    print("   Should look like:")
    print("   organizations/12345678-abcd-1234-abcd-123456789012/apiKeys/87654321-dcba-4321-dcba-210987654321")
    print("\n5. If anything looks wrong:")
    print("   - Delete the old key")
    print("   - Create a new ECDSA key")
    print("   - Update credentials.json")
    print("   - Run this diagnostic again")


def main():
    """Run full diagnostic"""
    print("\n" + "=" * 70)
    print("  🔍 COINBASE API DIAGNOSTIC TOOL")
    print("=" * 70)
    print("\n  This tool will help identify authentication issues")
    
    input("\n  Press Enter to start diagnostic...")
    
    # Step 1: Check credentials file
    creds = check_credentials_file()
    
    if not creds:
        print("\n❌ Fix credentials file first, then run again")
        return
    
    # Step 2: Test JWT generation
    token = test_jwt_generation(creds)
    
    if not token:
        print("\n❌ Fix JWT generation issues first")
        return
    
    # Step 3: Test API call
    success = test_api_call(token, creds['key_name'])
    
    if not success:
        # Step 4: Manual checks
        check_api_key_on_coinbase()
    
    # Summary
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("\n   Your API is configured correctly!")
        print("   Ready for live trading!")
        print("\n   Next step:")
        print("   python main.py --live --phase micro_live --confirm")
    else:
        print("\n❌ AUTHENTICATION FAILED")
        print("\n   Most likely issues:")
        print("   1. API key permissions (View + Trade required)")
        print("   2. API key type (must be ECDSA, not Ed25519)")
        print("   3. API key not activated yet")
        print("\n   Fix:")
        print("   1. Go to https://www.coinbase.com/settings/api")
        print("   2. Check your API key settings")
        print("   3. Create new ECDSA key if needed")
        print("   4. Update config/credentials.json")
        print("   5. Run this diagnostic again")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Diagnostic cancelled")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()