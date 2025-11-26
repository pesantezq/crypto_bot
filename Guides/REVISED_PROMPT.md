# 🔄 RECREATION PROMPT - REVISED & IMPROVED v2.0

Copy the prompt below into a new Claude chat to recreate this entire Windows crypto trading bot system.

---

## 📋 PROMPT START

```
Create a complete, production-ready crypto trading bot system optimized for Windows users. The system must be:

1. SYSTEM REQUIREMENTS
- Python 3.9+ (Python 3.11+ recommended for Windows)
- Windows 10/11 (64-bit)
- 100MB free disk space
- Active internet connection
- Single main.py entry point for all modes (backtest, paper, sandbox, live)
- Clean folder structure with no duplicate code
- Minimal documentation (5 core docs + supporting references)
- Easy for non-technical Windows users

2. DUAL-STRATEGY SYSTEM

CONSERVATIVE STRATEGY (BTC-USD, ETH-USD) - 70% allocation:

Buy Signals (ALL must be true):
1. RSI < 30 (14-period)
2. Price dropped 2.5% from 24-hour high
3. EITHER:
   - EMA crossover: 9-EMA crosses above 21-EMA and holds for 2 consecutive periods
   - OR Volume spike: Current volume > 1.5x of 20-day average volume

Sell Signals (ANY triggers):
1. RSI > 70 (14-period)
2. Take profit: Price is 8% above entry price (fixed target)
3. Stop loss: Price is 5% below entry price (FIXED, not trailing)
4. EMA crossunder: 9-EMA crosses below 21-EMA

Position Sizing:
- 50% BTC-USD, 50% ETH-USD (of conservative allocation)
- Per trade size = min(conservative_value * 0.10, max_position_size, available_cash)

AGGRESSIVE STRATEGY (SOL-USD, AVAX-USD, DOGE-USD) - 30% allocation:

Buy Signals (ANY triggers):
1. RSI dip: RSI < 25 AND price dropped 2% from 4-hour high
2. ATR breakout: Current ATR > 1.5x of 20-period ATR moving average
3. Price breakout: Price exceeds 20-period high by 0.5%+ with volume confirmation

Sell Signals (ANY triggers):
1. RSI > 75 (14-period)
2. Take profit: Price is 4% above entry price
3. Trailing stop: Price drops 3% from highest point reached since entry
4. Time-based exit: Held for 48 hours (2 days), sell regardless of profit

Position Sizing:
- 33.3% each: SOL-USD, AVAX-USD, DOGE-USD (of aggressive allocation)
- Per trade size = min(aggressive_value * 0.10, max_position_size, available_cash)

Trade Execution Rules:
- No overlapping trades on same coin (wait for complete exit before re-entry)
- Minimum 5 minutes between trades on same coin (prevents overtrading)
- Market orders only (for simplicity and guaranteed execution)
- Log execution time and slippage for all live trades

3. DYNAMIC ALLOCATION SYSTEM

Baseline Allocation:
- Conservative: 70% of total portfolio value
- Aggressive: 30% of total portfolio value
- Rebalance frequency: Every 90 days (quarterly)

Profit Skimming (checked every trade):
- Trigger condition: aggressive_current_value >= (aggressive_initial_value * 1.40)
- Calculation: 
  * excess = aggressive_current_value - aggressive_initial_value
  * skim_amount = excess * 0.27
- Action: Transfer skim_amount from aggressive → conservative
- Baseline stays fixed: aggressive_initial_value does not change after skim
- Example:
  * Start: Aggressive = $300 (initial)
  * Grows to: $420 (140% of $300 baseline)
  * Excess: $420 - $300 = $120
  * Skim: $120 × 0.27 = $32.40
  * Result: Aggressive = $387.60, Conservative = $732.40 (gained $32.40)
  * Next skim triggers at: $420 again (baseline unchanged)

Aggressive Cap (checked every trade):
- Trigger condition: (aggressive_value / total_value) > 0.50
- Calculation: excess = aggressive_value - (total_value * 0.50)
- Action: Transfer excess from aggressive → conservative
- Purpose: Prevent aggressive from dominating portfolio
- Example:
  * Total = $1000
  * Aggressive = $550 (55% of portfolio)
  * Excess = $550 - ($1000 * 0.50) = $50
  * Result: Aggressive = $500 (50%), Conservative = $500 (50%)

Quarterly Rebalancing (every 90 days):
- Calculate targets:
  * target_conservative = total_portfolio_value * 0.70
  * target_aggressive = total_portfolio_value * 0.30
- Sell positions in over-allocated strategy
- Buy positions in under-allocated strategy
- Rebalance to exact 70/30 split
- Log action: "Quarterly rebalance: Moved $X from [source] to [destination]"
- Set next rebalance date: today + 90 days

No Loss Chasing Rule:
- Conservative losses NEVER trigger transfers from aggressive
- Aggressive losses NEVER trigger additions from conservative
- Only profits can trigger skims/transfers
- Each strategy is accountable for its own performance
- Portfolio value can go below starting capital (no artificial protection)

4. FOLDER STRUCTURE
crypto_bot/
├── main.py                          # Single entry point, all modes (~400 lines)
├── requirements.txt                 # Python dependencies with version pins
├── .gitignore                       # Git ignore file
├── README.md                        # Main documentation (Windows-focused, 20 min read)
├── rollout_1week.md                 # 7-day deployment plan (complete guide)
├── INSTALLATION.md                  # 5-minute setup guide
├── WINDOWS_SETUP.md                 # Complete Windows guide (30 min)
├── START_HERE.md                    # Navigation guide (2 min read)
├── HOW_TO_USE.md                    # Command reference and daily operations
├── UPDATE_GUIDE.md                  # How to update the bot safely
│
├── strategies/
│   ├── __init__.py
│   ├── conservative.py              # Conservative strategy with all logic
│   └── aggressive.py                # Aggressive strategy with all logic
│
├── services/
│   ├── __init__.py
│   ├── coinbase_api.py              # Coinbase API wrapper (sandbox/live)
│   ├── price_api.py                 # CryptoCompare primary, CoinGecko fallback
│   ├── indicators.py                # RSI, EMA, ATR, volume, breakout detection
│   ├── logger.py                    # Unified CSV logging system
│   ├── risk.py                      # Risk management and position sizing
│   ├── state.py                     # Portfolio state with file locking
│   ├── alerts.py                    # Email and optional Telegram alerts
│   └── credentials.py               # Secure credential management
│
├── config/
│   ├── settings_conservative.json   # Conservative parameters
│   ├── settings_aggressive.json     # Aggressive parameters
│   ├── allocation.json              # 70/30 allocation rules
│   ├── deployment.json              # Phase configs (sandbox/micro/light/full)
│   └── credentials.example.json     # API key template (copy to credentials.json)
│
├── tools/
│   ├── __init__.py
│   ├── backtest.py                  # Backtesting engine with metrics
│   ├── optimize_params.py           # Parameter optimization from trade logs
│   ├── visualize.py                 # Chart generation (matplotlib)
│   └── dashboard.py                 # Streamlit dashboard
│
├── data/                            # Created on first run
│   ├── trade_log.csv
│   ├── signal_log.csv
│   ├── snapshot_log.csv
│   ├── error_log.csv
│   ├── audit_log.csv
│   ├── portfolio_state.json
│   └── kill_switch.flag             # Create this file to stop bot
│
├── logs/                            # Created on first run
│   └── bot.log
│
└── backups/                         # Created by --backup command
    └── backup_YYYYMMDD_HHMMSS/

5. MAIN.PY REQUIREMENTS

Command-line Interface:
- Required arguments: mode (--backtest, --paper, --sandbox, --live)
- Optional arguments:
  * --phase: Deployment phase (sandbox_test, micro_live, light_live, full_live)
  * --interval: Check interval in seconds (default: 300 = 5 minutes)
  * --confirm: Require user confirmation before each trade (micro_live default)
  * --dry-run: Run live logic but skip actual order execution
  * --days: Number of days for backtesting (default: 90)
  * --health: Run system health check
  * --status: Show portfolio status report
  * --backup: Create backup of data files
  * --restore: Restore from backup folder

Startup Sequence:
1. Parse command-line arguments
2. Validate configuration files (check_config_validity)
3. Check API connectivity (ping Coinbase, CryptoCompare)
4. Load credentials securely (from Windows Credential Manager or credentials.json)
5. Initialize logging system
6. Load portfolio state or create new
7. Validate phase-specific limits
8. Check kill switch status (data/kill_switch.flag)
9. Display startup summary
10. Begin main loop

Main Loop:
- Check kill switch every iteration
- Fetch current prices for all coins
- Calculate indicators (RSI, EMA, ATR, volume)
- Generate signals for each strategy
- Check allocation rules (skim, cap, rebalance)
- Execute trades if signals + allocation permit
- Update portfolio state
- Log everything
- Sleep for interval seconds
- Repeat

Kill Switch Logic:
- Before each trade: Check if data/kill_switch.flag exists
- If exists: Log "Kill switch activated", exit gracefully
- Manual creation: New-Item -Path "data\kill_switch.flag" -ItemType File
- Deactivation: Remove-Item "data\kill_switch.flag"

Examples:
```powershell
# Backtest 90 days
python main.py --backtest --days 90

