# 🔍 RECREATION PROMPT - REVIEW & IMPROVEMENTS

**Status**: ⚠️ **NEEDS IMPROVEMENTS** - Prompt is 70% ready but has critical gaps

---

## 📊 OVERALL ASSESSMENT

| Category | Score | Status |
|----------|-------|--------|
| **Completeness** | 7/10 | Good structure, missing key details |
| **Clarity** | 8/10 | Mostly clear, some ambiguities |
| **Feasibility** | 6/10 | Technical gaps need addressing |
| **Windows-Focus** | 9/10 | Excellent Windows optimization |
| **Security** | 4/10 | Major security concerns |
| **Production-Ready** | 5/10 | Not production-ready as-is |

**Overall**: 6.5/10 - Good foundation, needs refinements

---

## 🚨 CRITICAL ISSUES (Must Fix)

### 1. **API Authentication Incomplete**
**Problem**: Coinbase API requires 3 credentials, not just API key
```
Missing:
- API Key
- API Secret  
- Passphrase
```

**Fix**: Update Section 9 and credentials.example.json:
```json
{
  "coinbase": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret", 
    "passphrase": "your_passphrase"
  },
  "cryptocompare": {
    "api_key": "optional_for_higher_limits"
  }
}
```

### 2. **Paper Trading Contradiction**
**Problem**: Says "no API keys required" but needs price data from somewhere

**Fix**: Clarify in Section 11:
```
Paper Trading:
- No Coinbase credentials needed
- Requires free CryptoCompare/CoinGecko access (no key for basic tier)
- Falls back to public APIs if primary fails
- Uses 5-minute delayed data (acceptable for simulation)
```

### 3. **Strategy Parameters Underspecified**

**Problem**: Key strategy logic not defined

**Missing Details**:
- **EMA Crossover**: Is it when fast crosses above/below slow? Or sustained above/below?
- **ATR Volatility**: 1.5x of what baseline? (20-day average ATR? 50-day?)
- **Breakout Detection**: Price exceeds 20-period high? By how much? (1%? Just touch?)
- **Dip Detection**: 2.5% dip from what? (Daily high? 7-day high? Entry price?)
- **Stop Loss**: Trailing or fixed from entry? Daily recalculation?

**Fix**: Add to Section 2:
```
CLARIFIED TRIGGERS:

Conservative:
- EMA Crossover: BUY when 9-EMA crosses ABOVE 21-EMA and holds for 2 periods
                 SELL when 9-EMA crosses BELOW 21-EMA  
- Dip: 2.5% below 24-hour high
- Stop Loss: Fixed 5% from entry price (not trailing)
- Take Profit: Fixed 8% from entry price

Aggressive:  
- ATR Volatility: Current ATR > 1.5x of 20-period ATR average
- Breakout: Price exceeds 20-period high by 0.5% minimum
- Dip: 2% below 4-hour high
- Stop Loss: Trailing 3% (tracks highest price since entry)
- Take Profit: Fixed 4% from entry price
```

### 4. **Allocation Math Ambiguous**

**Problem**: "Skim 27% when aggressive hits 140%" - unclear math

**Example Scenario**:
```
Starting: Conservative $700, Aggressive $300
Aggressive grows to: $420 (140% of $300)
Skim 27% of what?
  Option A: 27% of excess ($420-$300) = $32.40
  Option B: 27% of total aggressive ($420) = $113.40
```

**Fix**: Specify in Section 3:
```
Profit Skimming Algorithm:
1. Calculate aggressive baseline: initial_capital * 0.30
2. If aggressive_current_value >= baseline * 1.40:
   - excess = aggressive_current_value - baseline
   - skim_amount = excess * 0.27
   - Transfer skim_amount from aggressive to conservative
   - Log: "Skimmed $X from aggressive to conservative"
3. Update baseline for next check
```

### 5. **Security Vulnerabilities**

