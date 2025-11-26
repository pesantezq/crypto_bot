# 🤖 Crypto Trading Bot - Windows Edition

**Version 2.0** | **Production-Ready** | **Windows-Optimized**

Automated cryptocurrency trading bot with dual-strategy system, dynamic allocation, and comprehensive risk management.

---

## 🚀 Quick Start (5 Minutes)

```powershell
# 1. Install Python 3.11+
# Download from: https://www.python.org/downloads/windows/

# 2. Extract bot to C:\crypto_bot

# 3. Setup virtual environment
cd C:\crypto_bot
python -m venv venv
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run health check
python main.py --health

# 6. Start paper trading
python main.py --paper
```

---

## 📚 Documentation Structure

- **[START_HERE.md](START_HERE.md)** - Navigation guide (read this first!)
- **[INSTALLATION.md](INSTALLATION.md)** - 5-minute setup guide
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - Complete Windows setup (30 min)
- **[rollout_1week.md](rollout_1week.md)** - 7-day deployment plan
- **[HOW_TO_USE.md](HOW_TO_USE.md)** - Command reference & daily operations
- **[UPDATE_GUIDE.md](UPDATE_GUIDE.md)** - How to update safely

---

## 🎯 What This Bot Does

**Automated Trading**: Monitors 5 cryptocurrencies (BTC, ETH, SOL, AVAX, DOGE) and executes trades based on technical indicators.

**Dual Strategy System**:
- **Conservative** (70%): BTC & ETH with safer entry/exit rules
- **Aggressive** (30%): SOL, AVAX, DOGE with higher-risk strategies

**Dynamic Allocation**: Automatically rebalances, skims profits, and caps aggressive allocation to manage risk.

**Multiple Modes**:
- **Backtest**: Test on historical data
- **Paper**: Simulate with live prices (no real money)
- **Sandbox**: Test with Coinbase sandbox (fake money, real API)
- **Live**: Real trading with phased capital deployment

---

## 📊 Deployment Phases

| Phase | Capital | Max Daily Loss | Use Case |
|-------|---------|----------------|----------|
| **Sandbox** | $1,000 (fake) | $50 | API testing, no risk |
| **Micro-live** | $10 | $3 | First real money test |
| **Light-live** | $50 | $10 | Monitored expansion |
| **Full-live** | $2,000 | $200 | Production deployment |

---

## 🔧 How It Works

### Conservative Strategy (BTC-USD, ETH-USD)

**Buy Signals** (ALL must trigger):
- RSI < 30
- Price dropped 2.5% from 24-hour high
- EMA crossover (9 crosses above 21) OR volume spike (1.5x average)

**Sell Signals** (ANY triggers):
- RSI > 70
- +8% profit (take profit)
- -5% loss (stop loss)
- EMA crossunder (9 crosses below 21)

### Aggressive Strategy (SOL-USD, AVAX-USD, DOGE-USD)

**Buy Signals** (ANY triggers):
- RSI < 25 + 2% dip from 4-hour high
- ATR breakout (current > 1.5x of 20-period average)
- Price breakout (exceeds 20-period high by 0.5%+)

**Sell Signals** (ANY triggers):
- RSI > 75
- +4% profit
- Trailing stop (-3% from highest point)
- 48-hour time limit

### Dynamic Allocation

**Profit Skimming**:
- Trigger: When aggressive reaches 140% of baseline
- Action: Transfer 27% of excess to conservative
- Example: $300 → $420 = $120 excess → skim $32.40

**Aggressive Cap**:
- Maximum: 50% of total portfolio
- Excess automatically moved to conservative

**Quarterly Rebalancing**:
- Every 90 days: Reset to 70/30 allocation

---

## 🛡️ Risk Management Features

1. **Kill Switch**: Create `data\kill_switch.flag` to stop instantly
2. **Daily Loss Limit**: Stops trading for 24h if exceeded
3. **Total Loss Limit**: Hard stop requiring manual intervention
4. **Position Sizing**: Max 10% per trade, capped by phase limits
5. **Confirmation Mode**: Prompts before each trade (micro-live)
6. **Dry-Run Mode**: Test logic without executing trades
7. **Audit Trail**: Complete logs of all trades and signals

---

## 📁 Folder Structure

```
crypto_bot/
├── main.py                  # Single entry point
├── requirements.txt         # Dependencies
├── README.md                # This file
│
├── config/                  # Configuration files
│   ├── settings_conservative.json
│   ├── settings_aggressive.json
│   ├── allocation.json
│   ├── deployment.json
│   └── credentials.example.json
│
├── strategies/              # Trading strategies
│   ├── conservative.py
│   └── aggressive.py
│
├── services/                # Core services
│   ├── logger.py           # CSV logging
│   ├── state.py            # Portfolio state
│   ├── risk.py             # Risk management
│   ├── price_api.py        # Price data
│   ├── coinbase_api.py     # Exchange API
│   ├── indicators.py       # Technical indicators
│   ├── credentials.py      # Secure credentials
│   └── alerts.py           # Email/Telegram
│
├── tools/                   # Utilities
│   ├── backtest.py         # Backtesting
│   ├── optimize_params.py  # Parameter optimization
│   ├── visualize.py        # Charts
│   └── dashboard.py        # Streamlit dashboard
│
├── data/                    # Generated data
│   ├── trade_log.csv
│   ├── signal_log.csv
│   ├── snapshot_log.csv
│   ├── error_log.csv
│   └── portfolio_state.json
│
└── logs/                    # Log files
    └── bot.log
```