# Paper trading, check every 5 minutes
python main.py --paper --interval 300

# Sandbox testing (Coinbase test environment)
python main.py --sandbox --phase sandbox_test

# Micro-live with confirmation
python main.py --live --phase micro_live --confirm

# Light-live (automated)
python main.py --live --phase light_live

# Full deployment
python main.py --live --phase full_live

# Dry-run mode (test logic without trades)
python main.py --live --phase micro_live --dry-run

# Health check
python main.py --health

# Status report
python main.py --status

# Backup data
python main.py --backup
```

6. DEPLOYMENT PHASES (config/deployment.json)

```json
{
  "sandbox_test": {
    "description": "Coinbase Sandbox (fake money, real API)",
    "capital": 1000,
    "max_daily_loss": 50,
    "max_total_loss": 100,
    "max_position_size": 100,
    "require_confirmation": true,
    "enable_kill_switch": true,
    "use_sandbox": true,
    "sandbox_url": "https://api-public.sandbox.pro.coinbase.com"
  },
  "micro_live": {
    "description": "First real money test - minimal capital",
    "capital": 10,
    "max_daily_loss": 3,
    "max_total_loss": 5,
    "max_position_size": 5,
    "require_confirmation": true,
    "enable_kill_switch": true,
    "use_sandbox": false
  },
  "light_live": {
    "description": "Increased capital - monitoring phase",
    "capital": 50,
    "max_daily_loss": 10,
    "max_total_loss": 20,
    "max_position_size": 20,
    "require_confirmation": false,
    "enable_kill_switch": true,
    "use_sandbox": false
  },
  "full_live": {
    "description": "Full deployment - production trading",
    "capital": 2000,
    "max_daily_loss": 200,
    "max_total_loss": 400,
    "max_position_size": 500,
    "require_confirmation": false,
    "enable_kill_switch": true,
    "use_sandbox": false
  }
}
```

7. LOGGING SYSTEM (services/logger.py)

CSV Log Files with Headers:

trade_log.csv:
- timestamp (ISO 8601 format with timezone)
- strategy (conservative/aggressive)
- coin (BTC-USD, ETH-USD, etc.)
- action (BUY/SELL)
- price (execution price)
- quantity (amount traded)
- pnl (profit/loss for this trade, 0 for buys)
- trigger_reason (which signal triggered: "RSI<30 + DCA", "EMA crossover", etc.)
- strategy_version (from settings JSON)
- deployment_phase (sandbox_test, micro_live, etc.)
- execution_time_ms (time from signal to execution)
- slippage_percent ((execution_price - signal_price) / signal_price * 100)
- fee_usd (exchange fees in USD)
- balance (portfolio value after trade)
- notes (any additional info)

signal_log.csv:
- timestamp
- strategy (conservative/aggressive)
- coin
- signal (BUY/SELL/HOLD)
- rsi (current RSI value)
- ema_fast (9-period EMA)
- ema_slow (21-period EMA)
- atr (current ATR)
- price (current price)
- volume (current 24h volume)
- trigger_met (True/False - did it qualify for trade?)
- blocked_reason (if trigger_met but trade blocked: "max_loss_reached", "kill_switch", etc.)

snapshot_log.csv:
- timestamp
- conservative_value (total conservative holdings in USD)
- aggressive_value (total aggressive holdings in USD)
- total_value (sum of both)
- allocation_pct (aggressive / total * 100)
- pnl_conservative (profit/loss from start)
- pnl_aggressive (profit/loss from start)
- rebalance_due_in_days (days until next quarterly rebalance)
- last_skim_date (when last profit skim occurred, or null)

error_log.csv:
- timestamp
- error_type (API_ERROR, CALCULATION_ERROR, FILE_ERROR, etc.)
- severity (INFO, WARNING, ERROR, CRITICAL)
- message (short description)
- traceback (full stack trace if available)
- recovery_action (what the bot did: "retried", "skipped trade", "stopped", etc.)

audit_log.csv:
- timestamp
- action (CONFIG_CHANGE, CREDENTIAL_ACCESS, MANUAL_OVERRIDE, etc.)
- user (system or username if manual)
- details (what changed)
- old_value
- new_value

8. RISK MANAGEMENT (services/risk.py)

Daily Loss Tracking:
- "Day" defined as UTC 00:00:00 to UTC 23:59:59 (aligns with exchanges)
- daily_loss_usd = sum of all realized losses since UTC midnight
- Check before every trade: if daily_loss_usd >= max_daily_loss, block all trades
- Automatic reset at UTC 00:00:00
- Log: "Daily loss limit reached: $X / $Y max - Trading suspended until UTC midnight"
- Send alert notification

Total Loss Tracking:
- total_loss_usd = sum of all realized losses since bot start
- Check before every trade: if total_loss_usd >= max_total_loss, HARD STOP
- Log: "CRITICAL: Total loss limit reached: $X / $Y max - BOT STOPPED"
- Send critical alert
- Require manual intervention to restart (delete data/loss_override.flag)

Position Sizing:
- Calculate per trade:
  ```
  max_trade_usd = min(
    allocation_value * 0.10,      # Max 10% of allocation per trade
    max_position_size,            # Phase-specific limit from deployment.json
    available_cash,               # Don't overdraft
    remaining_daily_loss_budget   # Don't exceed daily loss limit
  )
  ```
- Round to exchange minimum (e.g., $5 minimum for Coinbase)
- Validate before execution

Kill Switch:
- Check for data/kill_switch.flag before every trade
- If file exists: Log "Kill switch detected", save state, exit(0)
- Manual activation: New-Item -Path "data\kill_switch.flag" -ItemType File
- Remote kill switch (optional): Check webhook URL every iteration

Slippage Tracking:
- Backtest: No slippage (uses exact historical prices)
- Paper: Estimate slippage (0.1% for BTC/ETH, 0.3% for others)
- Sandbox/Live: Actual slippage = (execution_price - signal_price) / signal_price * 100
- Log every execution with slippage_percent
- Alert if slippage > 1% on any trade

Fee Tracking:
- Coinbase: ~0.5% per trade (taker fee)
- Calculate: fee_usd = trade_amount * 0.005
- Deduct from portfolio value
- Log in trade_log.csv

Overtrading Prevention:
- Max trades per day: 20 (configurable)
- Min time between trades on same coin: 5 minutes (300 seconds)
- Track last_trade_time per coin in state manager

9. WINDOWS-SPECIFIC REQUIREMENTS

File Paths:
- Use os.path.join() or pathlib.Path for all file operations
- Support long paths: Enable if needed via registry
- Example: os.path.join('data', 'trade_log.csv') not 'data/trade_log.csv'

PowerShell Commands:
- All documentation uses PowerShell, NOT Command Prompt or Bash
- Include Set-ExecutionPolicy fix for script execution
- Use Get-Content instead of cat, New-Item instead of touch, etc.

Credential Storage (3 methods):
1. Windows Credential Manager (RECOMMENDED):
   - Install: Install-Module -Name CredentialManager
   - Store: New-StoredCredential -Target "CryptoBot_Coinbase_Key" -UserName "api_key" -Password "your_key" -Persist LocalMachine
   - Retrieve in code: import keyring; keyring.get_password("CryptoBot_Coinbase", "api_key")

2. Environment Variables (NOT recommended for Task Scheduler):
   - Temporary: $env:COINBASE_API_KEY = "your_key"
   - Permanent: [System.Environment]::SetEnvironmentVariable('COINBASE_API_KEY', 'your_key', 'User')
   - NOT inherited by Task Scheduler - use credentials.json instead

3. Configuration File:
   - Copy config/credentials.example.json to config/credentials.json
   - Add to .gitignore
   - Validate on startup

Python Version:
- Require: Python 3.9+ (use --version check in docs)
- Recommend: Python 3.11+ for better Windows performance
- Download: https://www.python.org/downloads/windows/
- Install: Check "Add Python to PATH" during installation

Virtual Environment:
```powershell
# Create venv
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deactivate
deactivate
```

Task Scheduler:
- Complete step-by-step in WINDOWS_SETUP.md
- Include screenshots or detailed descriptions
- Handle "Run whether user is logged on or not"
- Set "Run with highest privileges"
- Configure for Windows 10/11
- Set working directory correctly

Windows Defender:
```powershell
# Add folder exception
Add-MpPreference -ExclusionPath "C:\crypto_bot"

