# ♻️ Update Guide

How to safely update the bot to new versions.

---

## Before Updating

### Step 1: Backup Everything
```powershell
python main.py --backup
```

This saves:
- portfolio_state.json
- All CSV logs
- Current configuration

### Step 2: Stop the Bot
```powershell
# Activate kill switch
New-Item -Path "data\kill_switch.flag" -ItemType File

# Wait 5 minutes for current cycle to complete

# Verify stopped
Get-Process python
# Should show no python processes for crypto bot
```

### Step 3: Note Current Version
```powershell
# Check main.py header
Get-Content main.py -Head 10
# Look for: Version: X.X
```

---

## Update Process

### Download New Version
1. Get latest `crypto_bot_windows.zip`
2. Extract to temporary folder: `C:\crypto_bot_new`

### Compare Configurations
```powershell
# Compare your current configs with new defaults
fc C:\crypto_bot\config\settings_conservative.json C:\crypto_bot_new\config\settings_conservative.json
```

**Important**: Don't blindly overwrite configs! New versions may have new parameters.

### Merge Configurations
For each config file:
1. Open both versions (old and new)
2. Add any new parameters from new version
3. Keep your custom values
4. Save to your production config

### Update Code Files Only
```powershell
# Replace code files (NOT data or config)
Copy-Item C:\crypto_bot_new\main.py C:\crypto_bot\main.py -Force
Copy-Item C:\crypto_bot_new\strategies\* C:\crypto_bot\strategies\ -Force
Copy-Item C:\crypto_bot_new\services\* C:\crypto_bot\services\ -Force
Copy-Item C:\crypto_bot_new\tools\* C:\crypto_bot\tools\ -Force

# Update requirements
Copy-Item C:\crypto_bot_new\requirements.txt C:\crypto_bot\requirements.txt -Force
```

### Update Dependencies
```powershell
cd C:\crypto_bot
.\venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
```

---

## After Updating

### Step 1: Health Check
```powershell
python main.py --health
```

Fix any errors before proceeding.

### Step 2: Test Paper Trading
```powershell
python main.py --paper --interval 60
```

Let run for 10 minutes. Check logs:
```powershell
Get-Content logs\bot.log -Tail 50
```

### Step 3: Test Dry-Run
```powershell
python main.py --live --phase micro_live --dry-run
```

Verify all logic works without executing real trades.

### Step 4: Resume Production
```powershell
# Remove kill switch
Remove-Item "data\kill_switch.flag"

# Restart with your normal phase
python main.py --live --phase full_live
```

---

## Rollback If Issues

### Step 1: Stop Bot
```powershell
New-Item -Path "data\kill_switch.flag" -ItemType File
```

### Step 2: Restore Old Version
```powershell
# Keep backup of new version
Move-Item C:\crypto_bot C:\crypto_bot_failed

# Restore old version from backup
# (You kept a backup before updating, right?)
Copy-Item -Recurse C:\crypto_bot_backup C:\crypto_bot
```

### Step 3: Restore Data
```powershell
python main.py --restore backups\backup_YYYYMMDD_HHMMSS
```

### Step 4: Resume
```powershell
Remove-Item "data\kill_switch.flag"
python main.py --live --phase full_live
```

---

## Update Checklist

Before update:
- [ ] Backup created
- [ ] Bot stopped
- [ ] Current version noted
- [ ] Old version backed up

During update:
- [ ] Configs compared and merged
- [ ] Code files updated
- [ ] Dependencies updated
- [ ] Health check passes

After update:
- [ ] Paper trading tested (10 min)
- [ ] Dry-run tested
- [ ] Logs reviewed
- [ ] Production resumed

---

## Version History

Keep track of updates:
```powershell
# Create version log
echo "$(Get-Date) - Updated to v2.1" >> version_history.txt
```

---

## When to Update

**Update immediately** for:
- Security fixes
- Critical bugs
- API changes

**Update carefully** for:
- New features
- Strategy changes
- Major rewrites

**Don't update** during:
- Active trades
- High volatility
- Without backup

---

## Getting Help

If update fails:
1. Rollback to previous version
2. Check update notes for breaking changes
3. Review error logs
4. Ask for help with specific error messages

---

**Always backup before updating!** 💾