---

## 💻 Command Reference

### Basic Commands

```powershell
# Health check
python main.py --health

# Status report
python main.py --status

# Backtest (90 days)
python main.py --backtest --days 90

# Paper trading
python main.py --paper

# Sandbox testing
python main.py --sandbox --phase sandbox_test

# Live trading (micro)
python main.py --live --phase micro_live --confirm

# Live trading (full)
python main.py --live --phase full_live

# Dry-run (test without executing)
python main.py --live --phase micro_live --dry-run

# Backup data
python main.py --backup

# Restore from backup
python main.py --restore backups\backup_20240101_120000
```

### Monitoring Commands

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

### Safety Commands

```powershell
# Activate kill switch
New-Item -Path "data\kill_switch.flag" -ItemType File

# Deactivate kill switch
Remove-Item "data\kill_switch.flag"

# Check kill switch status
Test-Path data\kill_switch.flag
```

---

## ⚙️ Configuration

### Settings Files

**config/settings_conservative.json**:
- RSI buy/sell thresholds
- EMA periods (9/21)
- Take profit: 8%
- Stop loss: 5%
- Min trade interval: 5 minutes

**config/settings_aggressive.json**:
- RSI buy/sell thresholds (25/75)
- ATR multiplier: 1.5x
- Breakout window: 20 periods
- Take profit: 4%
- Trailing stop: 3%
- Max hold: 48 hours

**config/allocation.json**:
- Conservative: 70%
- Aggressive: 30%
- Aggressive cap: 50%
- Skim trigger: 140%
- Skim fraction: 27%
- Rebalance interval: 90 days

**config/deployment.json**:
- Phase-specific capital and limits
- Confirmation requirements
- Sandbox URLs

---

## 📝 Logging System

### CSV Logs

**trade_log.csv**: Every executed trade with full details
**signal_log.csv**: All generated signals (buy/sell/hold)
**snapshot_log.csv**: Portfolio snapshots over time
**error_log.csv**: All errors with tracebacks
**audit_log.csv**: Configuration changes and admin actions

### Log Files

**logs/bot.log**: Real-time operational log with timestamps

---

## 🔄 Task Scheduler Setup (Windows)

For automated trading, set up Windows Task Scheduler:

1. Open: `Win+R` → `taskschd.msc`
2. Create Task (not Basic Task)
3. **General**: Run whether logged on or not
4. **Triggers**: Daily at 9 AM, repeat every 5 minutes
5. **Actions**: 
   - Program: `C:\crypto_bot\venv\Scripts\python.exe`
   - Arguments: `main.py --paper`
   - Start in: `C:\crypto_bot`
6. **Conditions**: Uncheck AC power requirement
7. **Settings**: Do not start new instance if running

See **WINDOWS_SETUP.md** for complete step-by-step guide.

---

## 🆘 Troubleshooting

### "Module not found" error
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Execution policy" error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "API authentication failed"
- Check `config/credentials.json` has all 3 fields
- Verify Coinbase API permissions (View + Trade)
- Check API key expiration

### Bot not starting
```powershell
python main.py --health  # Check system status
Get-Content logs\bot.log -Tail 50  # Check logs
```

### Task Scheduler not running
- Verify "Start in" path is correct
- Check Task History tab for errors
- Ensure admin privileges

See **HOW_TO_USE.md** for complete troubleshooting guide.

---

## ❓ FAQ

**Q: Is this safe to use with real money?**
A: Follow the 7-day rollout plan. Start with backtest → paper → sandbox → micro ($10) before going to full deployment.

**Q: How much can I expect to make?**
A: Past performance doesn't guarantee future results. This bot is for educational purposes. Trade at your own risk.

**Q: What exchange does it use?**
A: Coinbase Pro (via API). You need a Coinbase account and API keys.

**Q: Can I customize the strategies?**
A: Yes! Edit `config/settings_conservative.json` and `config/settings_aggressive.json`. Run `python main.py --health` after changes.

**Q: Does it work on Mac/Linux?**
A: This version is Windows-optimized. Commands would need adjusting for other platforms.

**Q: How much does it cost?**
A: The bot is free (MIT license). You only pay Coinbase trading fees (~0.5% per trade).

**Q: Can I add more coins?**
A: Yes! Edit the "coins" array in settings files. Make sure the coin pair is available on Coinbase.

**Q: What if I lose money?**
A: Risk management features limit losses (daily/total loss limits), but losses are possible. Only invest what you can afford to lose.

**Q: How do I stop it?**
A: Create kill switch file: `New-Item -Path "data\kill_switch.flag" -ItemType File`

**Q: Can I run multiple bots?**
A: Not recommended from the same folder (state conflicts). Use separate installations.

---

## 📜 License

MIT License - Free to use, modify, and distribute.

---

## ⚠️ Disclaimer

**FOR EDUCATIONAL PURPOSES ONLY**

Cryptocurrency trading involves substantial risk of loss. This bot is provided "as is" without warranty. The developers are not responsible for any financial losses incurred. Always:
- Test thoroughly with paper trading
- Start with minimal capital
- Never invest more than you can afford to lose
- Understand the risks before trading
- Consult a financial advisor

---

## 🤝 Support

- **Documentation**: Read START_HERE.md for navigation
- **Issues**: Check troubleshooting sections
- **Updates**: See UPDATE_GUIDE.md for safe update procedure

---

**Happy Trading! 🚀**

*Remember: Follow the 7-day rollout plan. Safety first!*
