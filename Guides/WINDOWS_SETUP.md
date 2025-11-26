# 🪟 Windows Complete Setup Guide

Comprehensive setup for Windows 10/11 users.

---

## Part 1: Python Installation (5 minutes)

### Download Python
1. Visit: https://www.python.org/downloads/windows/
2. Download: **Python 3.11.x** (or newer)
3. Run the installer

### Installation Steps
1. ✅ **CRITICAL**: Check "Add Python to PATH"
2. Click "Install Now"
3. Wait for completion
4. Click "Close"

### Verify Installation
```powershell
python --version
# Should show: Python 3.11.x

pip --version
# Should show: pip 23.x.x
```

---

## Part 2: Extract Bot (1 minute)

1. Extract `crypto_bot_windows.zip`
2. Move folder to: `C:\crypto_bot`
3. Verify folder structure:
```
C:\crypto_bot\
├── main.py
├── requirements.txt
├── README.md
├── config\
├── strategies\
├── services\
└── tools\
```

---

## Part 3: Virtual Environment (3 minutes)

### Open PowerShell as Administrator
1. Press `Win + X`
2. Select "Windows PowerShell (Admin)"

### Fix Execution Policy (If Needed)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Create Virtual Environment
```powershell
cd C:\crypto_bot
python -m venv venv
```

### Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your prompt.

---

## Part 4: Install Dependencies (2 minutes)

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Verify Installation
```powershell
pip list
# Should show: requests, pandas, numpy, streamlit, etc.
```

---

## Part 5: API Keys (10 minutes)

### Get Coinbase API Keys
1. Visit: https://www.coinbase.com/settings/api
2. Click "New API Key"
3. Permissions: ✅ View, ✅ Trade (NOT Transfer/Withdraw)
4. Save these securely:
   - API Key
   - API Secret
   - Passphrase

### Configure Credentials

**Method 1: JSON File (Recommended)**
```powershell
cd C:\crypto_bot\config
copy credentials.example.json credentials.json
notepad credentials.json
```

Fill in your actual credentials:
```json
{
  "coinbase": {
    "api_key": "your_actual_key_here",
    "api_secret": "your_actual_secret_here",
    "passphrase": "your_actual_passphrase_here"
  }
}
```

Save and close.

---

## Part 6: Windows Defender Exception (1 minute)

Add folder to Windows Defender exceptions:

```powershell
Add-MpPreference -ExclusionPath "C:\crypto_bot"

# Verify
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

---

## Part 7: Task Scheduler Setup (10 minutes)

### Open Task Scheduler
1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter

### Create New Task
1. Right-click "Task Scheduler Library"
2. Select "Create Task" (NOT "Create Basic Task")

### General Tab
- Name: `Crypto Bot - Paper Trading`
- Description: `Automated crypto trading bot`
- Security options:
  * ✅ Run whether user is logged on or not
  * ✅ Run with highest privileges
- Configure for: Windows 10 (or 11)

### Triggers Tab
1. Click "New..."
2. Begin the task: **On a schedule**
3. Settings: **Daily**
4. Start: **9:00:00 AM** (market open)
5. Advanced settings:
   * ✅ Repeat task every: **5 minutes**
   * For a duration of: **1 day**
   * ✅ Enabled
6. Click OK

### Actions Tab
1. Click "New..."
2. Action: **Start a program**
3. Program/script: `C:\crypto_bot\venv\Scripts\python.exe`
4. Add arguments: `main.py --paper --interval 300`
5. Start in: `C:\crypto_bot`
6. Click OK

### Conditions Tab
- Power:
  * ❌ Start the task only if the computer is on AC power
  * ❌ Stop if the computer switches to battery power
  * ✅ Wake the computer to run this task
- Network:
  * ✅ Start only if the following network connection is available
  * Select: Any connection

### Settings Tab
- ✅ Allow task to be run on demand
- ✅ Run task as soon as possible after a scheduled start is missed
- ✅ If the task fails, restart every: **1 minute**, **3 times**
- Stop the task if it runs longer than: **1 hour**
- If the running task does not end when requested: **Stop using Task Manager**
- If the task is already running: **Do not start a new instance**

### Save Task
1. Click OK
2. Enter your Windows password when prompted
3. Click OK

### Test the Task
1. Right-click your task
2. Select "Run"
3. Check "Last Run Result" → should be `0x0`
4. Open: `C:\crypto_bot\logs\bot.log`
5. Verify bot started successfully

---

## Part 8: Firewall Configuration (If Needed)

Usually not required, but if bot can't connect:

```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "Crypto Bot - Python" `
  -Direction Outbound `
  -Program "C:\crypto_bot\venv\Scripts\python.exe" `
  -Action Allow
```

---

## Part 9: Verification (5 minutes)

### Run Health Check
```powershell
cd C:\crypto_bot
.\venv\Scripts\Activate.ps1
python main.py --health
```

Should show all ✅ green checkmarks.

### Test Paper Trading
```powershell
python main.py --paper
```

Let run for 5 minutes, then Ctrl+C to stop.

### Verify Logs Created
```powershell
dir data\
# Should see: trade_log.csv, signal_log.csv, etc.

dir logs\
# Should see: bot.log
```

---

## Troubleshooting

### "Python not recognized"
**Fix**: Add Python to PATH manually
1. Open: Control Panel → System → Advanced System Settings
2. Click: Environment Variables
3. Edit: PATH (User variables)
4. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`
5. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`
6. Click OK, restart PowerShell

### "Execution policy error"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Module not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "API authentication failed"
- Verify all 3 credentials in config\credentials.json
- Check API key permissions on Coinbase
- Ensure API key not expired

### Task Scheduler Won't Run
- Verify "Start in" path: `C:\crypto_bot`
- Check account has admin privileges
- View task history for error codes
- Ensure Python path is correct (venv\Scripts\python.exe)

### Bot Can't Access Internet
- Check firewall settings
- Verify network connection
- Test: `curl https://api.coinbase.com/v2/time`

### PowerShell Errors
If any command fails:
1. Run PowerShell as Administrator
2. Check execution policy
3. Verify working directory: `cd C:\crypto_bot`
4. Activate venv: `.\venv\Scripts\Activate.ps1`

---

## Advanced Configuration

### Long Path Support (If Needed)
```powershell
# Enable long paths (> 260 characters)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Restart required
Restart-Computer
```

### Multiple Bot Instances
To run multiple bots:
1. Create separate folders: `C:\crypto_bot_1`, `C:\crypto_bot_2`
2. Each needs its own venv
3. Each needs separate Task Scheduler tasks
4. Use different coins or strategies

---

## Security Best Practices

1. **API Keys**:
   - Never share or commit to version control
   - Rotate keys quarterly
   - Use minimal permissions (View + Trade only)

2. **Credentials File**:
   - Keep in .gitignore
   - Backup securely
   - Don't email or share

3. **Windows Account**:
   - Use strong password
   - Enable BitLocker (optional)
   - Regular Windows updates

4. **Bot Security**:
   - Keep Python updated
   - Update dependencies: `pip install --upgrade -r requirements.txt`
   - Review logs regularly
   - Use kill switch when needed

---

## Next Steps

1. ✅ **Setup Complete!**
2. Read [rollout_1week.md](rollout_1week.md) for deployment plan
3. Start with paper trading: `python main.py --paper`
4. Monitor for 24-48 hours
5. Follow 7-day rollout before going live

---

**Questions?** Check [HOW_TO_USE.md](HOW_TO_USE.md) for daily operations.

**Ready to deploy?** Follow [rollout_1week.md](rollout_1week.md) step-by-step.
