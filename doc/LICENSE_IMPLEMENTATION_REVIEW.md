# License Implementation Review

## Overview
This document reviews how the license system works in FonixFlow and identifies potential issues.

## Current Implementation

### 1. License State Management

**Location**: `gui/main_window.py` (lines 95-99)

```python
# License key state
self.license_key = self.settings_manager.get("license_key", None)
self.license_valid = False
self.check_license_key_on_startup()
```

**How it works:**
- On startup, the app loads the license key from `~/.fonixflow_config.json`
- `license_valid` is set to `False` initially
- `check_license_key_on_startup()` validates the key if it exists

### 2. License Validation

**Location**: `gui/main_window.py` (lines 200-229)

**Validation Process:**
1. **Local File Check** (Primary for testing):
   - Checks `licenses.txt` file in project root
   - If key exists in file, returns `True`
   - Used for offline/testing scenarios

2. **LemonSqueezy API Check** (Production):
   - If not found locally, checks `https://api.lemonsqueezy.com/v1/licenses/validate`
   - Sends POST request with license key
   - Returns `True` if API response has `status == "active"`
   - Returns `False` on any error (network, timeout, invalid response)

**Potential Issues:**
- ❌ **Network failures cause validation to fail silently** - if API is unreachable, valid keys appear invalid
- ❌ **No retry mechanism** - single attempt, 10-second timeout
- ❌ **No caching of validation results** - re-validates on every startup
- ❌ **Error handling is too broad** - any exception returns `False`

### 3. Transcription License Check

**Location**: `gui/main_window.py` (lines 1775-1933)

**Current Behavior:**
```python
def start_transcription(self):
    """Start transcription process."""
    # Note: Transcription works without license, but is limited to 500 words.
    # The word limit is enforced in on_transcription_complete() after transcription finishes.
    # No need to show a message here - only show message if limit is actually exceeded.
```

**✅ GOOD**: Transcription is **NOT blocked** by license check. It allows transcription without a license.

**Word Limit Enforcement** (lines 2100-2113):
```python
# Word limit for unlicensed users (500 words)
if not self.license_valid:
    words = text.split()
    if len(words) > 500:
        # Truncate and show message
```

**✅ GOOD**: Word limit is enforced **AFTER** transcription completes, not before.

### 4. License Dialog

**Location**: `gui/dialogs.py` (lines 4-98)

**When it's shown:**
1. User clicks "Activate" button in Settings tab → `show_activation_dialog()`
2. User manually calls `prompt_for_license_key()`

**Dialog Behavior:**
- Shows input field for license key
- Validates key (local file first, then API)
- Saves key to `~/.fonixflow_config.json` if valid
- Sets `self.license_valid = True` on success

## Identified Issues

### Issue #1: License Validation May Fail Due to Network Issues

**Problem:**
If the LemonSqueezy API is unreachable (network down, firewall, etc.), even valid license keys will be marked as invalid.

**Current Code:**
```python
except Exception as e:
    logger.error(f"License validation error: {e}")
    return False  # ❌ Returns False on ANY error
```

**Impact:**
- User enters valid license key
- Network issue occurs during validation
- License marked as invalid
- User sees license prompts even though they have a valid key

**Recommendation:**
- Add retry logic (3 attempts with exponential backoff)
- Cache validation results (validate once per day, not on every startup)
- Show user-friendly error message if validation fails due to network
- Allow "offline mode" if license was previously validated

### Issue #2: License State Not Persisted Correctly

**Problem:**
`license_valid` is recalculated on every startup. If validation fails (network issue), the state is lost even if the key was previously valid.

**Current Flow:**
1. User enters license key → saved to config file
2. On next startup → `check_license_key_on_startup()` runs
3. If validation fails → `license_valid = False`
4. User sees license prompts again

**Recommendation:**
- Store `license_validated_date` in config file
- Only re-validate if last validation was > 24 hours ago
- Show "License validation pending" status if network unavailable

### Issue #3: No Clear Indication of License Status