# Verify
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

10. DOCUMENTATION REQUIREMENTS

README.md (Main documentation, ~20 min read):
- Quick start (3 steps: Install, Configure, Test)
- What it does (high-level overview)
- Dual strategy explanation with examples
- Dynamic allocation with diagrams
- Deployment phases table
- Risk management features
- Folder structure overview
- Configuration guide
- All usage commands (PowerShell)
- Logging system explanation
- Task Scheduler setup (brief, link to WINDOWS_SETUP.md)
- Troubleshooting (common issues)
- FAQ (10+ questions)
- Links to other docs

rollout_1week.md (Complete 7-day plan):
- Day-by-day table with capital, pass criteria, commands
- Day 1: Backtest (must beat buy-and-hold, DD limits, PF > 1.1)
- Day 2: Paper trading (24-48h, zero errors, 5+ signals)
- Day 2.5: Sandbox testing (Coinbase test environment, fake money)
- Day 3: Micro-live ($10, confirmation mode, perfect logs)
- Day 4: Parameter optimization (analyze trade_log.csv)
- Day 5: Light-live ($50, automated, monitoring)
- Day 6: Stress testing (kill switch, API errors, edge cases)
- Day 7: Full deployment ($2000, production mode)
- Each day: Specific PowerShell commands, pass/fail criteria, rollback procedure

