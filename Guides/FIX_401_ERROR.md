# ⚠️ FIX: 401 Unauthorized Error

## ❌ **The Error**

```
⚠️  API Error: 401
   Response: Unauthorized
  ❌ Could not access account
```

**Meaning:** Your API key exists but Coinbase is rejecting it.

---

## 🔍 **Most Common Causes**

### 1. Wrong API Key Type ⚠️
**Problem:** You created an Ed25519 key instead of ECDSA

**How to check:**
1. Go to https://www.coinbase.com/settings/api
2. Look at your API key
3. Check the "Type" column

**What it should say:** ECDSA
**What it might say:** Ed25519 ❌

**Fix:** Create new ECDSA key (see below)

---

### 2. Missing Permissions ⚠️
**Problem:** API key doesn't have View or Trade permissions

**How to check:**
1. Go to https://www.coinbase.com/settings/api
2. Click on your API key
3. Check permissions

**What you need:**
- ✅ View: YES
- ✅ Trade: YES
- ❌ Transfer: NO (don't enable for security)
- ❌ Withdraw: NO (don't enable for security)

**Fix:** Create new key with correct permissions

---

### 3. API Key Not Activated ⚠️
**Problem:** Key was just created and not fully active

**How to check:**
Look at the status in API key list

**Status should be:** Active
**Status might be:** Pending ❌

**Fix:** Wait a few minutes, or create new key

---

### 4. Wrong key_name Format ⚠️
**Problem:** key_name in credentials.json is wrong

**Correct format:**
```
organizations/12345678-abcd-1234-abcd-123456789012/apiKeys/87654321-dcba-4321-dcba-210987654321
```

**Must have:**
- `organizations/` at start
- `/apiKeys/` in middle
- Two UUIDs (with dashes)

**Fix:** Copy exact key_name from Coinbase

---

### 5. Wrong Private Key Format ⚠️
**Problem:** Private key is malformed

**Correct format:**
```
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIAbcdefghijklmnopqrstuvwxyz...
...more lines...
-----END EC PRIVATE KEY-----
```

**Must have:**
- `-----BEGIN EC PRIVATE KEY-----` header
- `-----END EC PRIVATE KEY-----` footer
- Line breaks (use `\n` in JSON)

**Fix:** Copy exact private key from Coinbase

---

## ✅ **THE FIX** (5 minutes)

### Step 1: Run Diagnostic Tool

```powershell
python diagnose_api.py
```

This will identify the exact problem.

### Step 2: Create New ECDSA API Key

**Go to:** https://www.coinbase.com/settings/api

**Click:** "New API Key" or "Create New Key"

**Configure:**
```
Portfolio: Default (or your trading portfolio)
Permissions:
  ✅ View
  ✅ Trade
  ❌ Transfer
  ❌ Withdraw

⚠️  IMPORTANT: Signature Algorithm
  Select: ECDSA ✅
  NOT: Ed25519 ❌
```

**Save and copy:**
- Key name (starts with `organizations/`)
- Private key (starts with `-----BEGIN EC PRIVATE KEY-----`)

### Step 3: Update credentials.json

```powershell
notepad config\credentials.json
```

**Replace with your new keys:**
```json
{
  "coinbase": {
    "key_name": "organizations/YOUR-NEW-ORG-ID/apiKeys/YOUR-NEW-KEY-ID",
    "private_key": "-----BEGIN EC PRIVATE KEY-----\nYOUR-NEW-PRIVATE-KEY-HERE\n-----END EC PRIVATE KEY-----"
  }
}
```

**Important:**
- Copy EXACT key_name (entire string)
- Copy EXACT private key (including headers/footers)
- Keep the `\n` for line breaks in JSON

### Step 4: Test Again

```powershell
python test_coinbase_api.py
```

**Expected:**
```
✅ ECDSA credentials detected
✅ Connection successful
✅ API authentication working
✅ Successfully accessed Coinbase account!

Total: 4/4 tests passed
```

---

## 🔍 **Detailed Diagnostic**

Run this for step-by-step analysis:

```powershell
python diagnose_api.py
```

**This will:**
1. Check credentials file format
2. Test JWT token generation
3. Test actual API call
4. Give specific fix instructions

---

## 📋 **Checklist for New API Key**

When creating a new key, verify:

- [ ] Type: ECDSA (NOT Ed25519)
- [ ] Permissions: View ✅
- [ ] Permissions: Trade ✅
- [ ] Permissions: Transfer ❌
- [ ] Permissions: Withdraw ❌
- [ ] Status: Active (not Pending)
- [ ] Copied key_name exactly
- [ ] Copied private_key exactly (with headers)
- [ ] Updated credentials.json
- [ ] Saved credentials.json

---

## 🎯 **Quick Decision Tree**

**Did you just create the API key?**
→ Wait 5 minutes, then test again

**Is the Type "Ed25519"?**
→ Create new ECDSA key

**Are View or Trade permissions missing?**
→ Create new key with correct permissions

**Did you copy the key_name correctly?**
→ Check it has `organizations/` and `/apiKeys/`

**Did you copy the private key correctly?**
→ Check it has `-----BEGIN EC PRIVATE KEY-----`

**Still not working?**
→ Run `python diagnose_api.py`

---

## 🚨 **Common Mistakes**

### Mistake 1: Ed25519 Instead of ECDSA
```
❌ Type: Ed25519
✅ Type: ECDSA
```
**Fix:** Create new ECDSA key

### Mistake 2: Missing Permissions
```
❌ View: NO, Trade: NO
✅ View: YES, Trade: YES
```
**Fix:** Create key with permissions

### Mistake 3: Wrong Key Format
```
❌ key_name: "just-the-uuid-part"
✅ key_name: "organizations/uuid/apiKeys/uuid"
```
**Fix:** Copy full key_name

### Mistake 4: Missing Key Headers
```
❌ private_key: "MHcCAQEE..."
✅ private_key: "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEE...\n-----END EC PRIVATE KEY-----"
```
**Fix:** Copy with headers

---

## 📚 **Resources**

### Download Diagnostic Tool:
**[diagnose_api.py](computer:///mnt/user-data/outputs/diagnose_api.py)** - Identifies exact problem

### Guides:
- **REAL_TRADING_SETUP.md** - Complete setup guide
- **ENABLE_REAL_TRADING.md** - Quick setup
- **INSTALL_REAL_TRADING.md** - Installation steps

---

## ✅ **Summary**

**Most likely issue:** Wrong API key type (Ed25519 vs ECDSA)

**Quick fix:**
1. Create new ECDSA API key
2. Copy key_name and private_key exactly
3. Update credentials.json
4. Test: `python test_coinbase_api.py`

**Still stuck?**
```powershell
python diagnose_api.py
```

---

**Fix your API key and you'll be trading in 5 minutes!** 🚀
