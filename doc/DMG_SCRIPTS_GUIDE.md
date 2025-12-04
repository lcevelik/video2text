# DMG Creation Scripts Guide

FonixFlow has multiple DMG creation scripts for different use cases. This guide explains when to use each one.

## Available Scripts

### 1. `create_clean_dmg.sh` ⭐ **Recommended for Quick DMG**
**Simple, fast DMG without custom background**

```bash
./create_clean_dmg.sh
```

**Features:**
- ✓ Fastest option
- ✓ No background image
- ✓ Basic layout (app + Applications link)
- ✓ Smallest file size
- ✓ Most reliable

**Use when:**
- Quick testing
- Internal builds
- When background image isn't needed
- When speed is priority

**Output:** `dist/FonixFlow.dmg`

---

### 2. `scripts/create_custom_dmg.sh` ⭐ **Recommended for Production**
**Professional DMG with custom background and layout**

```bash
./scripts/create_custom_dmg.sh "FonixFlow" "dist/FonixFlow.app" "dist/FonixFlow.dmg" "assets/dmg_background.png"
```

**Features:**
- ✓ Custom background image
- ✓ Professional layout
- ✓ Icon positioning
- ✓ Window size control
- ✓ Used by `full_release.sh`

**Use when:**
- Production releases
- Public distribution
- When you want branded DMG
- Official releases

**Output:** Custom DMG name specified

---

### 3. `create_dmg_working.sh` ⭐ **Recommended for Custom Layout**
**DMG with fixed window size and icon positioning**

```bash
./create_dmg_working.sh
```

**Features:**
- ✓ Fixed window size (600x400)
- ✓ Precise icon positioning
- ✓ No background (clean look)
- ✓ Reliable layout

**Use when:**
- You need specific window size
- You want clean, simple layout
- Testing different layouts

**Output:** `dist/FonixFlow.dmg`

---

### 4. `create_dmg_simple.sh`
**DMG with background (simplified approach)**

```bash
./create_dmg_simple.sh
```

**Features:**
- ✓ Background image support
- ✓ Simplified approach
- ✓ Window size locking
- ⚠ More complex than `create_custom_dmg.sh`

**Use when:**
- You prefer this specific implementation
- Testing background options

**Output:** `dist/FonixFlow.dmg`

---

### 5. `create_dmg.sh`
**DMG with faded background**

```bash
./create_dmg.sh
```

**Features:**
- ✓ Faded background (20% opacity)
- ✓ Custom layout
- ⚠ Most complex script
- ⚠ Requires PIL/Pillow for fading

**Use when:**
- You want subtle background effect
- Testing different visual styles

**Output:** `dist/FonixFlow.dmg`

---

## Icon Creation

### `create_icns.sh` 🎨
**Creates macOS .icns icon file from PNG**

```bash
./create_icns.sh
```

**What it does:**
- Generates all required icon sizes (16x16 to 1024x1024)
- Creates `assets/fonixflow_icon.icns`
- Required for app bundle

**Use when:**
- Building app for first time
- Icon has been updated
- `.icns` file is missing

**Output:** `assets/fonixflow_icon.icns`

---

## Quick Reference

| Script | Speed | Background | Layout | Best For |
|--------|-------|------------|--------|----------|
| `create_clean_dmg.sh` | ⚡⚡⚡ | ❌ | Basic | Quick builds |
| `scripts/create_custom_dmg.sh` | ⚡⚡ | ✅ | Custom | Production |
| `create_dmg_working.sh` | ⚡⚡ | ❌ | Fixed | Custom layout |
| `create_dmg_simple.sh` | ⚡ | ✅ | Custom | Background testing |
| `create_dmg.sh` | ⚡ | ✅ Faded | Custom | Visual testing |

---

## Integration with Release Workflow

### Automated Release
The `full_release.sh` script uses `create_custom_dmg.sh`:

```bash
./scripts/full_release.sh 1.0.1
# Uses: scripts/create_custom_dmg.sh
```

### Manual Release
Choose based on your needs:

```bash
# Quick test
./create_clean_dmg.sh

# Production release
./scripts/create_custom_dmg.sh "FonixFlow" "dist/FonixFlow.app" "dist/FonixFlow.dmg" "assets/dmg_background.png"
```

---

## Recommendations

### For Development/Testing
```bash
./create_clean_dmg.sh
```
- Fastest
- No dependencies
- Reliable

### For Production Releases
```bash
./scripts/create_custom_dmg.sh "FonixFlow" "dist/FonixFlow.app" "dist/FonixFlow.dmg" "assets/dmg_background.png"
```
- Professional appearance
- Branded background
- Used by automated workflow

### For Custom Layouts
```bash
./create_dmg_working.sh
```
- Fixed window size
- Precise positioning
- Clean appearance

---

## Troubleshooting

### "Background image not found"
- Ensure `assets/dmg_background.png` exists
- Or use `create_clean_dmg.sh` (no background)

### "Window size not correct"
- Use `create_dmg_working.sh` for fixed size
- Or edit AppleScript in `create_custom_dmg.sh`

### "DMG creation fails"
- Try `create_clean_dmg.sh` (simplest)
- Check disk space
- Ensure app is built first

### "Icon not showing"
- Run `./create_icns.sh` first
- Check `assets/fonixflow_icon.icns` exists

---

## Script Dependencies

| Script | Dependencies |
|--------|--------------|
| `create_clean_dmg.sh` | None (uses system tools) |
| `scripts/create_custom_dmg.sh` | Background image (optional) |
| `create_dmg_working.sh` | None |
| `create_dmg_simple.sh` | PIL/Pillow (optional, has fallback) |
| `create_dmg.sh` | PIL/Pillow (for fading) |
| `create_icns.sh` | `sips` (macOS built-in) |

---

## Updating Scripts

All scripts are in the project root or `scripts/` directory. They can be customized:

- **Window size**: Edit `WINDOW_W` and `WINDOW_H` variables
- **Icon positions**: Edit `APP_ICON_X/Y` and `APPS_LINK_X/Y`
- **Background**: Change background image path
- **Compression**: Adjust `zlib-level` in `hdiutil convert`

---

## Best Practices

1. **Use `create_clean_dmg.sh` for testing** - Fast and reliable
2. **Use `create_custom_dmg.sh` for releases** - Professional appearance
3. **Run `create_icns.sh` before building** - Ensures icon is ready
4. **Test DMG before distribution** - Always verify it works
5. **Keep scripts updated** - Use latest version for best results

---

## Related Documentation

- [DMG_CREATION_GUIDE.md](../DMG_CREATION_GUIDE.md) - Detailed DMG creation guide
- [RELEASE_WORKFLOW.md](./RELEASE_WORKFLOW.md) - Complete release workflow
- [BUILD_MACOS.md](./BUILD_MACOS.md) - Build instructions