**Problem:**
User doesn't know if:
- License key is saved but validation failed
- License key is invalid
- Network issue prevented validation
- License is actually active

**Recommendation:**
- Add license status indicator in UI (Settings tab)
- Show last validation date/time
- Show validation error message if available

### Issue #4: Word Count Calculation May Be Inaccurate

**Current Implementation:**
```python
words = text.split()
if len(words) > 500:
```

**Potential Issues:**
- `split()` splits on any whitespace, which may not match user's expectation
- Punctuation attached to words counts as part of word
- Empty strings in split result may affect count

**Recommendation:**
- Use more robust word counting (consider punctuation)
- Log word count for debugging
- Show word count in UI before truncation

## How License System Should Work

### Expected Behavior:

1. **Without License:**
   - ✅ Transcription works
   - ✅ Limited to 500 words
   - ✅ Shows info message if limit exceeded
   - ❌ Should NOT prompt for license during transcription

2. **With Valid License:**
   - ✅ Transcription works
   - ✅ Unlimited words
   - ✅ All features enabled

3. **With Invalid/Expired License:**
   - ✅ Transcription works (with 500-word limit)
   - ⚠️ Shows message about license status
   - ❌ Should NOT block transcription

### Current Behavior (Based on Code Review):

✅ **CORRECT**: Transcription is NOT blocked by license
✅ **CORRECT**: Word limit enforced after transcription
❌ **POTENTIAL ISSUE**: License validation may fail due to network issues
❌ **POTENTIAL ISSUE**: No clear feedback about license validation status

## Debugging Steps

If user reports "license prompt even with few words":

1. **Check if license key is saved:**
   ```python
   # Check ~/.fonixflow_config.json
   # Look for "license_key" field
   ```

2. **Check license validation logs:**
   ```python
   # Look for log messages:
   # - "check_license_key_on_startup: key=..."
   # - "License key checked: valid=..."
   # - "License validation error: ..."
   ```

3. **Check if validation is failing:**
   - Network connectivity to LemonSqueezy API
   - Local `licenses.txt` file exists and contains key
   - API response status

4. **Check where license dialog is triggered:**
   - Search for `prompt_for_license_key()` calls
   - Should only be called from "Activate" button, not during transcription

## Recommendations

### Immediate Fixes:

1. **Improve error handling in `validate_license_key()`:**
   - Distinguish between network errors and invalid keys
   - Return error type instead of just `True/False`
   - Log detailed error information

2. **Add license status indicator:**
   - Show license status in Settings tab
   - Display last validation date
   - Show validation errors if any

3. **Cache validation results:**
   - Store validation timestamp in config
   - Only re-validate if > 24 hours old
   - Allow manual "Re-validate" button

### Long-term Improvements:

1. **Offline license validation:**
   - Use cryptographic signatures
   - Validate license key format locally
   - Only require API for activation/revocation checks

2. **Better user feedback:**
   - Show license status in status bar
   - Display validation errors clearly
   - Provide troubleshooting steps

3. **Graceful degradation:**
   - If validation fails, assume license is valid if it was valid recently (< 7 days)
   - Show warning but don't block features
   - Allow user to continue with cached validation

## Code Locations Summary

- **License State**: `gui/main_window.py:95-99`
- **Validation**: `gui/main_window.py:200-229`
- **Startup Check**: `gui/main_window.py:190-198`
- **Transcription Start**: `gui/main_window.py:1775-1933`
- **Word Limit**: `gui/main_window.py:2100-2113`
- **License Dialog**: `gui/dialogs.py:4-98`
- **Settings Storage**: `gui/managers/settings_manager.py`

## Testing Checklist

- [ ] Transcription works without license (500-word limit)
- [ ] Transcription works with valid license (unlimited)
- [ ] License validation works with local `licenses.txt`
- [ ] License validation works with LemonSqueezy API
- [ ] License validation handles network errors gracefully
- [ ] License key is saved to config file
- [ ] License state persists across app restarts
- [ ] Word limit message shows only when limit exceeded
- [ ] License dialog only shows when user clicks "Activate"
