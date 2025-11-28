import json
import time
from coinbase.rest import RESTClient

CREDENTIALS_PATH = "config/credentials.json"

# ---- CONFIGURABLE TEST SETTINGS ----
PRODUCT_ID = "BTC-USD"           # e.g. BTC-USD, ETH-USD, SOL-USD
BUY_QUOTE_SIZE = "1.00"          # spend $1.00 on the buy
SLEEP_BETWEEN_CHECKS = 2         # seconds between order status checks
MAX_STATUS_CHECKS = 10           # how many times to poll get_order
SLEEP_BEFORE_SELL = 3            # pause after filled before sell
# ------------------------------------


def load_credentials(path=CREDENTIALS_PATH):
    with open(path, "r") as f:
        return json.load(f)


def create_client():
    creds = load_credentials()
    coinbase = creds["coinbase"]
    key_name = coinbase["key_name"]
    private_key = coinbase["private_key"]

    print("[*] Loaded credentials")
    print("    Key Name: {}".format(key_name))

    client = RESTClient(api_key=key_name, api_secret=private_key)
    print("[*] REST Client initialized")
    return client


def place_market_buy(client):
    """
    Place a market BUY using quote_size (spend BUY_QUOTE_SIZE of quote currency).
    Returns the created order_id.
    """
    print("[*] Placing MARKET BUY on {} for quote_size=${} ...".format(PRODUCT_ID, BUY_QUOTE_SIZE))
    resp = client.create_order(
        client_order_id="test-buy-{}".format(int(time.time())),
        product_id=PRODUCT_ID,
        side="BUY",
        order_configuration={
            "market_market_ioc": {
                "quote_size": BUY_QUOTE_SIZE
            }
        },
    )

    order = resp.to_dict()
    print("[BUY RESPONSE]")
    print(order)

    error_resp = order.get("error_response")
    if error_resp:
        print("[BUY ERROR RESPONSE]")
        print(error_resp)
        raise RuntimeError("Buy order was rejected by Coinbase.")

    success_resp = order.get("success_response", {})
    order_id = success_resp.get("order_id")

    if not order_id:
        raise RuntimeError("Could not find order_id in buy response.")

    return order_id


def wait_for_filled_size(client, order_id):
    """
    Poll get_order() until the order is FILLED or we give up.
    Returns filled_size (base asset amount) as a string, or None.
    """
    for attempt in range(1, MAX_STATUS_CHECKS + 1):
        print("[*] Fetching order status (attempt {}/{}) for order_id={} ...".format(
            attempt, MAX_STATUS_CHECKS, order_id
        ))
        resp = client.get_order(order_id=order_id)
        order_details = resp.to_dict()
        order = order_details.get("order", {})

        status = order.get("status")
        filled_size = order.get("filled_size")  # base asset filled

        print("[ORDER DETAILS]")
        print(order_details)

        if status == "FILLED" and filled_size:
            print("[*] Order is FILLED with filled_size={}".format(filled_size))
            return filled_size

        print("[*] Status={}, filled_size={}. Waiting {} seconds...".format(
            status, filled_size, SLEEP_BETWEEN_CHECKS
        ))
        time.sleep(SLEEP_BETWEEN_CHECKS)

    print("[WARN] Order did not reach FILLED status in time.")
    return None


def place_market_sell_base(client, base_size_str):
    """
    Place a market SELL using base_size (required by Coinbase for market sells).
    """
    print("[*] Placing MARKET SELL on {} for base_size={} ...".format(PRODUCT_ID, base_size_str))

    resp = client.create_order(
        client_order_id="test-sell-{}".format(int(time.time())),
        product_id=PRODUCT_ID,
        side="SELL",
        order_configuration={
            "market_market_ioc": {
                "base_size": base_size_str
            }
        },
    )

    order = resp.to_dict()
    print("[SELL RESPONSE]")
    print(order)

    error_resp = order.get("error_response")
    if error_resp:
        print("[SELL ERROR RESPONSE]")
        print(error_resp)
        raise RuntimeError("Sell order was rejected by Coinbase.")

    return order


def main():
    print("=== Coinbase BUY/SELL Test Script (base_size sell) ===")
    client = create_client()

    # 1. Place BUY order
    buy_order_id = place_market_buy(client)

    # 2. Wait for order to be filled and get filled_size (base asset amount)
    filled_size = wait_for_filled_size(client, buy_order_id)
    if not filled_size:
        print("[WARN] Could not get a filled_size for the buy order. Aborting sell.")
        return

    print("[*] Using filled_size={} as base_size for sell.".format(filled_size))

    # 3. Optional pause before sell
    print("[*] Waiting {} seconds before selling...".format(SLEEP_BEFORE_SELL))
    time.sleep(SLEEP_BEFORE_SELL)

    # 4. Place SELL using base_size
    place_market_sell_base(client, base_size_str=filled_size)

    print("=== Done ===")


if __name__ == "__main__":
    main()
