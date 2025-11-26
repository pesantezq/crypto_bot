# ⚡ Quick Installation Guide (5 Minutes)

Get the bot running in paper trading mode fast!

---

## Step 1: Install Python (2 minutes)

1. Download Python 3.11+ from: https://www.python.org/downloads/windows/
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:

```powershell
python --version
# Should show: Python 3.11.x or higher
```

---

## Step 2: Extract Bot (30 seconds)

1. Extract `crypto_bot_windows.zip` to `C:\crypto_bot`
2. Your folder should look like:
```
C:\crypto_bot\
├── main.py
├── requirements.txt
├── README.md
├── config/
├── strategies/
└── services/
```

---

## Step 3: Setup Virtual Environment (1 minute)

Open PowerShell as Administrator:

```powershell
# Navigate to bot folder
cd C:\crypto_bot

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
.\venv\Scripts\Activate.ps1
```

---

## Step 4: Install Dependencies (1 minute)

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

Wait for installation to complete (~1 minute).

---

## Step 5: Test Run (30 seconds)

```powershell
# Run health check
python main.py --health

# Should show:
# ✅ Python 3.11.x
# ✅ Configuration files
# ✅ Dependencies
```

---

## Step 6: Start Paper Trading! (Now!)

```powershell
python main.py --paper
```

**You should see**:
```
🤖 Crypto Trading Bot v2.0
Mode: PAPER
📝 Starting paper trading mode...
✅ Price API: Connected (BTC: $45,234.56)
✅ Logger initialized
✅ All components initialized successfully!
```

**Press Ctrl+C to stop**

---

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] Bot extracted to C:\crypto_bot
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (no errors)
- [ ] Health check passes
- [ ] Paper trading starts successfully

---

## ⚠️ Troubleshooting

### "Python not found"
- Reinstall Python with "Add to PATH" checked
- Or manually add to PATH: Control Panel → System → Environment Variables

### "Execution policy error"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Module not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Health check fails"
- Check config/ folder exists
- Verify all JSON files are present
- Run: `python main.py --health` for detailed errors

---

## 🎉 You're Done!

**Paper trading is running!** This mode uses live prices but simulates trades (no real money).

**Next Steps**:
- Let it run for 24 hours
- Check logs: `Get-Content logs\bot.log -Tail 20`
- View trades: `Get-Content data\trade_log.csv -Tail 20`
- Read [HOW_TO_USE.md](HOW_TO_USE.md) for daily operations
- When ready: Follow [rollout_1week.md](rollout_1week.md) for real money deployment

---

**Questions?** Check [README.md](README.md) FAQ section.

**Ready to go live?** Read [WINDOWS_SETUP.md](WINDOWS_SETUP.md) first!