INSTALLATION.md (5 minutes):
1. Install Python 3.11+ (with PATH)
2. Extract crypto_bot folder to C:\
3. Open PowerShell as Administrator
4. Run setup commands:
   ```powershell
   cd C:\crypto_bot
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
5. Test: python main.py --health
6. Success indicators
7. Next steps (read WINDOWS_SETUP.md)

WINDOWS_SETUP.md (Complete guide, ~30 min):
- Python installation (step-by-step with screenshots)
- Virtual environment setup
- Dependency installation
- API key acquisition (Coinbase, CryptoCompare)
- Credential configuration (all 3 methods)
- Task Scheduler complete guide:
  * Open taskschd.msc
  * Create Task (not Basic Task)
  * General tab settings
  * Triggers tab (daily + repeat every 5 minutes)
  * Actions tab (program path, arguments, working directory)
  * Conditions tab (uncheck AC power, check wake computer)
  * Settings tab (if already running: do not start new instance)
  * Save and test
- Windows Defender exception
- Firewall rules (if needed)
- Long path support (if needed)
- Troubleshooting:
  * PowerShell execution policy errors
  * Module not found errors
  * API authentication errors
  * JSON parsing errors
  * Task Scheduler not running
  * Prices not updating

START_HERE.md (Navigation, 2 min):
- Welcome message
- What to read first (flowchart)
- Quick start: 3 steps
- Documentation structure
- Where to find help

HOW_TO_USE.md (Reference guide):
- All commands with examples
- Monitoring commands:
  * Get-Content data\trade_log.csv -Tail 20
  * Get-Content logs\bot.log -Wait
  * python main.py --status
- Configuration editing
- Safety controls (kill switch, loss limits)
- Tools usage:
  * Backtest: python tools\backtest.py
  * Optimize: python tools\optimize_params.py
  * Visualize: python tools\visualize.py
  * Dashboard: streamlit run tools\dashboard.py
- Daily routine (5 min checkup)
- Weekly routine (review logs)
- Monthly routine (parameter optimization, rebalancing)
- Troubleshooting quick reference

UPDATE_GUIDE.md (Update procedure):
- When to update
- Backup procedure (python main.py --backup)
- Update steps
- Config file migration
- Testing after update
- Rollback procedure if needed

11. KEY FEATURES TO IMPLEMENT

Backtesting (tools/backtest.py):
- Load historical price data (from CSV or API)
- Simulate conservative and aggressive strategies
- Track portfolio value over time
- Calculate metrics:
  * Total return (%)
  * Max drawdown (%)
  * Profit factor (gross profit / gross loss)
  * Win rate (%)
  * Sharpe ratio
  * Number of trades
  * Average win/loss
- Compare to buy-and-hold BTC
- Save results to data/backtest_results.csv
- Generate equity curve chart

Paper Trading (main.py --paper):
- Simulated trades with live price data
- No Coinbase API keys required (uses CryptoCompare/CoinGecko)
- Virtual USD balance (starts with phase capital)
- Full logging (trade_log, signal_log, snapshot_log)
- Estimated slippage and fees
- Perfect for testing strategy logic

Sandbox Trading (main.py --sandbox --phase sandbox_test):
- Uses Coinbase Sandbox API (fake money, real API)
- Get sandbox keys: https://public.sandbox.pro.coinbase.com
- Tests actual order execution without risk
- Validates API integration
- Required before micro_live phase

Live Trading (main.py --live --phase <phase>):
- Real Coinbase API integration
- Actual order execution
- Phase-specific capital and limits
- Confirmation mode for micro_live (prompts before each trade)
- Full audit trail

Dry-Run Mode (main.py --live --dry-run):
- Runs all live logic
- Generates signals
- Calculates trades
- Logs everything
- BUT: Skips actual order execution
- Perfect for testing live environment without risk

Health Check (main.py --health):
- Check Python version (>= 3.9)
- Verify all config files exist and valid JSON
- Test API connectivity (Coinbase, CryptoCompare)
- Check credentials loaded
- Verify data folder writable
- Check disk space (>= 50MB free)
- Validate portfolio_state.json integrity
- Check kill switch status
- List missing dependencies
- Overall: PASS/FAIL with recommendations

Status Report (main.py --status):
- Current portfolio value
- Conservative/Aggressive breakdown
- Today's PnL
- Recent trades (last 5)
- Risk status (daily loss, total loss)
- Next rebalance date
- Skim status
- Kill switch status
- Last update time

Parameter Optimization (tools/optimize_params.py):
- Analyze trade_log.csv
- Calculate win rate by:
  * Trigger type (RSI, EMA, ATR, etc.)
  * Coin
  * Time of day
  * Market conditions
- Calculate PnL by parameter set
- Suggest optimal parameters
- Save to data/optimized_params.json
- Generate recommendation report

Visualization (tools/visualize.py):
- Equity curve (portfolio value over time)
- Allocation chart (conservative vs aggressive)
- Win/loss distribution histogram
- Drawdown chart
- Trade frequency heatmap
- Performance by coin
- Save charts to data/charts/

Dashboard (tools/dashboard.py):
- Streamlit web interface (localhost:8501)
- Real-time portfolio status
- Recent trades table (last 20)
- Performance charts
- Risk metrics
- Signal history
- Error log viewer
- Configuration editor
- Manual controls (kill switch, rebalance)
- Auto-refresh every 30 seconds

Backup/Restore:
- Backup command: python main.py --backup
- Creates: backups/backup_YYYYMMDD_HHMMSS/
- Backs up: portfolio_state.json, all CSVs, config files
- Restore: python main.py --restore backups/backup_YYYYMMDD_HHMMSS
- Automatic weekly backups (Task Scheduler)

12. REQUIREMENTS.TXT

```
# Core dependencies
requests>=2.31.0,<3.0.0
pandas>=2.0.0,<3.0.0
numpy>=1.24.0,<2.0.0
python-dotenv>=1.0.0,<2.0.0

