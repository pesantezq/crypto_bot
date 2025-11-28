"""
Complete Trading Test Script
Tests all components: signals, strategies, risk management, execution
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.conservative import ConservativeStrategy
from strategies.aggressive import AggressiveStrategy
from services.price_api import PriceAPI
from services.logger import Logger
from services.state import StateManager
from services.risk import RiskManager
import json
import time


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_price_api():
    """Test price API functionality"""
    print_header("TEST 1: Price API")
    
    price_api = PriceAPI()
    coins = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD', 'DOGE-USD']
    
    print("\n📊 Testing current prices...")
    for coin in coins:
        price = price_api.get_price(coin)
        if price:
            print(f"  ✓ {coin}: ${price:,.2f}")
        else:
            print(f"  ✗ {coin}: Failed to fetch")
    
    print("\n📈 Testing historical prices...")
    test_coin = 'BTC-USD'
    historical = price_api.get_historical_prices(test_coin, hours=48)
    
    if historical and len(historical) > 0:
        print(f"  ✓ Fetched {len(historical)} data points for {test_coin}")
        print(f"  ✓ Oldest: ${historical[0]['price']:,.2f}")
        print(f"  ✓ Newest: ${historical[-1]['price']:,.2f}")
        return True
    else:
        print(f"  ✗ Failed to fetch historical data")
        return False


def test_strategies():
    """Test strategy signal generation"""
    print_header("TEST 2: Strategy Signal Generation")
    
    logger = Logger()
    price_api = PriceAPI()
    
    print("\n🔵 Testing Conservative Strategy (BTC/ETH)...")
    conservative = ConservativeStrategy(logger, price_api, mode='paper')
    
    signals = conservative.evaluate_all()
    
    for signal in signals:
        print(f"\n  Coin: {signal['coin']}")
        print(f"  Action: {signal['action']}")
        print(f"  Price: ${signal['price']:,.2f}")
        print(f"  RSI: {signal['rsi']:.1f}")
        print(f"  EMA Fast: ${signal['ema_fast']:,.2f}")
        print(f"  EMA Slow: ${signal['ema_slow']:,.2f}")
        print(f"  Reason: {signal['reason']}")
        
        if signal['action'] != 'HOLD':
            print(f"  🎯 SIGNAL GENERATED!")
    
    print("\n🔴 Testing Aggressive Strategy (SOL/AVAX/DOGE)...")
    aggressive = AggressiveStrategy(logger, price_api, mode='paper')
    
    signals = aggressive.evaluate_all()
    
    for signal in signals:
        print(f"\n  Coin: {signal['coin']}")
        print(f"  Action: {signal['action']}")
        print(f"  Price: ${signal['price']:,.2f}")
        print(f"  RSI: {signal['rsi']:.1f}")
        print(f"  ATR: {signal['atr']:.4f}")
        print(f"  Reason: {signal['reason']}")
        
        if signal['action'] != 'HOLD':
            print(f"  🎯 SIGNAL GENERATED!")
    
    return True


def test_risk_management():
    """Test risk management system"""
    print_header("TEST 3: Risk Management")
    
    # Load deployment config
    with open('config/deployment.json', 'r') as f:
        deployment = json.load(f)
    
    phase = 'micro_live'
    config = deployment[phase]
    
    risk_manager = RiskManager(
        max_daily_loss=config['max_daily_loss'],
        max_total_loss=config['max_total_loss'],
        max_position_size=config['max_position_size']
    )
    
    print(f"\n⚙️  Phase: {phase}")
    print(f"  Max daily loss: ${config['max_daily_loss']}")
    print(f"  Max total loss: ${config['max_total_loss']}")
    print(f"  Max position size: ${config['max_position_size']}")
    
    # Test loss tracking
    print(f"\n📊 Current Loss Status:")
    print(f"  Daily loss: ${risk_manager.daily_loss:.2f}")
    print(f"  Total loss: ${risk_manager.total_loss:.2f}")
    
    # Test can_trade
    test_coin = 'BTC-USD'
    test_amount = 5.0
    can_trade = risk_manager.can_trade(test_coin, test_amount)
    
    if can_trade:
        print(f"\n✅ Can trade {test_coin} for ${test_amount}")
    else:
        print(f"\n❌ Cannot trade {test_coin} (exceeds limits)")
    
    # Test position sizing
    available_cash = config['capital']
    allocation_value = available_cash * 0.70  # Conservative allocation
    position_size = risk_manager.get_position_size(allocation_value, available_cash)
    
    print(f"\n💰 Position Sizing:")
    print(f"  Available capital: ${available_cash}")
    print(f"  Calculated position: ${position_size:.2f}")
    
    if position_size >= 5:
        print(f"  ✅ Position size meets minimum ($5)")
        return True
    else:
        print(f"  ❌ Position size too small (< $5)")
        print(f"  💡 Tip: Increase capital in deployment.json")
        return False


def test_paper_trade():
    """Test paper trading execution"""
    print_header("TEST 4: Paper Trading Execution")
    
    logger = Logger()
    price_api = PriceAPI()
    state = StateManager(initial_capital=10000, logger=logger)
    
    print(f"\n💰 Initial Portfolio:")
    print(f"  Cash: ${state.state['cash']:,.2f}")
    print(f"  Positions: {len(state.state['positions'])}")
    
    # Simulate a buy
    test_coin = 'BTC-USD'
    price = price_api.get_price(test_coin)
    
    if not price:
        print(f"\n❌ Could not fetch price for {test_coin}")
        return False
    
    amount_usd = 50.0
    
    print(f"\n🔵 Executing PAPER BUY:")
    print(f"  Coin: {test_coin}")
    print(f"  Price: ${price:,.2f}")
    print(f"  Amount: ${amount_usd}")
    
    state.execute_paper_trade(test_coin, 'BUY', price, amount_usd)
    
    print(f"\n💰 After BUY:")
    print(f"  Cash: ${state.state['cash']:,.2f}")
    print(f"  Positions: {len(state.state['positions'])}")
    
    if test_coin in state.state['positions']:
        pos = state.state['positions'][test_coin]
        print(f"  {test_coin}: {pos['quantity']:.6f} @ ${pos['avg_price']:,.2f}")
        
        # Simulate a sell
        print(f"\n🔴 Executing PAPER SELL:")
        print(f"  Coin: {test_coin}")
        print(f"  Price: ${price:,.2f}")
        print(f"  Amount: ${amount_usd}")
        
        state.execute_paper_trade(test_coin, 'SELL', price, amount_usd)
        
        print(f"\n💰 After SELL:")
        print(f"  Cash: ${state.state['cash']:,.2f}")
        print(f"  Positions: {len(state.state['positions'])}")
        
        print(f"\n✅ Paper trading execution successful!")
        return True
    else:
        print(f"\n❌ Position not created")
        return False


def test_full_trading_loop():
    """Test complete trading loop (one iteration)"""
    print_header("TEST 5: Full Trading Loop (Paper Mode)")
    
    logger = Logger()
    price_api = PriceAPI()
    state = StateManager(initial_capital=10000, logger=logger)
    
    # Load deployment config
    with open('config/deployment.json', 'r') as f:
        deployment = json.load(f)
    
    phase = 'micro_live'
    config = deployment[phase]
    
    risk_manager = RiskManager(
        max_daily_loss=config['max_daily_loss'],
        max_total_loss=config['max_total_loss'],
        max_position_size=config['max_position_size']
    )
    
    # Initialize strategies
    conservative = ConservativeStrategy(logger, price_api, mode='paper')
    aggressive = AggressiveStrategy(logger, price_api, mode='paper')
    
    print("\n🔄 Running one complete trading iteration...\n")
    
    # Evaluate conservative
    print("🔵 Conservative Strategy:")
    conservative_signals = conservative.evaluate_all()
    
    for signal in conservative_signals:
        print(f"\n  {signal['coin']}: {signal['action']}")
        
        if signal['action'] == 'BUY':
            # Calculate position size first
            allocation_value = state.state['cash'] * 0.70  # Conservative gets 70%
            position_size = risk_manager.get_position_size(allocation_value, state.state['cash'])
            
            # Check if we can trade this amount
            can_trade = risk_manager.can_trade(signal['coin'], position_size)
            
            if can_trade:
                if position_size >= 5:
                    print(f"  ✅ Executing BUY: ${position_size:.2f}")
                    state.execute_paper_trade(
                        signal['coin'], 
                        'BUY', 
                        signal['price'], 
                        position_size
                    )
                    risk_manager.record_trade(signal['coin'], 0)  # P&L tracked later
                else:
                    print(f"  ❌ Position too small: ${position_size:.2f}")
            else:
                print(f"  ❌ Blocked by risk limits")
        
        elif signal['action'] == 'SELL':
            print(f"  ✅ SELL signal generated")
            # Would execute sell here
    
    # Evaluate aggressive
    print("\n🔴 Aggressive Strategy:")
    aggressive_signals = aggressive.evaluate_all()
    
    for signal in aggressive_signals:
        print(f"\n  {signal['coin']}: {signal['action']}")
        
        if signal['action'] == 'BUY':
            # Calculate position size
            allocation_value = state.state['cash'] * 0.30  # Aggressive gets 30%
            position_size = risk_manager.get_position_size(allocation_value, state.state['cash'])
            
            # Check if we can trade
            can_trade = risk_manager.can_trade(signal['coin'], position_size)
            
            if can_trade:
                if position_size >= 5:
                    print(f"  ✅ Executing BUY: ${position_size:.2f}")
                    state.execute_paper_trade(
                        signal['coin'], 
                        'BUY', 
                        signal['price'], 
                        position_size
                    )
                    risk_manager.record_trade(signal['coin'], 0)  # P&L tracked later
                else:
                    print(f"  ❌ Position too small: ${position_size:.2f}")
            else:
                print(f"  ❌ Blocked by risk limits")
        
        elif signal['action'] == 'SELL':
            print(f"  ✅ SELL signal generated")
    
    # Summary
    print(f"\n📊 Final State:")
    print(f"  Cash: ${state.state['cash']:,.2f}")
    print(f"  Positions: {len(state.state['positions'])}")
    print(f"  Total trades: {state.state['total_trades']}")
    
    print(f"\n✅ Complete trading loop executed successfully!")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🧪 COMPREHENSIVE TRADING SYSTEM TEST")
    print("=" * 70)
    print("\n  This will test all components of the trading bot")
    print("  Duration: ~2-3 minutes")
    print("  Mode: Paper trading (no real money)")
    
    input("\n  Press Enter to start tests...")
    
    results = {
        'Price API': False,
        'Strategy Signals': False,
        'Risk Management': False,
        'Paper Trading': False,
        'Full Trading Loop': False
    }
    
    try:
        # Test 1: Price API
        results['Price API'] = test_price_api()
        time.sleep(2)
        
        # Test 2: Strategy signals
        results['Strategy Signals'] = test_strategies()
        time.sleep(2)
        
        # Test 3: Risk management
        results['Risk Management'] = test_risk_management()
        time.sleep(2)
        
        # Test 4: Paper trading
        results['Paper Trading'] = test_paper_trade()
        time.sleep(2)
        
        # Test 5: Full loop
        results['Full Trading Loop'] = test_full_trading_loop()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Final summary
    print_header("TEST SUMMARY")
    
    print()
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n  Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  ✅ Your trading bot is fully functional!")
        print("\n  Next steps:")
        print("    1. Run paper trading: python main.py --paper")
        print("    2. Monitor for 24-48 hours")
        print("    3. Review trade_log.csv for performance")
        print("    4. Deploy to live: python main.py --live --phase micro_live --confirm")
    else:
        print("\n  ⚠️  Some tests failed")
        print("\n  Please fix the issues above before deploying to live trading")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_all_tests()