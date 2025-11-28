import json
from coinbase.rest import RESTClient

def load_credentials(path="config/credentials.json"):
    with open(path, "r") as f:
        return json.load(f)

def test_coinbase_auth():
    # Load CDP API credentials
    creds = load_credentials()

    coinbase = creds["coinbase"]
    key_name = coinbase["key_name"]
    private_key = coinbase["private_key"]

    print("[*] Loaded credentials")
    print(f"    Key Name: {key_name}")

    # Initialize the CDP REST Client
    try:
        client = RESTClient(api_key=key_name, api_secret=private_key)
        print("[*] REST Client initialized")
    except Exception as e:
        print("[ERROR] Failed initializing RESTClient:", e)
        return

    # Test: list accounts
    try:
        print("[*] Sending test request -> GET /accounts ...")
        response = client.get_accounts()
        print("[SUCCESS] API Authenticated!")
        print("Accounts Response:")
        print(response)
    except Exception as e:
        print("[ERROR] Authentication failed:")
        print(e)

if __name__ == "__main__":
    print("=== Coinbase API Test Script ===")
    test_coinbase_auth()
