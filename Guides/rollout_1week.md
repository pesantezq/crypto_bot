# 📅 7-Day Deployment Plan

Complete, safe deployment from testing to production.

---

## Overview

| Day | Phase | Capital | Pass Criteria |
|-----|-------|---------|---------------|
| 1 | Backtest | $0 (historical) | DD < 25%/45%, PF > 1.1, beats BTC |
| 2 | Paper Trading | $0 (simulated) | 24-48h, zero errors, 5+ signals |
| 2.5 | Sandbox Testing | $1000 (fake) | API works, trades execute |
| 3 | Micro-live | $10 | Logs match exchange 100% |
| 4 | Parameter Tuning | - | Optimize based on results |
| 5 | Light-live | $50 | Same behavior as micro |
| 6 | Stress Testing | - | Kill switch, edge cases |
| 7 | Full Deployment | $2000 | Production ready |

---

## Day 1: Backtesting (Historical Simulation)

**Goal**: Validate strategies on 90 days of historical data

```powershell
python main.py --backtest --days 90
```

**Pass Criteria**:
- Conservative: Max Drawdown < 25%, Profit Factor > 1.1
- Aggressive: Max Drawdown < 45%, Profit Factor > 1.1
- Combined returns beat BTC buy-and-hold
- Minimum 50 trades generated

**If Failed**: Adjust parameters in `config/settings_*.json`

---

## Day 2: Paper Trading (Live Simulation)

**Goal**: Test with live prices, zero risk

```powershell
python main.py --paper --interval 300
```

**Let Run**: 24-48 hours minimum

**Pass Criteria**:
- Zero errors in logs
- At least 5 signals generated
- All signals logged correctly
- No negative balance scenarios

**Monitoring**:
```powershell
# Watch logs
Get-Content logs\bot.log -Wait

# Check trades
Get-Content data\trade_log.csv -Tail 20

# View signals
Get-Content data\signal_log.csv -Tail 20
```

---

## Day 2.5: Sandbox Testing (Coinbase Test Environment)

**Goal**: Test real API without real money

**Setup**:
1. Get sandbox API keys: https://public.sandbox.pro.coinbase.com
2. Add to `config/credentials.json`
3. Run sandbox mode

```powershell
python main.py --sandbox --phase sandbox_test
```

**Pass Criteria**:
- API connection successful
- Orders execute in sandbox
- Trades appear in sandbox account
- Logs match sandbox transactions

**If Failed**: Check API keys, permissions, sandbox URL

---

## Day 3: Micro-live ($10 Real Money)

**Goal**: First real money test with minimal capital

**Setup**:
```powershell
python main.py --live --phase micro_live --confirm
```

**Confirmation Mode**: You'll be prompted before each trade

**Pass Criteria**:
- Logs 100% match Coinbase exchange
- All trades execute successfully
- Balance tracking is accurate
- No unexpected behavior

**Safety**:
- Max daily loss: $3
- Max total loss: $5
- Kill switch ready: `New-Item -Path "data\kill_switch.flag" -ItemType File`

**Monitoring** (every 2 hours):
- Check bot.log
- Verify Coinbase transactions
- Compare trade_log.csv with exchange

---

## Day 4: Parameter Optimization

**Goal**: Tune parameters based on real results

```powershell
python tools\optimize_params.py
```

**Analyze**:
- Win rate by trigger type
- PnL by parameter set
- Best performing coins
- Optimal RSI thresholds

**Actions**:
- Adjust `config/settings_conservative.json`
- Adjust `config/settings_aggressive.json`
- Re-run micro-live for 6 hours
- Verify improvements

---

## Day 5: Light-live ($50)

**Goal**: Scale up with automated trading

```powershell
python main.py --live --phase light_live
```

**No Confirmation Mode**: Trades execute automatically

**Pass Criteria**:
- Same behavior as micro-live (just scaled)
- No new errors introduced
- Risk limits respected
- Allocation rules working

**Let Run**: 24 hours minimum

**Daily Checks**:
```powershell
# Status
python main.py --status

# Recent trades
Get-Content data\trade_log.csv -Tail 10

# Errors
Get-Content data\error_log.csv -Tail 5
```

---

## Day 6: Stress Testing

**Goal**: Test edge cases and safety features

**Tests**:

1. **Kill Switch Test**:
```powershell
New-Item -Path "data\kill_switch.flag" -ItemType File
# Verify bot stops immediately
```

2. **Daily Loss Limit**: Let it hit max daily loss, verify it stops

3. **Network Interruption**: Disconnect internet briefly, verify recovery

4. **API Rate Limit**: Verify exponential backoff works

5. **Invalid Config**: Corrupt a JSON file, verify error handling

6. **Low Balance**: Simulate insufficient funds, verify graceful handling

**Pass Criteria**: All safety features work as expected

---

## Day 7: Full Deployment ($2000)

**Goal**: Production deployment with full capital

**Final Checks**:
- [ ] All previous phases passed
- [ ] No errors in past 24 hours
- [ ] Backup created: `python main.py --backup`
- [ ] Task Scheduler configured (if desired)
- [ ] Kill switch tested and understood

```powershell
python main.py --live --phase full_live
```

**Setup Task Scheduler** (Optional but Recommended):
- See WINDOWS_SETUP.md for complete guide
- Run every 5 minutes
- Start at market open (9 AM)
- Run whether logged in or not

**Ongoing Monitoring**:

**Daily** (5 minutes):
- Check bot.log for errors
- Review trade_log.csv
- Verify exchange matches logs

**Weekly** (15 minutes):
- Run: `python tools\optimize_params.py`
- Review win rate and PnL
- Adjust parameters if needed
- Create backup: `python main.py --backup`

**Monthly** (30 minutes):
- Full performance review
- Parameter reoptimization
- Rebalancing check
- Update bot if new version available

---

## Rollback Procedure

**If anything goes wrong**:

1. **Activate kill switch immediately**:
```powershell
New-Item -Path "data\kill_switch.flag" -ItemType File
```

2. **Review logs**:
```powershell
Get-Content logs\bot.log -Tail 100
Get-Content data\error_log.csv -Tail 20
```

3. **Restore from backup**:
```powershell
python main.py --restore backups\backup_YYYYMMDD_HHMMSS
```

4. **Drop back one phase**:
- Full → Light ($50)
- Light → Micro ($10)
- Micro → Paper ($0)

5. **Fix issues, re-test, try again**

---

## Success Metrics

**After 7 Days**, you should have:
- ✅ 50+ trades executed
- ✅ Positive net PnL (or small loss within limits)
- ✅ Zero critical errors
- ✅ All safety features tested
- ✅ Confidence in the system
- ✅ Understanding of operation

---

## ⚠️ Important Reminders

1. **Never skip phases** - Each builds on the previous
2. **Log everything** - You'll need it for debugging
3. **Start small** - Better to miss gains than take losses
4. **Trust the process** - 7 days is reasonable for $2000
5. **Use kill switch** - When in doubt, stop and review

---

**Ready to start? Day 1 begins now!** 🚀
