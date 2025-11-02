# Bug Fixes - Verified and Fixed

## Bug 1: Static Scanner Execution Logic - ✅ FIXED

**Issue:** 
The static scanner code (lines 77-79) was outside the `if not dynamic_only:` block, causing it to always execute regardless of the `dynamic_only` flag. When `dynamic_only=True`, users expected only dynamic scanning, but static scanning still ran.

**Location:** `verimodel/cli.py` lines 74-83

**Before (Buggy Code):**
```python
# ============ QUÉT TĨNH ============
if not dynamic_only:
    console.print("[bold blue]📊 Đang chạy quét tĩnh...[/bold blue]")
static_scanner = StaticScanner()  # ❌ OUTSIDE if block
static_result = static_scanner.scan_file(file_path)  # ❌ OUTSIDE if block
results["static"] = static_result  # ❌ OUTSIDE if block

# Hiển thị kết quả quét tĩnh
_display_static_results(static_result, verbose)  # ❌ OUTSIDE if block
console.print()  # ❌ OUTSIDE if block
```

**After (Fixed Code):**
```python
# ============ QUÉT TĨNH ============
if not dynamic_only:
    console.print("[bold blue]📊 Đang chạy quét tĩnh...[/bold blue]")
    static_scanner = StaticScanner()  # ✅ INSIDE if block
    static_result = static_scanner.scan_file(file_path)  # ✅ INSIDE if block
    results["static"] = static_result  # ✅ INSIDE if block

    # Hiển thị kết quả quét tĩnh
    _display_static_results(static_result, verbose)  # ✅ INSIDE if block
    console.print()  # ✅ INSIDE if block
```

**Fix Applied:**
- Lines 77-79 and 82-83 are now properly indented inside the `if not dynamic_only:` block
- Static scanning now only runs when `dynamic_only=False` (which is the default)
- When `dynamic_only=True`, static scanning is properly skipped

**Verification:**
- ✅ No linter errors
- ✅ Code logic now correctly respects the `dynamic_only` flag
- ✅ Consistent with dynamic scanner logic pattern

---

## Bug 2: `.cursor/worktrees.json` with npm install - ⚠️ NOT FOUND IN WORKSPACE

**Issue:**
The `.cursor/worktrees.json` file contains an `npm install` command in a pure Python project. This is incorrect as:
1. This is a Python project with no `package.json`
2. `npm install` is a Node.js command, not relevant here
3. The file appears to be an accidentally committed editor configuration

**Expected Action:**
1. Remove the file if it's editor-specific configuration
2. OR replace `npm install` with Python setup commands like `pip install -r requirements.txt`
3. Add `.cursor/` to `.gitignore` if it's editor-specific

**Note:**
The file `.cursor/worktrees.json` was not found in the current workspace. It may be:
- In a parent `.cursor` directory outside this workspace
- Already removed
- In a different branch/commit

**Recommendation:**
If the file exists elsewhere, check for:
```json
{
  "command": "npm install"  // ❌ Should be removed or changed
}
```

**Suggested Fix (if file exists):**
1. **Option A - Remove:** Delete `.cursor/worktrees.json` and add to `.gitignore`:
   ```
   .cursor/
   ```
2. **Option B - Fix Content:** Replace with Python setup:
   ```json
   {
     "command": "pip install -r requirements.txt"
   }
   ```

**Action Required:**
- Check if file exists in parent directories or git history
- If found, apply one of the fixes above
- Add `.cursor/` to `.gitignore` to prevent accidental commits

---

## Summary

✅ **Bug 1: FIXED** - Static scanner now correctly respects `dynamic_only` flag
⚠️ **Bug 2: NOT FOUND** - File not in current workspace, may need manual verification

**Date:** 2024
**Status:** Bug 1 verified and fixed. Bug 2 requires manual check if file exists elsewhere.