**Problems**:
- API keys in environment variables (Task Scheduler doesn't inherit them)
- No credential encryption
- Kill switch is just a file (easily bypassed)
- Dashboard has no authentication
- No rate limit protection

**Fix**: Add new Section 20 - Security:
```
SECURITY REQUIREMENTS:

1. Credential Storage:
   - Use Windows Credential Manager (CredentialManager PowerShell module)
   - Or encrypted config file with python-keyring
   - Never store in plain text or environment variables for scheduled tasks

2. Kill Switch Enhancement:
   - Require password file alongside kill_switch.flag
   - Verify checksum of kill switch file
   - Add remote kill switch (webhook URL)

3. Dashboard Authentication:
   - Add basic auth with username/password
   - Or restrict to localhost only (127.0.0.1)
   - Document port forwarding risks

4. Rate Limiting:
   - Max 10 API calls per minute to Coinbase
   - Exponential backoff on errors
   - Queue trades if hitting limits

5. Audit Trail:
   - Log all config changes with timestamp
   - Log all credential access attempts
   - Daily integrity check of portfolio_state.json
```

### 6. **Daily Loss Reset Undefined**

**Problem**: "Max daily loss" but no timezone or reset time specified

**Fix**: Add to Section 8:
```
Daily Loss Tracking:
- "Day" = UTC 00:00 to 23:59 (aligns with most exchanges)
- daily_loss_usd = sum of all realized losses since UTC midnight
- Resets automatically at UTC 00:00
- If max_daily_loss exceeded:
  * Stop all trading immediately
  * Log: "Daily loss limit reached: $X / $Y max"
  * Resume automatically next UTC day
  * Send alert notification
```

---

## ⚠️ MODERATE ISSUES (Should Fix)

### 7. **Position Sizing Not Specified**

**Problem**: Says "max position size" but not how to calculate trade size

**Fix**: Add to Section 8:
```
Position Sizing:
- Each trade = min(
    portfolio_value * 0.10,  # Max 10% per trade
    max_position_size,        # Phase-specific limit
    available_cash            # Don't overdraft
  )
- Conservative: Equal weight across BTC/ETH (50% each of allocation)
- Aggressive: Equal weight across SOL/AVAX/DOGE (33.3% each)
- Rebalance positions quarterly during scheduled rebalance
```

### 8. **Concurrent Trading Risk**

**Problem**: No mention of preventing simultaneous trades for same coin

**Fix**: Add to services/state.py requirements:
```
State Manager Must:
- Lock portfolio_state.json during reads/writes (fcntl on Windows)
- Prevent concurrent trades on same coin (in-memory lock)
- Atomic updates (write to temp file, then rename)
- Validate JSON before saving
- Keep 7-day backup rotation
```

### 9. **Slippage Tracking Impossible in Paper Mode**

**Problem**: Can't track slippage without actual executions

**Fix**: Update Section 11:
```
Slippage Tracking:
- Backtest: N/A (uses exact prices)
- Paper: Estimate 0.1% for BTC/ETH, 0.3% for others
- Live: Calculate (execution_price - signal_price) / signal_price
```

### 10. **Task Scheduler Details Lacking**

**Problem**: Section 15 too brief for beginners

**Fix**: Expand WINDOWS_SETUP.md section:
```
TASK SCHEDULER COMPLETE GUIDE:

1. Open Task Scheduler:
   - Press Win+R, type: taskschd.msc
   - Click "Task Scheduler Library"

2. Create Basic Task:
   - Right-click → "Create Task" (NOT Basic Task)
   - Name: "Crypto Bot - Paper Trading"
   - Description: "Automated crypto trading bot"
   - Check: "Run whether user is logged on or not"
   - Check: "Run with highest privileges"
   - Configure for: Windows 10

3. Triggers Tab:
   - New → Daily at 9:00 AM (market open)
   - Repeat task every: 5 minutes
   - For a duration of: 1 day
   - Check: "Enabled"

4. Actions Tab:
   - New → "Start a program"
   - Program/script: C:\crypto_bot\venv\Scripts\python.exe
   - Add arguments: main.py --paper --interval 300
   - Start in: C:\crypto_bot

5. Conditions Tab:
   - UNCHECK: "Start only if computer is on AC power"
   - CHECK: "Wake the computer to run this task"

6. Settings Tab:
   - Allow task to be run on demand: YES
   - Stop if runs longer than: 1 hour
   - If already running: "Do not start a new instance"

7. Save & Test:
   - Enter your Windows password when prompted
   - Right-click task → "Run" to test immediately
   - Check logs\bot.log for output
```

### 11. **No Coinbase Sandbox Mentioned**

**Problem**: Going straight to live trading is risky

**Fix**: Add to Section 6 deployment.json:
```json
"sandbox_test": {
  "capital": 1000,
  "max_daily_loss": 50,
  "max_total_loss": 100,
  "max_position_size": 100,
  "require_confirmation": true,
  "enable_kill_switch": true,
  "use_sandbox": true,
  "sandbox_url": "https://api-public.sandbox.pro.coinbase.com"
}
```

Add to rollout_1week.md:
```
Day 2.5: Sandbox Testing (before paper trading ends)
- Enable Coinbase Sandbox mode
- Get sandbox API keys from https://public.sandbox.pro.coinbase.com
- Run: python main.py --live --phase sandbox_test
- Verify trades appear in sandbox account
- Zero risk (fake money on test environment)
```

### 12. **Python Version Not Specified**

**Fix**: Add to Section 1:
```
REQUIREMENTS:
- Python 3.9+ (3.11+ recommended for Windows)
- Windows 10/11 (64-bit)
- 100MB free disk space
- Active internet connection
```

Update requirements.txt:
```
requests>=2.31.0,<3.0.0
pandas>=2.0.0,<3.0.0
numpy>=1.24.0,<2.0.0
python-dotenv>=1.0.0,<2.0.0
streamlit>=1.28.0,<2.0.0
python-keyring>=24.0.0  # NEW: Secure credential storage
```

---

## 💡 RECOMMENDED ENHANCEMENTS

### 13. **Add Dry-Run Mode**

**Why**: Test live code without actual trades

**Add to main.py flags**:
```python
parser.add_argument('--dry-run', action='store_true',
                   help='Live mode but skip actual order execution')
```

**Benefits**:
- Test API connectivity
- Verify order logic
- Check credential setup
- No financial risk

### 14. **Add Health Check Command**

**Why**: Quickly verify system status

**Add to main.py**:
```python
parser.add_argument('--health', action='store_true',
                   help='Run system health check')
```

**Should check**:
- API connectivity
- Config file validity
- Log file writability  
- Portfolio state integrity
- Kill switch status
- Disk space
- Python dependencies

### 15. **Add Parameter Validation**

**Why**: Prevent invalid configs from causing issues

**Add to main.py startup**:
```python
def validate_config():
    """Validate all config files before starting"""
    errors = []
    
    # Check allocation adds to 100%
    alloc = load_json('config/allocation.json')
    if alloc['conservative_pct'] + alloc['aggressive_pct'] != 1.0:
        errors.append("Allocation must sum to 1.0")
    
    # Check aggressive cap > baseline
    if alloc['aggressive_cap_pct'] <= alloc['aggressive_pct']:
        errors.append("Aggressive cap must be > baseline")
    
    # Check RSI bounds
    for strategy in ['conservative', 'aggressive']:
        settings = load_json(f'config/settings_{strategy}.json')
        if settings['rsi_buy'] >= settings['rsi_sell']:
            errors.append(f"{strategy}: RSI buy must be < RSI sell")
    
    if errors:
        print("CONFIG ERRORS:")
        for e in errors: print(f"  - {e}")
        sys.exit(1)
```

### 16. **Add Status Report Command**

**Why**: Quick portfolio overview without opening files

**Add to HOW_TO_USE.md**:
```powershell
# Get quick status
python main.py --status

# Example output:
# ═══════════════════════════════════════
# CRYPTO BOT STATUS - 2024-01-15 14:30:00
# ═══════════════════════════════════════
# Portfolio Value: $2,150.00 (+7.5%)
# Conservative: $1,500.00 (69.8%)
# Aggressive: $650.00 (30.2%)
# ───────────────────────────────────────
# Today's Performance:
#   Trades: 3 (2 wins, 1 loss)
#   PnL: +$45.00 (+2.1%)
#   Win Rate: 66.7%
# ───────────────────────────────────────
# Risk Status: ✓ HEALTHY
#   Daily Loss: $15 / $200 max (7.5%)
#   Total Loss: $0 / $400 max (0%)
# ───────────────────────────────────────
# Next Actions:
#   - Rebalance due in 45 days
#   - No skim needed (aggressive at 32%)
# ═══════════════════════════════════════
```

### 17. **Add Backup/Restore Commands**

**Why**: Recover from corrupted state files

**Add to main.py**:
```python
parser.add_argument('--backup', action='store_true',
                   help='Backup portfolio state and logs')
parser.add_argument('--restore', type=str,
                   help='Restore from backup file')
```

**Implementation**:
```python
def backup():
    """Create timestamped backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backups/backup_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy critical files
    shutil.copy('data/portfolio_state.json', backup_dir)
    shutil.copy('data/trade_log.csv', backup_dir)
    shutil.copy('data/snapshot_log.csv', backup_dir)
    
    print(f"Backup created: {backup_dir}")
```

### 18. **Add Exchange Connectivity Check**

**Why**: Don't start trading if API is down

**Add to main.py startup**:
```python
def check_connectivity():
    """Verify Coinbase API is reachable"""
    try:
        response = requests.get(
            'https://api.coinbase.com/v2/time',
            timeout=5
        )
        if response.status_code == 200:
            print("✓ Coinbase API: Connected")
            return True
        else:
            print(f"✗ Coinbase API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Coinbase API: {str(e)}")
        return False
```

### 19. **Add Performance Benchmarks**

**Why**: Know if strategies are actually profitable

**Add to rollout_1week.md pass criteria**:
```
Pass Criteria Enhanced:

Day 1 - Backtest:
- Conservative DD < 25%, PF > 1.1
- Aggressive DD < 45%, PF > 1.1
- BENCHMARK: Must beat BTC buy-and-hold
- Min 50 trades in 90-day backtest
- Win rate > 50%

Day 2 - Paper:
- Zero errors for 24-48 hours
- At least 5 signals generated
- All signals logged correctly
- No negative balance scenarios
```

### 20. **Add Windows Defender Exception**

**Why**: Prevent false positives

**Add to WINDOWS_SETUP.md**:
```powershell
# Add folder to Windows Defender exceptions
Add-MpPreference -ExclusionPath "C:\crypto_bot"

# Verify exception was added
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

---

## 📋 MISSING DOCUMENTATION SECTIONS

### 21. **Troubleshooting Quick Reference**

Add to HOW_TO_USE.md:
```
COMMON ISSUES:

"Module not found":
→ Activate venv: .\venv\Scripts\Activate.ps1
→ Reinstall: pip install -r requirements.txt

"API authentication failed":
→ Check credentials in config/credentials.json
→ Verify Coinbase API permissions (view, trade)
→ Check API key expiration date

"Portfolio state corrupted":
→ Restore from backup: python main.py --restore backups/backup_YYYYMMDD_HHMMSS
→ Or delete portfolio_state.json (starts fresh)

"Task Scheduler not running":
→ Check logs\bot.log for errors
→ Verify "Start in" path is correct
→ Ensure account has Admin privileges
→ Check Task History tab for error codes

"Prices not updating":
→ Check internet connection
→ Verify CryptoCompare API status
→ Check data/error_log.csv for API errors

"Too many trades":
→ Check if parameters are too sensitive
→ Run: python tools/optimize_params.py
→ Increase RSI thresholds (less sensitive)
```

### 22. **Update Checklist**

Add new file: UPDATE_GUIDE.md:
```markdown
# Bot Update Procedure

## Before Updating
1. Stop bot: Delete data/kill_switch.flag, wait 5 minutes
2. Backup: python main.py --backup
3. Note current version: Check main.py header

## Update Steps
1. Download new version
2. Compare config files (don't overwrite your settings)
3. Update code files only
4. Run: python main.py --health
5. Test: python main.py --paper --interval 60 (1 min test)
6. Resume: python main.py --live --phase [current_phase]

## Rollback If Issues
1. Stop bot
2. Restore old version from backup
3. Restore: python main.py --restore backups/[latest]
4. Report issue to developer
```

---

## 🎯 PRIORITY FIXES SUMMARY

**Fix These FIRST (Before Recreation)**:

1. ✅ Add complete Coinbase authentication (key + secret + passphrase)
2. ✅ Clarify strategy trigger logic (EMA, ATR, breakout, dips)
3. ✅ Specify allocation math precisely (skim calculation)
4. ✅ Add security section (credentials, encryption, auth)
5. ✅ Define "daily loss" reset time (UTC midnight)
6. ✅ Add position sizing algorithm
7. ✅ Expand Task Scheduler instructions
8. ✅ Add Coinbase Sandbox phase
9. ✅ Specify Python version requirement
10. ✅ Add config validation on startup

**Nice-to-Have Additions**:

11. ✅ Dry-run mode
12. ✅ Health check command
13. ✅ Status report command
14. ✅ Backup/restore commands
15. ✅ Connectivity check
16. ✅ Windows Defender exceptions
17. ✅ Troubleshooting quick reference
18. ✅ Update guide

---

## 📝 REVISED PROMPT SECTIONS

### Replace Section 9 (WINDOWS-SPECIFIC) with:

```markdown
9. WINDOWS-SPECIFIC REQUIREMENTS
- All file paths use os.path.join() or pathlib.Path
- PowerShell commands in all documentation
- Environment variable setup (Windows Credential Manager preferred)
- Task Scheduler automation guide (complete step-by-step with screenshots)
- No Linux-only commands or bash scripts
- Execution policy fix: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
- Windows Defender exception for bot folder
- Support for long paths (enable if needed)
- Python 3.9+ (3.11+ recommended)
```

### Add NEW Section 20 (SECURITY):

```markdown
20. SECURITY REQUIREMENTS

Credential Storage:
- Use Windows Credential Manager (cmdkey.exe or powershell CredentialManager)
- Or python-keyring for encrypted storage
- Format: coinbase_key, coinbase_secret, coinbase_passphrase
- NEVER store in plain text files or environment vars for scheduled tasks

Authentication:
- Dashboard: Basic auth or localhost-only (127.0.0.1)
- API keys: Read-only for backtesting, trade permission for live
- Rotate keys quarterly

Kill Switch:
- Primary: data/kill_switch.flag (manual file creation)
- Remote: Optional webhook URL for emergency stop
- Verify file checksum to prevent tampering

Rate Limiting:
- Coinbase: Max 10 calls/minute (built into coinbase_api.py)
- Price APIs: Max 100 calls/hour
- Exponential backoff on errors (2s, 4s, 8s, 16s, stop)

Audit:
- Log all config changes to logs/audit.log
- Daily integrity check of portfolio_state.json
- Alert on suspicious activity (large losses, many errors)
```

### Update Section 2 (DUAL-STRATEGY) with:

```markdown
2. DUAL-STRATEGY SYSTEM

CONSERVATIVE (BTC-USD, ETH-USD) - 70% allocation:

Buy Signals (ALL must trigger):
1. RSI < 30 (14-period)
2. Price dropped 2.5% from 24-hour high
3. EITHER:
   - EMA crossover: 9-EMA crosses above 21-EMA and holds 2 periods
   - OR volume spike: 1.5x 20-day average volume

Sell Signals (ANY triggers):
1. RSI > 70
2. Price +8% from entry (take profit)
3. Price -5% from entry (stop loss - FIXED, not trailing)
4. EMA crossunder: 9-EMA crosses below 21-EMA

AGGRESSIVE (SOL-USD, AVAX-USD, DOGE-USD) - 30% allocation:

Buy Signals (ANY triggers):
1. RSI < 25 + price dropped 2% from 4-hour high
2. ATR breakout: Current ATR > 1.5x of 20-period ATR average
3. Price breakout: Price exceeds 20-period high by 0.5%+ with volume

Sell Signals (ANY triggers):
1. RSI > 75
2. Price +4% from entry (take profit)
3. Trailing stop: Price drops 3% from highest point since entry
4. Time-based: Hold 48 hours max, sell regardless

Position Sizing:
- Each trade = min(allocation_value * 0.10, max_position_size, available_cash)
- Conservative: 50% BTC, 50% ETH (of conservative allocation)
- Aggressive: 33.3% each SOL, AVAX, DOGE (of aggressive allocation)
- No overlapping trades on same coin (wait for exit before re-entry)
```

### Update Section 3 (ALLOCATION) with:

```markdown
3. DYNAMIC ALLOCATION SYSTEM

Baseline Allocation:
- Conservative: 70% of total portfolio
- Aggressive: 30% of total portfolio
- Rebalance: Every 90 days (quarterly)

Profit Skimming (happens anytime):
- Trigger: When aggressive_value >= (initial_aggressive_value * 1.40)
- Calculate: excess = aggressive_value - initial_aggressive_value
- Skim: skim_amount = excess * 0.27
- Action: Transfer skim_amount from aggressive → conservative
- Reset: initial_aggressive_value stays the same (no new baseline)
- Example: 
  * Start: Aggressive $300
  * Grows to: $420 (140% of baseline)
  * Excess: $420 - $300 = $120
  * Skim: $120 * 0.27 = $32.40
  * After skim: Aggressive $387.60, Conservative $732.40

Aggressive Cap (happens anytime):
- Trigger: When aggressive_pct > 50% of total portfolio
- Calculate: excess = aggressive_value - (total_value * 0.50)
- Action: Transfer excess to conservative
- Example:
  * Total: $1000
  * Aggressive: $550 (55%)
  * Excess: $550 - $500 = $50
  * After cap: Aggressive $500 (50%), Conservative $500 (50%)

Quarterly Rebalancing (every 90 days):
- Calculate: target_conservative = total_value * 0.70
- Calculate: target_aggressive = total_value * 0.30
- Rebalance: Transfer funds to match targets exactly
- Log: "Quarterly rebalance: Moved $X from [source] to [dest]"
- Next rebalance: 90 days from today

No Loss Chasing:
- Conservative losses NEVER trigger transfers from aggressive
- Only profits can trigger skims/transfers
- Each strategy is accountable for its own performance
```

---

## ✅ VALIDATION CHECKLIST

After applying these fixes, the prompt should:

- [ ] Specify all required API credentials clearly
- [ ] Define all strategy triggers unambiguously  
- [ ] Clarify all allocation math with examples
- [ ] Include comprehensive security measures
- [ ] Specify timezones and reset logic
- [ ] Define position sizing algorithm
- [ ] Provide complete Task Scheduler guide
- [ ] Include Coinbase Sandbox phase
- [ ] Require Python 3.9+ explicitly
- [ ] Validate configs on startup
- [ ] Add dry-run mode
- [ ] Add health check command
- [ ] Add backup/restore functionality
- [ ] Check exchange connectivity
- [ ] Include troubleshooting guide
- [ ] Document update procedure

---

## 🎯 FINAL RECOMMENDATION

**Status**: Prompt needs **medium refactor** before use

**Estimated Time**: 2-3 hours to incorporate all fixes

**Priority Actions**:
1. Fix Sections 2, 3, 9 (critical logic)
2. Add Section 20 (security)
3. Expand Section 15 (Task Scheduler)
4. Add validation, health check, dry-run
5. Enhance troubleshooting docs

**After Fixes**: Prompt will be **9/10** production-ready 🎯

---

Would you like me to:
1. Generate the REVISED PROMPT with all fixes incorporated?
2. Create a PATCH FILE showing exact changes needed?
3. Build the system now with improvements applied?

Let me know! 🚀