# Visualization
streamlit>=1.28.0,<2.0.0
matplotlib>=3.7.0,<4.0.0

# Security
keyring>=24.0.0,<25.0.0  # Secure credential storage
cryptography>=41.0.0,<42.0.0  # Encryption

# Optional
# twilio>=8.0.0  # SMS alerts
# python-telegram-bot>=20.0  # Telegram alerts
```

13. CONFIGURATION FILES

credentials.example.json (copy to credentials.json):
```json
{
  "coinbase": {
    "api_key": "your_coinbase_api_key_here",
    "api_secret": "your_coinbase_api_secret_here",
    "passphrase": "your_coinbase_passphrase_here"
  },
  "cryptocompare": {
    "api_key": "optional_for_higher_rate_limits"
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "your_email@gmail.com",
    "from_password": "your_app_password",
    "to_email": "your_email@gmail.com"
  }
}
```

settings_conservative.json:
```json
{
  "strategy_version": "1.0",
  "coins": ["BTC-USD", "ETH-USD"],
  "rsi_period": 14,
  "rsi_buy": 30,
  "rsi_sell": 70,
  "ema_fast": 9,
  "ema_slow": 21,
  "dca_dip_percent": 2.5,
  "dca_dip_lookback_hours": 24,
  "volume_spike_multiplier": 1.5,
  "volume_spike_period": 20,
  "take_profit_percent": 8.0,
  "stop_loss_percent": 5.0,
  "min_trade_interval_minutes": 5
}
```

settings_aggressive.json:
```json
{
  "strategy_version": "1.0",
  "coins": ["SOL-USD", "AVAX-USD", "DOGE-USD"],
  "rsi_period": 14,
  "rsi_buy": 25,
  "rsi_sell": 75,
  "dip_buy_percent": 2.0,
  "dip_lookback_hours": 4,
  "atr_period": 14,
  "atr_multiplier": 1.5,
  "atr_baseline_period": 20,
  "breakout_window": 20,
  "breakout_min_percent": 0.5,
  "take_profit_percent": 4.0,
  "stop_loss_percent": 3.0,
  "max_hold_hours": 48,
  "min_trade_interval_minutes": 5
}
```

allocation.json:
```json
{
  "conservative_pct": 0.70,
  "aggressive_pct": 0.30,
  "aggressive_cap_pct": 0.50,
  "skim_trigger_multiplier": 1.40,
  "skim_fraction": 0.27,
  "rebalance_interval_days": 90,
  "min_skim_amount_usd": 10
}
```

deployment.json: (see Section 6 above)

14. SECURITY REQUIREMENTS

Credential Storage:
- PREFERRED: Windows Credential Manager
  * Install: Install-Module -Name CredentialManager
  * Store: New-StoredCredential -Target "CryptoBot_Coinbase" -UserName "api_key" -Password "value" -Persist LocalMachine
  * Code: import keyring; key = keyring.get_password("CryptoBot_Coinbase", "api_key")
- ALTERNATIVE: credentials.json (ensure in .gitignore)
- NEVER: Environment variables for Task Scheduler (not inherited)

API Key Permissions (Coinbase):
- Backtest/Paper: No keys needed
- Sandbox: Sandbox keys (separate from production)
- Micro/Light/Full: Production keys with "View" + "Trade" permissions only
- DO NOT enable "Transfer" or "Withdraw" permissions
- Rotate keys quarterly

Dashboard Authentication:
- Add basic auth: st.experimental_user with password
- OR run localhost-only: --server.address=127.0.0.1
- Document port forwarding risks
- Never expose dashboard to internet without auth

Rate Limiting:
- Coinbase: Max 10 API calls per minute
- Implement in coinbase_api.py:
  * Track last_call_time
  * Sleep if < 6 seconds since last call
  * Queue trades if needed
- Exponential backoff on errors: 2s, 4s, 8s, 16s, 32s, then stop

Audit Trail:
- Log all config changes to audit_log.csv
- Log all credential access attempts
- Daily portfolio_state.json integrity check (checksum)
- Weekly backup rotation (keep last 4 weeks)

Kill Switch Enhancements:
- Primary: data/kill_switch.flag file
- Verify checksum of kill switch file (prevent tampering)
- Remote kill switch (optional): webhook URL that returns {"kill": true}
- Require password file alongside kill switch for extra security

Data Encryption (optional):
- Encrypt portfolio_state.json at rest
- Use cryptography library
- Store encryption key in Windows Credential Manager
- Decrypt on load, encrypt on save

15. WINDOWS COMMANDS REFERENCE

Installation:
```powershell
# Create virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Fix execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Upgrade pip
python -m pip install --upgrade pip
```

Running:
```powershell
# Health check
python main.py --health

