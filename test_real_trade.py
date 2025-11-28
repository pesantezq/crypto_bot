"""
REAL TRADING TEST - EXECUTES ACTUAL TRADES WITH REAL MONEY
⚠️  WARNING: This script will BUY and SELL cryptocurrency with REAL MONEY
⚠️  Only use this if you understand the risks and have funds in your Coinbase account
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the REAL TRADING API (not the placeholder)
import importlib.util
spec = importlib.util.spec_from_file_location("coinbase_api", "coinbase_api_REAL_TRADING.py")
coinbase_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coinbase_module)
CoinbaseAPI = coinbase_module.CoinbaseAPI

from services.price_api import PriceAPI
from services.logger import Logger
from services.state import StateManager
import time
from datetime import datetime


def print_warning():
    """Print major warning about real money"""
    print("\n" + "!" * 70)
    print("!" * 70)
    print("!!                                                                  !!")
    print("!!   ⚠️  WARNING: REAL MONEY TRADING TEST ⚠️                        !!")
    print("!!                                                                  !!")
    print("!!   This script will execute ACTUAL trades on Coinbase            !!")
    print("!!   You will BUY and SELL cryptocurrency with REAL MONEY          !!")
    print("!!   There are fees involved (~0.5% per trade)                     !!")
    print("!!   You may lose money due to price movements and fees            !!")
    print("!!                                                                  !!")
    print("!" * 70)
    print("!" * 70)


def get_user_confirmation(test_amount):
    """Get explicit user confirmation"""
    print("\n" + "=" * 70)
    print("  CONFIRMATION REQUIRED")
    print("=" * 70)
    print(f"\n  This test will:")
    print(f"  1. BUY ${test_amount:.2f} worth of cryptocurrency")
    print(f"  2. Wait 10 seconds")
    print(f"  3. SELL immediately")
    print(f"\n  Estimated fees: ${test_amount * 0.01:.2f} (1% total)")
    print(f"  Expected loss: $0.10 - $0.50 (fees + slippage)")
    print(f"\n  Requirements:")
    print(f"  - You have USD in your Coinbase account")
    print(f"  - Your API keys are configured correctly")
    print(f"  - API has View + Trade permissions")
    
    print("\n" + "-" * 70)
    print("  Type EXACTLY: 'I UNDERSTAND THIS USES REAL MONEY'")
    print("-" * 70)
    
    confirmation = input("\n  > ").strip()
    
    if confirmation != "I UNDERSTAND THIS USES REAL MONEY":
        print("\n  ❌ Confirmation failed. Test cancelled.")
        return False
    
    print("\n  ⚠️  FINAL WARNING: You will spend real money in 10 seconds...")
    print("  Press Ctrl+C NOW to cancel, or wait to continue...")
    
    for i in range(10, 0, -1):
        print(f"  {i}...", end='\r')
        time.sleep(1)
    
    print("\n  ✅ Starting real trade test...")
    return True


def test_api_connection():
    """Test Coinbase API connection"""
    print("\n" + "=" * 70)
    print("  STEP 1: Testing Coinbase API Connection")
    print("=" * 70)
    
    coinbase = CoinbaseAPI(sandbox=False)
    
    print("\n  🔌 Testing connection...")
    
    if coinbase.test_connection():
        print("  ✅ Connection successful")
    else:
        print("  ❌ Connection failed")
        print("\n  Possible issues:")
        print("    - No internet connection")
        print("    - Coinbase API is down")
        return False
    
    print("\n  🔑 Testing authentication...")
    
    if not coinbase.auth_type:
        print("  ❌ No credentials found")
        print("\n  Please configure credentials in config/credentials.json")
        return False
    
    print(f"  ✅ Authentication type: {coinbase.auth_type.upper()}")
    
    # Test API access
    print("\n  📊 Testing API access...")
    
    try:
        # Try to get account info (requires authentication)
        if coinbase.auth_type == 'ecdsa':
            accounts = coinbase.get_accounts()
            if accounts:
                print("  ✅ API authentication working")
                print(f"  ✅ Connected to Coinbase account")
                return True
            else:
                print("  ❌ Could not access account")
                print("  Check your API key permissions (View + Trade required)")
                return False
        else:
            print("  ✅ Legacy API credentials loaded")
            return True
    except Exception as e:
        print(f"  ❌ Authentication error: {str(e)}")
        return False


def execute_real_buy(coin, amount_usd):
    """Execute real buy order"""
    print("\n" + "=" * 70)
    print("  STEP 2: Executing REAL BUY Order")
    print("=" * 70)
    
    coinbase = CoinbaseAPI(sandbox=False)
    price_api = PriceAPI()
    logger = Logger()
    
    # Get current price
    print(f"\n  📊 Fetching current price for {coin}...")
    current_price = price_api.get_price(coin)
    
    if not current_price:
        print(f"  ❌ Could not fetch price for {coin}")
        return None
    
    print(f"  ✅ Current price: ${current_price:,.2f}")
    
    # Calculate expected quantity
    expected_quantity = amount_usd / current_price
    print(f"  📐 Expected quantity: {expected_quantity:.8f} {coin.split('-')[0]}")
    print(f"  💵 Total cost: ${amount_usd:.2f}")
    
    print(f"\n  🔵 Placing BUY order...")
    print(f"     Coin: {coin}")
    print(f"     Type: MARKET order")
    print(f"     Amount: ${amount_usd:.2f}")
    
    # Execute order
    result = coinbase.place_order(coin, 'buy', amount_usd)
    
    if result['success']:
        print(f"\n  ✅ BUY ORDER SUCCESSFUL!")
        print(f"     Price: ${result['price']:,.2f}")
        print(f"     Amount: ${result['amount_usd']:.2f}")
        print(f"     Fee: ${result['fee_usd']:.2f}")
        print(f"     Total cost: ${result['amount_usd'] + result['fee_usd']:.2f}")
        
        # Log the trade
        logger.log_trade(
            strategy='real_test',
            coin=coin,
            action='buy',
            price=result['price'],
            quantity=result['amount_usd'] / result['price'],
            pnl=0,
            trigger_reason='manual_real_test',
            strategy_version='test',
            deployment_phase='test',
            execution_time_ms=0,
            slippage_percent=0,
            fee_usd=result['fee_usd'],
            balance=0
        )
        
        print(f"\n  ✅ Trade logged to data/trade_log.csv")
        
        return {
            'coin': coin,
            'price': result['price'],
            'quantity': result['amount_usd'] / result['price'],
            'amount_usd': result['amount_usd'],
            'fee_usd': result['fee_usd']
        }
    else:
        print(f"\n  ❌ BUY ORDER FAILED!")
        print(f"     Error: {result['error']}")
        
        # Log error
        logger.log_error(
            error_type='trade_execution',
            severity='high',
            message=f"Real buy test failed: {result['error']}",
            traceback='',
            recovery_action='manual_intervention'
        )
        
        return None


def execute_real_sell(coin, buy_info):
    """Execute real sell order"""
    print("\n" + "=" * 70)
    print("  STEP 3: Executing REAL SELL Order")
    print("=" * 70)
    
    print(f"\n  ⏳ Waiting 10 seconds before selling...")
    for i in range(10, 0, -1):
        print(f"     {i} seconds...", end='\r')
        time.sleep(1)
    print()
    
    coinbase = CoinbaseAPI(sandbox=False)
    price_api = PriceAPI()
    logger = Logger()
    
    # Get current price
    print(f"\n  📊 Fetching current price for {coin}...")
    current_price = price_api.get_price(coin)
    
    if not current_price:
        print(f"  ❌ Could not fetch price for {coin}")
        print(f"  ⚠️  You still have {buy_info['quantity']:.8f} {coin.split('-')[0]}")
        print(f"  ⚠️  You need to manually sell this on Coinbase!")
        return None
    
    print(f"  ✅ Current price: ${current_price:,.2f}")
    
    # Calculate value and P&L
    current_value = buy_info['quantity'] * current_price
    buy_cost = buy_info['amount_usd'] + buy_info['fee_usd']
    price_change = ((current_price - buy_info['price']) / buy_info['price']) * 100
    
    print(f"\n  📊 Position Status:")
    print(f"     Buy price: ${buy_info['price']:,.2f}")
    print(f"     Current price: ${current_price:,.2f}")
    print(f"     Price change: {price_change:+.2f}%")
    print(f"     Quantity: {buy_info['quantity']:.8f}")
    print(f"     Current value: ${current_value:.2f}")
    
    print(f"\n  🔴 Placing SELL order...")
    print(f"     Coin: {coin}")
    print(f"     Type: MARKET order")
    print(f"     Quantity: {buy_info['quantity']:.8f}")
    print(f"     Expected proceeds: ${current_value:.2f}")
    
    # Execute sell order
    result = coinbase.place_order(coin, 'sell', current_value)
    
    if result['success']:
        print(f"\n  ✅ SELL ORDER SUCCESSFUL!")
        print(f"     Price: ${result['price']:,.2f}")
        print(f"     Amount: ${result['amount_usd']:.2f}")
        print(f"     Fee: ${result['fee_usd']:.2f}")
        print(f"     Net proceeds: ${result['amount_usd'] - result['fee_usd']:.2f}")
        
        # Calculate total P&L
        sell_proceeds = result['amount_usd'] - result['fee_usd']
        total_pnl = sell_proceeds - buy_cost
        total_pnl_percent = (total_pnl / buy_cost) * 100
        
        print(f"\n  💰 TOTAL P&L:")
        print(f"     Buy cost (with fee): ${buy_cost:.2f}")
        print(f"     Sell proceeds (after fee): ${sell_proceeds:.2f}")
        print(f"     Net P&L: ${total_pnl:+.2f} ({total_pnl_percent:+.2f}%)")
        
        if total_pnl < 0:
            print(f"\n  ⚠️  You lost ${abs(total_pnl):.2f} (fees + slippage)")
        else:
            print(f"\n  🎉 You gained ${total_pnl:.2f}!")
        
        # Log the trade
        logger.log_trade(
            strategy='real_test',
            coin=coin,
            action='sell',
            price=result['price'],
            quantity=buy_info['quantity'],
            pnl=total_pnl,
            trigger_reason='manual_real_test',
            strategy_version='test',
            deployment_phase='test',
            execution_time_ms=0,
            slippage_percent=0,
            fee_usd=result['fee_usd'],
            balance=0
        )
        
        print(f"\n  ✅ Trade logged to data/trade_log.csv")
        
        return {
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'buy_cost': buy_cost,
            'sell_proceeds': sell_proceeds
        }
    else:
        print(f"\n  ❌ SELL ORDER FAILED!")
        print(f"     Error: {result['error']}")
        print(f"\n  ⚠️  CRITICAL: You still have {buy_info['quantity']:.8f} {coin.split('-')[0]}")
        print(f"  ⚠️  Value: ~${current_value:.2f}")
        print(f"  ⚠️  You MUST manually sell this on Coinbase.com!")
        
        # Log error
        logger.log_error(
            error_type='trade_execution',
            severity='critical',
            message=f"Real sell test failed: {result['error']} - MANUAL SELL REQUIRED",
            traceback='',
            recovery_action='MANUAL_SELL_REQUIRED'
        )
        
        return None


def main():
    """Main test execution"""
    print_warning()
    
    # Configuration
    test_coin = 'BTC-USD'  # Less volatile than altcoins
    test_amount = 10.0     # $10 test
    
    print("\n" + "=" * 70)
    print("  REAL TRADING TEST CONFIGURATION")
    print("=" * 70)
    print(f"\n  Coin: {test_coin}")
    print(f"  Amount: ${test_amount:.2f}")
    print(f"  Mode: LIVE (real Coinbase)")
    print(f"  Network: PRODUCTION")
    
    # Get confirmation
    if not get_user_confirmation(test_amount):
        sys.exit(0)
    
    # Step 1: Test API
    if not test_api_connection():
        print("\n  ❌ API test failed. Cannot proceed.")
        sys.exit(1)
    
    # Step 2: Execute buy
    buy_result = execute_real_buy(test_coin, test_amount)
    
    if not buy_result:
        print("\n  ❌ Buy failed. Test aborted.")
        sys.exit(1)
    
    # Step 3: Execute sell
    sell_result = execute_real_sell(test_coin, buy_result)
    
    # Final summary
    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)
    
    if sell_result:
        print(f"\n  ✅ Successfully completed buy/sell cycle!")
        print(f"\n  📊 Final Results:")
        print(f"     Coin: {test_coin}")
        print(f"     Buy cost: ${sell_result['buy_cost']:.2f}")
        print(f"     Sell proceeds: ${sell_result['sell_proceeds']:.2f}")
        print(f"     Net P&L: ${sell_result['total_pnl']:+.2f} ({sell_result['total_pnl_percent']:+.2f}%)")
        
        print(f"\n  📝 What happened:")
        print(f"     1. Bought ${buy_result['amount_usd']:.2f} of {test_coin}")
        print(f"     2. Paid ${buy_result['fee_usd']:.2f} in buy fees")
        print(f"     3. Waited 10 seconds")
        print(f"     4. Sold all {buy_result['quantity']:.8f} {test_coin.split('-')[0]}")
        print(f"     5. Paid fees and slippage")
        print(f"     6. Net result: ${sell_result['total_pnl']:+.2f}")
        
        print(f"\n  ✅ Coinbase API is working correctly!")
        print(f"  ✅ Bot can execute real trades!")
        print(f"  ✅ Ready for live trading deployment!")
        
        print(f"\n  📋 Check your logs:")
        print(f"     Trade log: data/trade_log.csv")
        print(f"     Coinbase: https://www.coinbase.com/transactions")
        
    else:
        print(f"\n  ⚠️  Sell failed - check Coinbase manually")
        print(f"  📋 Check data/error_log.csv for details")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ❌ Test cancelled by user (Ctrl+C)")
        print("  ⚠️  Check Coinbase.com to see if any orders executed")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n  ❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n  ⚠️  Check Coinbase.com to see if any orders executed")
        sys.exit(1)
