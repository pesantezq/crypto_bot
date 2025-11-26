# 📖 How To Use - Complete Reference

Daily operations, commands, and troubleshooting.

---

## Daily Commands

### Check Status
```powershell
python main.py --status
```

### View Recent Trades
```powershell
Get-Content data\trade_log.csv -Tail 20
```

### Watch Live Logs
```powershell
Get-Content logs\bot.log -Wait
```

### Check for Errors
```powershell
Get-Content data\error_log.csv -Tail 10
```

---

## Running the Bot

### Paper Trading (No Real Money)
```powershell
python main.py --paper --interval 300
```

### Sandbox Testing (Fake Money, Real API)
```powershell
python main.py --sandbox --phase sandbox_test
```

### Live Trading (Real Money)
```powershell
# Micro ($10) with confirmation
python main.py --live --phase micro_live --confirm

# Light ($50) automated
python main.py --live --phase light_live

# Full ($2000) production
python main.py --live --phase full_live

# Dry-run (test without executing)
python main.py --live --phase micro_live --dry-run
```

---

## Safety Controls

### Kill Switch (Emergency Stop)
```powershell
# Activate
New-Item -Path "data\kill_switch.flag" -ItemType File

# Deactivate
Remove-Item "data\kill_switch.flag"

# Check status
Test-Path data\kill_switch.flag
```

### Daily Loss Limit
- Automatically enforced
- Resets at UTC midnight
- Check: Review error_log.csv for limit messages

### Total Loss Limit
- Hard stop - requires manual intervention
- Check portfolio_state.json for total_loss field

---

## Backup & Restore

### Create Backup
```powershell
python main.py --backup
# Creates: backups\backup_YYYYMMDD_HHMMSS\
```

### Restore from Backup
```powershell
python main.py --restore backups\backup_20240115_120000
```

### Schedule Automatic Backups
Add to Task Scheduler (runs weekly):
```
Program: C:\crypto_bot\venv\Scripts\python.exe
Arguments: main.py --backup
Start in: C:\crypto_bot
```

---

## Monitoring

### Real-time Monitoring
```powershell
# Watch all logs
Get-Content logs\bot.log -Wait

# Portfolio status (every 5 min)
while ($true) { 
    Clear-Host
    python main.py --status
    Start-Sleep -Seconds 300
}
```

### Check Logs
```powershell
# Last 20 trades
Get-Content data\trade_log.csv -Tail 20

# Last 10 signals
Get-Content data\signal_log.csv -Tail 10

# Portfolio snapshots
Get-Content data\snapshot_log.csv -Tail 5

# Recent errors
Get-Content data\error_log.csv -Tail 10
```

---

## Configuration

### Edit Strategy Settings
```powershell
# Conservative
notepad config\settings_conservative.json

# Aggressive
notepad config\settings_aggressive.json

# Allocation rules
notepad config\allocation.json

# Deployment phases
notepad config\deployment.json
```

**After editing**: Run health check
```powershell
python main.py --health
```

---

## Tools

### Backtest
```powershell
python tools\backtest.py --days 90
```

### Optimize Parameters
```powershell
python tools\optimize_params.py
```

### Generate Charts
```powershell
python tools\visualize.py
```

### Launch Dashboard
```powershell
streamlit run tools\dashboard.py
```

---

## Troubleshooting

### "Module not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Execution policy error"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "API authentication failed"
1. Check `config\credentials.json` exists
2. Verify all 3 fields (api_key, api_secret, passphrase)
3. Check Coinbase API permissions (View + Trade)
4. Verify API key not expired

### "Config validation failed"
```powershell
python main.py --health
# Shows specific config errors
```

### Bot Not Starting
```powershell
# Check health
python main.py --health

# View recent logs
Get-Content logs\bot.log -Tail 50

# Check for errors
Get-Content data\error_log.csv -Tail 10
```

### Trades Not Executing
- Check kill switch: `Test-Path data\kill_switch.flag`
- Check daily loss limit not hit
- Check total loss limit not hit
- Verify API connectivity
- Check signal_log.csv for blocked_reason

### Task Scheduler Not Running
1. Open Task Scheduler: `taskschd.msc`
2. Find your task
3. Check "Last Run Result" (should be 0x0)
4. View "History" tab for errors
5. Verify "Start in" path: `C:\crypto_bot`
6. Check task runs with highest privileges

---

## Daily Routine (5 minutes)

**Morning** (before market open):
1. Check if bot is running: `Get-Process python`
2. Review overnight logs: `Get-Content logs\bot.log -Tail 50`
3. Check for errors: `Get-Content data\error_log.csv -Tail 5`
4. Verify kill switch inactive: `Test-Path data\kill_switch.flag`

**Evening** (after market close):
1. Review trades: `Get-Content data\trade_log.csv -Tail 10`
2. Check PnL: `python main.py --status`
3. Note any issues for tomorrow

---

## Weekly Routine (15 minutes)

1. **Backup**:
```powershell
python main.py --backup
```

2. **Optimize**:
```powershell
python tools\optimize_params.py
```

3. **Review**:
- Win rate trending
- Loss frequency
- Parameter effectiveness

4. **Adjust** (if needed):
- Edit config files
- Test with `--dry-run`
- Deploy changes

---

## Monthly Routine (30 minutes)

1. **Full Analysis**:
```powershell
python tools\visualize.py
python tools\backtest.py --days 30
```

2. **Performance Review**:
- Total return vs. buy-and-hold
- Sharpe ratio
- Max drawdown
- Win rate by strategy

3. **Rebalancing Check**:
- Should happen automatically every 90 days
- Verify in snapshot_log.csv

4. **Update Check**:
- Check for bot updates
- Follow UPDATE_GUIDE.md if available

---

## Advanced

### Custom Check Interval
```powershell
# Check every 1 minute (60 seconds)
python main.py --paper --interval 60

# Check every 10 minutes (600 seconds)
python main.py --paper --interval 600
```

### Force Rebalance
(Manual intervention - use carefully)
```powershell
# Stop bot
New-Item -Path "data\kill_switch.flag" -ItemType File

# Edit portfolio_state.json manually
notepad data\portfolio_state.json

# Remove kill switch and restart
Remove-Item "data\kill_switch.flag"
python main.py --live --phase full_live
```

---

## Emergency Procedures

### Bot Misbehaving
1. **Stop immediately**: Create kill switch
2. **Review logs**: Check bot.log and error_log.csv
3. **Backup state**: `python main.py --backup`
4. **Analyze trades**: Compare with exchange
5. **Fix issues**: Update config or code
6. **Test**: Run with `--dry-run` first
7. **Resume**: Remove kill switch

### Exchange API Down
- Bot will log errors and retry
- Check error_log.csv for API_ERROR entries
- Trades will be retried automatically
- If extended outage: Activate kill switch

### Unexpected Loss
1. Review trade_log.csv for pattern
2. Check if risk limits are appropriate
3. Verify strategy logic in signal_log.csv
4. Consider lowering position sizes
5. Optimize parameters: `python tools\optimize_params.py`

---

## Getting Help

1. **Check logs** first: `Get-Content logs\bot.log -Tail 100`
2. **Run health check**: `python main.py --health`
3. **Review this guide**: Most issues covered above
4. **Check README FAQ**: Common questions answered

---

**This is your main reference. Bookmark it!** 📚