# Status report
python main.py --status

# Backtest
python main.py --backtest --days 90

# Paper trading
python main.py --paper --interval 300

# Sandbox testing
python main.py --sandbox --phase sandbox_test

# Micro-live with confirmation
python main.py --live --phase micro_live --confirm

# Light-live
python main.py --live --phase light_live

# Full live
python main.py --live --phase full_live

# Dry-run mode
python main.py --live --phase micro_live --dry-run
```

Monitoring:
```powershell
# View last 20 trades
Get-Content data\trade_log.csv -Tail 20

# Watch live logs
Get-Content logs\bot.log -Wait

# View errors
Get-Content data\error_log.csv -Tail 10

# Check portfolio state
Get-Content data\portfolio_state.json | ConvertFrom-Json | Format-List
```

Safety:
```powershell
# Activate kill switch
New-Item -Path "data\kill_switch.flag" -ItemType File

# Deactivate kill switch
Remove-Item "data\kill_switch.flag"

# Check kill switch status
Test-Path data\kill_switch.flag

# Backup
python main.py --backup

# Restore
python main.py --restore backups\backup_20240101_120000
```

Configuration:
```powershell
# Edit conservative settings
notepad config\settings_conservative.json

# Edit aggressive settings
notepad config\settings_aggressive.json

