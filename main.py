#!/usr/bin/env python3
"""
Crypto Trading Bot - Main Entry Point
Version: 2.0
Windows-Optimized Automated Trading System

Supports multiple modes:
- Backtest: Historical simulation
- Paper: Live simulation (no real money)
- Sandbox: Coinbase test environment
- Live: Real trading with phased deployment

Author: Crypto Bot Team
License: MIT
"""

import sys
import os
import json
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.logger import Logger
from services.state import StateManager
from services.risk import RiskManager
from services.credentials import CredentialManager
from services.price_api import PriceAPI
from services.coinbase_api import CoinbaseAPI
from strategies.conservative_old import ConservativeStrategy
from strategies.aggressive_old import AggressiveStrategy


class CryptoBot:
    """Main bot orchestrator"""
    
    VERSION = "2.0"
    
    def __init__(self, args):
        """Initialize bot with command-line arguments"""
        self.args = args
        self.mode = self._determine_mode()
        self.running = True
        
        # Initialize components
        self.logger = None
        self.state = None
        self.risk = None
        self.price_api = None
        self.exchange_api = None
        self.conservative = None
        self.aggressive = None
        self.deployment_config = None
        
    def _determine_mode(self):
        """Determine operating mode from arguments"""
        if self.args.backtest:
            return "backtest"
        elif self.args.paper:
            return "paper"
        elif self.args.sandbox:
            return "sandbox"
        elif self.args.live:
            return "live"
        else:
            return None
            
    def validate_config(self):
        """Validate all configuration files"""
        print("🔍 Validating configuration files...")
        
        errors = []
        config_dir = Path("config")
        
        # Check required config files exist
        required_files = [
            "settings_conservative.json",
            "settings_aggressive.json",
            "allocation.json",
            "deployment.json"
        ]
        
        for filename in required_files:
            filepath = config_dir / filename
            if not filepath.exists():
                errors.append(f"Missing config file: {filename}")
                continue
                
            # Validate JSON
            try:
                with open(filepath, 'r') as f:
                    config = json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in {filename}: {str(e)}")
                continue
                
        # Validate allocation rules
        try:
            with open(config_dir / "allocation.json", 'r') as f:
                alloc = json.load(f)
            
            # Check allocation sums to 100%
            total = alloc.get('conservative_pct', 0) + alloc.get('aggressive_pct', 0)
            if abs(total - 1.0) > 0.001:
                errors.append(f"Allocation must sum to 1.0, got {total}")
            
            # Check aggressive cap > baseline
            if alloc.get('aggressive_cap_pct', 0) <= alloc.get('aggressive_pct', 0):
                errors.append("Aggressive cap must be > baseline allocation")
                
        except Exception as e:
            errors.append(f"Error validating allocation.json: {str(e)}")
            
        # Validate RSI bounds
        for strategy_name in ['conservative', 'aggressive']:
            try:
                with open(config_dir / f"settings_{strategy_name}.json", 'r') as f:
                    settings = json.load(f)
                
                rsi_buy = settings.get('rsi_buy', 0)
                rsi_sell = settings.get('rsi_sell', 100)
                
                if rsi_buy >= rsi_sell:
                    errors.append(f"{strategy_name}: RSI buy ({rsi_buy}) must be < RSI sell ({rsi_sell})")
                    
            except Exception as e:
                errors.append(f"Error validating {strategy_name} settings: {str(e)}")
        
        if errors:
            print("\n❌ CONFIGURATION ERRORS:")
            for error in errors:
                print(f"  • {error}")
            print("\nPlease fix these errors and try again.")
            sys.exit(1)
        else:
            print("✅ All configuration files valid")
            
    def check_connectivity(self):
        """Check API connectivity"""
        print("\n🌐 Checking API connectivity...")
        
        # Check price API
        try:
            self.price_api = PriceAPI()
            test_price = self.price_api.get_price("BTC-USD")
            if test_price:
                print(f"✅ Price API: Connected (BTC: ${test_price:,.2f})")
            else:
                print("⚠️  Price API: Failed (will retry)")
        except Exception as e:
            print(f"⚠️  Price API error: {str(e)}")
            
        # Check exchange API (only for sandbox/live)
        if self.mode in ["sandbox", "live"]:
            try:
                use_sandbox = self.deployment_config.get('use_sandbox', False)
                self.exchange_api = CoinbaseAPI(sandbox=use_sandbox)
                
                # Test connection
                if self.exchange_api.test_connection():
                    print(f"✅ Coinbase API: Connected ({'Sandbox' if use_sandbox else 'Production'})")
                else:
                    print("❌ Coinbase API: Failed")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Coinbase API error: {str(e)}")
                sys.exit(1)
                
    def check_kill_switch(self):
        """Check if kill switch is activated"""
        kill_switch_path = Path("data") / "kill_switch.flag"
        if kill_switch_path.exists():
            return True
        return False
        
    def load_deployment_config(self):
        """Load deployment configuration"""
        config_path = Path("config") / "deployment.json"
        
        try:
            with open(config_path, 'r') as f:
                all_configs = json.load(f)
            
            # Get phase-specific config
            phase = self.args.phase or "sandbox_test"
            
            if phase not in all_configs:
                print(f"❌ Unknown deployment phase: {phase}")
                print(f"Available phases: {', '.join(all_configs.keys())}")
                sys.exit(1)
            
            self.deployment_config = all_configs[phase]
            self.deployment_config['phase'] = phase
            
            print(f"\n📋 Deployment Configuration:")
            print(f"  Phase: {phase}")
            print(f"  Description: {self.deployment_config.get('description', 'N/A')}")
            print(f"  Capital: ${self.deployment_config.get('capital', 0):,.2f}")
            print(f"  Max Daily Loss: ${self.deployment_config.get('max_daily_loss', 0):,.2f}")
            print(f"  Max Total Loss: ${self.deployment_config.get('max_total_loss', 0):,.2f}")
            print(f"  Confirmation Required: {self.deployment_config.get('require_confirmation', False)}")
            
        except Exception as e:
            print(f"❌ Error loading deployment config: {str(e)}")
            sys.exit(1)
            
    def initialize(self):
        """Initialize all components"""
        print(f"\n{'='*60}")
        print(f"🤖 Crypto Trading Bot v{self.VERSION}")
        print(f"{'='*60}")
        print(f"Mode: {self.mode.upper()}")
        print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"{'='*60}\n")
        
        # Validate configuration
        self.validate_config()
        
        # Load deployment config (for sandbox/live)
        if self.mode in ["sandbox", "live"]:
            self.load_deployment_config()
        else:
            # Use default config for backtest/paper
            self.deployment_config = {
                'phase': self.mode,
                'capital': 10000,  # Virtual capital for backtest/paper
                'max_daily_loss': 500,
                'max_total_loss': 1000,
                'max_position_size': 1000,
                'require_confirmation': False,
                'enable_kill_switch': True,
                'use_sandbox': False
            }
        
        # Check connectivity
        self.check_connectivity()
        
        # Initialize logger
        self.logger = Logger(mode=self.mode, phase=self.deployment_config['phase'])
        print("✅ Logger initialized")
        
        # Initialize state manager
        self.state = StateManager(
            initial_capital=self.deployment_config['capital'],
            logger=self.logger
        )
        print("✅ State manager initialized")
        
        # Initialize risk manager
        self.risk = RiskManager(
            max_daily_loss=self.deployment_config['max_daily_loss'],
            max_total_loss=self.deployment_config['max_total_loss'],
            max_position_size=self.deployment_config['max_position_size'],
            logger=self.logger
        )
        print("✅ Risk manager initialized")
        
        # Initialize strategies
        self.conservative = ConservativeStrategy(
            logger=self.logger,
            price_api=self.price_api
        )
        print("✅ Conservative strategy initialized")
        
        self.aggressive = AggressiveStrategy(
            logger=self.logger,
            price_api=self.price_api
        )
        print("✅ Aggressive strategy initialized")
        
        print("\n✅ All components initialized successfully!\n")
        
    def run_backtest(self):
        """Run backtesting mode"""
        print(f"🔄 Running backtest for {self.args.days} days...")
        print("⚠️  Backtest functionality requires tools/backtest.py")
        print("Run: python tools/backtest.py --days", self.args.days)
        
    def run_paper(self):
        """Run paper trading mode"""
        print("📝 Starting paper trading mode...")
        print(f"Check interval: {self.args.interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            iteration = 0
            while self.running:
                iteration += 1
                print(f"[Iteration {iteration}] {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
                
                # Check kill switch
                if self.check_kill_switch():
                    print("\n⚠️  Kill switch activated - stopping bot")
                    break
                
                # Run trading cycle
                self._run_trading_cycle()
                
                # Wait for next iteration
                time.sleep(self.args.interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        finally:
            self._shutdown()
            
    def run_sandbox(self):
        """Run sandbox trading mode"""
        print("🧪 Starting sandbox trading mode...")
        print(f"Check interval: {self.args.interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        if self.args.dry_run:
            print("⚠️  DRY-RUN MODE: Trades will be simulated, not executed\n")
        
        try:
            iteration = 0
            while self.running:
                iteration += 1
                print(f"[Iteration {iteration}] {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
                
                # Check kill switch
                if self.check_kill_switch():
                    print("\n⚠️  Kill switch activated - stopping bot")
                    break
                
                # Run trading cycle
                self._run_trading_cycle()
                
                # Wait for next iteration
                time.sleep(self.args.interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        finally:
            self._shutdown()
            
    def run_live(self):
        """Run live trading mode"""
        print("💰 Starting LIVE trading mode...")
        print(f"Phase: {self.deployment_config['phase']}")
        print(f"Capital: ${self.deployment_config['capital']:,.2f}")
        print(f"Check interval: {self.args.interval} seconds")
        
        if self.args.dry_run:
            print("⚠️  DRY-RUN MODE: Trades will be simulated, not executed")
        
        if self.deployment_config.get('require_confirmation'):
            print("⚠️  CONFIRMATION MODE: You will be prompted before each trade")
        
        print("\nPress Ctrl+C to stop\n")
        
        # Final confirmation for live mode
        if not self.args.dry_run:
            confirm = input("⚠️  This is REAL MONEY. Type 'YES' to continue: ")
            if confirm != "YES":
                print("Aborted.")
                sys.exit(0)
        
        try:
            iteration = 0
            while self.running:
                iteration += 1
                print(f"[Iteration {iteration}] {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
                
                # Check kill switch
                if self.check_kill_switch():
                    print("\n⚠️  Kill switch activated - stopping bot")
                    break
                
                # Run trading cycle
                self._run_trading_cycle()
                
                # Wait for next iteration
                time.sleep(self.args.interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        finally:
            self._shutdown()
            
    def _run_trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # Update portfolio state
            self.state.update()
            
            # Check allocation rules
            self._check_allocation_rules()
            
            # Run conservative strategy
            conservative_signals = self.conservative.evaluate_all()
            self._process_signals(conservative_signals, 'conservative')
            
            # Run aggressive strategy
            aggressive_signals = self.aggressive.evaluate_all()
            self._process_signals(aggressive_signals, 'aggressive')
            
            # Log snapshot
            self.state.log_snapshot()
            
            print("  ✓ Cycle complete\n")
            
        except Exception as e:
            self.logger.log_error("CYCLE_ERROR", str(e))
            print(f"  ✗ Error: {str(e)}\n")
            
    def _check_allocation_rules(self):
        """Check and enforce allocation rules"""
        # This would implement profit skimming, aggressive cap, and rebalancing
        # For now, just a placeholder
        pass
        
    def _process_signals(self, signals, strategy_type):
        """Process trading signals from strategy"""
        for signal in signals:
            if signal['action'] == 'HOLD':
                continue
            
            # Check if trade is allowed
            if not self.risk.can_trade(signal['coin'], signal['amount_usd']):
                self.logger.log_signal(
                    strategy=strategy_type,
                    coin=signal['coin'],
                    signal=signal['action'],
                    rsi=signal.get('rsi', 0),
                    ema_fast=signal.get('ema_fast', 0),
                    ema_slow=signal.get('ema_slow', 0),
                    atr=signal.get('atr', 0),
                    price=signal['price'],
                    volume=signal.get('volume', 0),
                    trigger_met=True,
                    blocked_reason="risk_limit"
                )
                continue
            
            # Confirmation mode
            if self.deployment_config.get('require_confirmation') and not self.args.dry_run:
                print(f"\n⚠️  Trade Confirmation Required:")
                print(f"  {signal['action']} {signal['coin']}")
                print(f"  Amount: ${signal['amount_usd']:.2f}")
                print(f"  Price: ${signal['price']:.2f}")
                confirm = input("Execute trade? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("  Trade skipped")
                    continue
            
            # Execute trade (or simulate)
            if self.args.dry_run:
                print(f"  [DRY-RUN] Would {signal['action']} {signal['coin']} @ ${signal['price']:.2f}")
            else:
                self._execute_trade(signal, strategy_type)
                
    def _execute_trade(self, signal, strategy_type):
        """Execute a trade"""
        try:
            if self.mode == "paper":
                # Simulated execution
                self.state.execute_paper_trade(
                    coin=signal['coin'],
                    action=signal['action'],
                    price=signal['price'],
                    amount_usd=signal['amount_usd']
                )
                print(f"  ✓ [PAPER] {signal['action']} {signal['coin']} @ ${signal['price']:.2f}")
            else:
                # Real execution via exchange API
                result = self.exchange_api.place_order(
                    coin=signal['coin'],
                    side=signal['action'].lower(),
                    amount_usd=signal['amount_usd']
                )
                
                if result['success']:
                    self.state.execute_live_trade(
                        coin=signal['coin'],
                        action=signal['action'],
                        price=result['price'],
                        amount_usd=result['amount_usd'],
                        fee_usd=result['fee_usd']
                    )
                    print(f"  ✓ [LIVE] {signal['action']} {signal['coin']} @ ${result['price']:.2f}")
                else:
                    print(f"  ✗ Trade failed: {result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            self.logger.log_error("TRADE_EXECUTION", str(e))
            print(f"  ✗ Execution error: {str(e)}")
            
    def _shutdown(self):
        """Clean shutdown"""
        print("\n" + "="*60)
        print("🛑 Shutting down...")
        print("="*60)
        
        # Save final state
        if self.state:
            self.state.save()
            print("✅ State saved")
        
        # Log final snapshot
        if self.logger:
            print("✅ Logs flushed")
        
        print("\n👋 Bot stopped successfully")
        
    def run(self):
        """Main run method"""
        try:
            # Handle special commands
            if self.args.health:
                return self.run_health_check()
            elif self.args.status:
                return self.run_status()
            elif self.args.backup:
                return self.run_backup()
            elif self.args.restore:
                return self.run_restore(self.args.restore)
            
            # Initialize bot
            self.initialize()
            
            # Run appropriate mode
            if self.mode == "backtest":
                self.run_backtest()
            elif self.mode == "paper":
                self.run_paper()
            elif self.mode == "sandbox":
                self.run_sandbox()
            elif self.mode == "live":
                self.run_live()
            else:
                print("❌ No mode specified. Use --backtest, --paper, --sandbox, or --live")
                sys.exit(1)
                
        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    def run_health_check(self):
        """Run system health check"""
        print("🏥 Running system health check...\n")
        
        passed = 0
        failed = 0
        
        # Check Python version
        print("1. Python Version")
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
            passed += 1
        else:
            print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.9+)")
            failed += 1
        
        # Check config files
        print("\n2. Configuration Files")
        config_files = [
            "config/settings_conservative.json",
            "config/settings_aggressive.json",
            "config/allocation.json",
            "config/deployment.json"
        ]
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        json.load(f)
                    print(f"   ✅ {config_file}")
                    passed += 1
                except:
                    print(f"   ❌ {config_file} (invalid JSON)")
                    failed += 1
            else:
                print(f"   ❌ {config_file} (not found)")
                failed += 1
        
        # Check data directory
        print("\n3. Data Directory")
        data_dir = Path("data")
        if data_dir.exists() and data_dir.is_dir():
            print(f"   ✅ data/ directory exists")
            passed += 1
        else:
            print(f"   ⚠️  data/ directory will be created")
        
        # Check dependencies
        print("\n4. Dependencies")
        required_modules = ['requests', 'pandas', 'numpy']
        for module in required_modules:
            try:
                __import__(module)
                print(f"   ✅ {module}")
                passed += 1
            except ImportError:
                print(f"   ❌ {module} (not installed)")
                failed += 1
        
        # Check kill switch
        print("\n5. Kill Switch")
        if self.check_kill_switch():
            print("   ⚠️  Kill switch is ACTIVE (data/kill_switch.flag exists)")
        else:
            print("   ✅ Kill switch is inactive")
            passed += 1
        
        # Summary
        print("\n" + "="*60)
        print(f"Health Check Summary: {passed} passed, {failed} failed")
        print("="*60)
        
        if failed == 0:
            print("✅ System is healthy and ready to run!")
            return 0
        else:
            print("⚠️  Please fix the issues above before running")
            return 1
            
    def run_status(self):
        """Show current status"""
        print("📊 Portfolio Status\n")
        print("⚠️  Status command requires initialized state")
        print("Run the bot first to generate portfolio data")
        return 0
        
    def run_backup(self):
        """Create backup"""
        print("💾 Creating backup...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path("backups") / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy important files
        import shutil
        files_to_backup = [
            "data/portfolio_state.json",
            "data/trade_log.csv",
            "data/snapshot_log.csv",
            "data/signal_log.csv"
        ]
        
        for file in files_to_backup:
            src = Path(file)
            if src.exists():
                dst = backup_dir / src.name
                shutil.copy(src, dst)
                print(f"  ✓ {file}")
        
        print(f"\n✅ Backup created: {backup_dir}")
        return 0
        
    def run_restore(self, backup_path):
        """Restore from backup"""
        print(f"♻️  Restoring from: {backup_path}")
        print("⚠️  This will overwrite current data files")
        confirm = input("Continue? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Aborted")
            return 1
        
        # Restore files
        import shutil
        backup_dir = Path(backup_path)
        
        if not backup_dir.exists():
            print(f"❌ Backup not found: {backup_path}")
            return 1
        
        for file in backup_dir.iterdir():
            dst = Path("data") / file.name
            shutil.copy(file, dst)
            print(f"  ✓ Restored {file.name}")
        
        print("\n✅ Restore complete")
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Crypto Trading Bot - Windows Optimized",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--backtest', action='store_true',
                           help='Run backtesting mode')
    mode_group.add_argument('--paper', action='store_true',
                           help='Run paper trading mode (simulation)')
    mode_group.add_argument('--sandbox', action='store_true',
                           help='Run sandbox mode (Coinbase test environment)')
    mode_group.add_argument('--live', action='store_true',
                           help='Run live trading mode (REAL MONEY)')
    
    # Special commands
    mode_group.add_argument('--health', action='store_true',
                           help='Run system health check')
    mode_group.add_argument('--status', action='store_true',
                           help='Show portfolio status')
    mode_group.add_argument('--backup', action='store_true',
                           help='Create backup of data files')
    
    # Optional arguments
    parser.add_argument('--phase', type=str,
                       help='Deployment phase (sandbox_test, micro_live, light_live, full_live)')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--confirm', action='store_true',
                       help='Require confirmation for each trade')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate trades without executing')
    parser.add_argument('--days', type=int, default=90,
                       help='Number of days for backtesting (default: 90)')
    parser.add_argument('--restore', type=str,
                       help='Restore from backup folder')
    
    args = parser.parse_args()
    
    # Create and run bot
    bot = CryptoBot(args)
    sys.exit(bot.run() or 0)


if __name__ == "__main__":
    main()