# Edit allocation rules
notepad config\allocation.json

# Validate config
python main.py --health
```

Tools:
```powershell
# Optimize parameters
python tools\optimize_params.py

# Generate charts
python tools\visualize.py

# Launch dashboard
streamlit run tools\dashboard.py

# Backtest with visualization
python tools\backtest.py --visualize
```

Maintenance:
```powershell
# Check disk space
Get-PSDrive C

# Clear old logs (keep last 30 days)
Get-ChildItem logs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item

# Verify dependencies
pip list

# Update dependencies (careful!)
pip install --upgrade requests pandas numpy

# Check Python version
python --version
```

16. TASK SCHEDULER COMPLETE SETUP

WINDOWS_SETUP.md must include:

Step 1: Open Task Scheduler
- Press Windows Key + R
- Type: taskschd.msc
- Press Enter
- Navigate to "Task Scheduler Library"

Step 2: Create New Task
- Right-click in Task Scheduler Library
- Select "Create Task" (NOT "Create Basic Task")
- This opens advanced settings dialog

Step 3: General Tab
- Name: Crypto Bot - Paper Trading
- Description: Automated crypto trading bot (paper trading mode)
- Security options:
  * Select: "Run whether user is logged on or not"
  * Check: "Run with highest privileges"
  * Check: "Hidden" (optional)
- Configure for: Windows 10 (or Windows 11)

Step 4: Triggers Tab
- Click "New..."
- Begin the task: On a schedule
- Settings: Daily
- Start: 9:00:00 AM (or your preferred time)
- Advanced settings:
  * Check: "Repeat task every" → Select: 5 minutes
  * For a duration of: 1 day
  * Check: "Enabled"
- Click OK

Step 5: Actions Tab
- Click "New..."
- Action: Start a program
- Program/script: C:\crypto_bot\venv\Scripts\python.exe
  (Use full path to python.exe in your virtual environment)
- Add arguments (optional): main.py --paper --interval 300
- Start in (optional): C:\crypto_bot
  (CRITICAL: Must set working directory)
- Click OK

Step 6: Conditions Tab
- Power:
  * UNCHECK: "Start the task only if the computer is on AC power"
  * UNCHECK: "Stop if the computer switches to battery power"
  * CHECK: "Wake the computer to run this task"
- Network:
  * CHECK: "Start only if the following network connection is available"
  * Select: "Any connection"

Step 7: Settings Tab
- CHECK: "Allow task to be run on demand"
- CHECK: "Run task as soon as possible after a scheduled start is missed"
- CHECK: "If the task fails, restart every" → 1 minute → 3 times
- "Stop the task if it runs longer than": 1 hour
- "If the running task does not end when requested": Stop using Task Manager
- "If the task is already running": Do not start a new instance

Step 8: Save & Provide Password
- Click OK to save
- Enter your Windows username and password
- Click OK
- Task is now created

Step 9: Test the Task
- Right-click on your new task
- Select "Run"
- Check "Last Run Result" column → should show "The operation completed successfully (0x0)"
- Open logs\bot.log to verify execution

Step 10: Verify Ongoing Execution
- Task should run every 5 minutes
- Check "Next Run Time" column
- View history: Select task → Actions tab → Enable All Tasks History
- View logs: Get-Content logs\bot.log -Wait

Troubleshooting Task Scheduler:
- Task won't start: Check working directory is set correctly
- "Access denied": Run Task Scheduler as Administrator
- Task runs but bot fails: Check logs\bot.log for errors
- Python not found: Verify path to python.exe in venv
- Arguments not passed: Ensure "Add arguments" field has: main.py --paper
- Bot stops after 10 minutes: Check "Stop the task if it runs longer than" setting

17. QUALITY STANDARDS

Code Quality:
- All Python code follows PEP 8
- Docstrings for all functions (Google style)
- Type hints where appropriate
- Error handling with try/except
- Logging for all important events
- No hardcoded paths (use os.path.join or pathlib)
- No magic numbers (use constants)
- Comments for complex logic

File Paths:
- Always use os.path.join() or pathlib.Path
- Example: os.path.join('data', 'trade_log.csv')
- Never: 'data/trade_log.csv' (Linux-style)
- Test on Windows to verify

Documentation:
- All documentation uses PowerShell commands ONLY
- No Linux/Mac commands (no bash, cat, touch, etc.)
- Step-by-step instructions with examples
- Beginner-friendly language
- Screenshots or ASCII diagrams for complex steps
- Table of contents for long docs
- Links between related docs

Configuration:
- All JSON files must be valid (use json.load() to validate)
- Include comments in example files (as strings, since JSON doesn't support comments)
- Provide reasonable defaults
- Validate on startup

Error Handling:
- Graceful degradation (continue if non-critical error)
- Log all errors with full traceback
- User-friendly error messages
- Suggest recovery actions
- Never crash without saving state

Testing:
- main.py must run without errors in all modes
- All imports must work
- JSON configs must be valid
- Logging must create files correctly
- Kill switch must stop trading immediately
- Confirmation mode must prompt correctly
- Phase limits must be enforced
- Health check must catch common issues

18. TESTING REQUIREMENTS

Before Delivery:
- [ ] Python 3.9+ check passes
- [ ] All imports work (no ModuleNotFoundError)
- [ ] main.py --help shows all options
- [ ] main.py --health passes all checks
- [ ] main.py --backtest --days 30 completes
- [ ] main.py --paper runs for 5 minutes without errors
- [ ] Kill switch stops bot immediately
- [ ] Confirmation mode prompts user
- [ ] All phase limits are enforced
- [ ] All config files are valid JSON
- [ ] All docs use PowerShell commands only
- [ ] Folder structure matches specification exactly

Integration Tests:
- [ ] Backtest produces results CSV
- [ ] Paper trading logs to trade_log.csv
- [ ] Status report displays correctly
- [ ] Backup creates folder with files
- [ ] Health check identifies missing dependencies
- [ ] Dashboard launches without errors
- [ ] Optimize tool analyzes trade log
- [ ] Visualize tool generates charts

Failure Scenarios:
- [ ] Missing config file → graceful error
- [ ] Invalid JSON → clear error message
- [ ] API unreachable → logs error, continues with retry
- [ ] Insufficient balance → logs warning, skips trade
- [ ] Kill switch during trade → cancels trade, saves state
- [ ] Daily loss limit hit → stops trading, logs reason
- [ ] Total loss limit hit → hard stop, requires intervention

19. DELIVERABLES CHECKLIST

Files to Create:

Core System:
- [ ] main.py (~400 lines, complete entry point)
- [ ] requirements.txt (with pinned versions)
- [ ] .gitignore (credentials, logs, data, backups, venv)
- [ ] README.md (comprehensive, 20 min read)

Configuration:
- [ ] config/settings_conservative.json
- [ ] config/settings_aggressive.json
- [ ] config/allocation.json
- [ ] config/deployment.json
- [ ] config/credentials.example.json

Documentation:
- [ ] START_HERE.md (navigation guide)
- [ ] INSTALLATION.md (5 min quick start)
- [ ] WINDOWS_SETUP.md (30 min complete guide)
- [ ] rollout_1week.md (7-day deployment plan)
- [ ] HOW_TO_USE.md (reference guide)
- [ ] UPDATE_GUIDE.md (update procedure)
- [ ] FILE_INVENTORY.md (list all files with descriptions)

Strategies:
- [ ] strategies/__init__.py
- [ ] strategies/conservative.py (complete implementation)
- [ ] strategies/aggressive.py (complete implementation)

Services:
- [ ] services/__init__.py
- [ ] services/coinbase_api.py (API wrapper)
- [ ] services/price_api.py (CryptoCompare + fallback)
- [ ] services/indicators.py (RSI, EMA, ATR, volume)
- [ ] services/logger.py (CSV logging)
- [ ] services/risk.py (risk management)
- [ ] services/state.py (portfolio state with locking)
- [ ] services/alerts.py (email + optional Telegram)
- [ ] services/credentials.py (secure credential loading)

Tools:
- [ ] tools/__init__.py
- [ ] tools/backtest.py (backtesting engine)
- [ ] tools/optimize_params.py (parameter optimization)
- [ ] tools/visualize.py (chart generation)
- [ ] tools/dashboard.py (Streamlit dashboard)

Total: 35+ files

Verification:
- [ ] All Python files run without errors
- [ ] All JSON files are valid
- [ ] All documentation is complete
- [ ] No Linux-specific commands
- [ ] All paths use os.path.join()
- [ ] PowerShell commands throughout
- [ ] No TODO or FIXME comments
- [ ] All sections implemented (not templates)

20. OUTPUT FORMAT

File Organization:
- Create all files in folder: crypto_bot_windows/
- Use exact folder structure specified in Section 4
- Include __init__.py in all package folders
- Create empty folders with .gitkeep if needed

Code Quality:
- Production-ready code (not templates or pseudocode)
- Complete implementations (no placeholder functions)
- Full error handling
- Comprehensive logging
- All features functional
- Tested and verified

Documentation Quality:
- Complete guides (not abbreviated)
- Windows-native throughout
- Beginner-friendly language
- Step-by-step instructions
- Examples for every command
- Troubleshooting sections
- No "TBD" or "Coming soon"

Configuration:
- Valid JSON format
- Reasonable default values
- Comments (as string fields where helpful)
- Example credentials file
- All phases defined

Final Package:
- Single downloadable folder
- Ready to extract and run
- No additional setup required (except Python + APIs)
- All documentation included
- Production-ready
- Windows-optimized

Additional Notes:
- Paper trading works without Coinbase API keys (uses public price APIs)
- Sandbox testing requires Coinbase Sandbox API keys (separate from production)
- Live trading requires Coinbase production API keys with "View" + "Trade" permissions
- Start with backtest → paper → sandbox → micro → light → full (follow 7-day rollout)
- All features must be functional and tested
- Documentation must be Windows-native throughout
- System must be beginner-friendly
- Prioritize safety and risk management
```

## 📋 PROMPT END

---

**This is the complete, improved prompt with all fixes incorporated! 🎯**
