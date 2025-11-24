# Universal Binary Build Guide for FonixFlow

## Current Status

The build scripts (`build_macos.sh` and `build_macos_free.sh`) currently create **architecture-specific** builds that work on either:
- Apple Silicon (M1/M2/M3/M4) Macs - **ARM64**
- Intel Macs - **x86_64**

## Why Universal Binaries Don't Work Currently

To create a **universal binary** (fat binary) that works on both architectures, ALL Python packages must be compiled as universal binaries. Currently, your Python packages (PyTorch, markupsafe, numpy, etc.) are compiled **only for ARM64**.

### The Error:
```
PyInstaller.utils.osx.IncompatibleBinaryArchError: markupsafe/_speedups.cpython-310-darwin.so is not a fat binary!
```

## Options for Universal Binary Support

### Option 1: Architecture-Specific Builds (CURRENT - RECOMMENDED)

Build separate DMGs for each architecture. This is the **standard approach** used by most macOS apps.

**Pros:**
- Works with current setup
- Smaller file sizes
- Faster builds
- Native performance on each architecture

**Cons:**
- Need to distribute two separate DMG files

**How to use:**
```bash
# On Apple Silicon Mac - creates ARM64 build
./build_macos.sh
# Output: dist/FonixFlow_macOS_Silicon.dmg

# On Intel Mac - creates x86_64 build  
./build_macos.sh
# Output: dist/FonixFlow_macOS_Intel.dmg
```

### Option 2: Reinstall Python Packages as Universal Binaries

Reinstall all dependencies as universal binaries using pip with specific flags.

**Steps:**
```bash
# 1. Create a new virtual environment
python3 -m venv venv_universal
source venv_universal/bin/activate

# 2. Set environment variables for universal build
export ARCHFLAGS="-arch arm64 -arch x86_64"
export MACOSX_DEPLOYMENT_TARGET="10.15"

# 3. Reinstall all packages from scratch
pip install --no-binary :all: --force-reinstall -r requirements.txt
```

**Pros:**
- Single DMG works on both architectures
- Better for distribution

**Cons:**
- Complex setup
- Longer build times
- Some packages may not support universal compilation
- PyTorch universal builds are very large

**Likelihood of success:** Medium - Some packages (especially PyTorch) may not support this approach.

### Option 3: Use Conda with Universal Build

Conda can manage universal Python environments more easily.

**Steps:**
```bash
# Install conda if not already installed
brew install --cask miniconda

# Create universal environment
CONDA_SUBDIR=osx-64 conda create -n fonixflow_universal python=3.10
conda activate fonixflow_universal
conda config --env --set subdir osx-64

# Install packages
conda install pytorch torchvision torchaudio -c pytorch
pip install -r requirements.txt
```

**Pros:**
- Conda handles architecture compatibility better
- More reliable for scientific packages

**Cons:**
- Requires conda installation
- Different dependency management
- Still may not create true universal binaries

### Option 4: Keep Current Architecture-Specific Approach (RECOMMENDED)

**This is what most professional macOS apps do**, including:
- Google Chrome (separate downloads for Intel and Apple Silicon)
- Many other large applications

**Recommendation:** Provide both DMG files for download with clear labels:
- `FonixFlow_macOS_Silicon.dmg` - For M1/M2/M3/M4 Macs
- `FonixFlow_macOS_Intel.dmg` - For Intel Macs

Users on Apple Silicon can run either version (Intel via Rosetta 2), but the native ARM64 version will be faster.

## Current Build Configuration

I've **reverted** the spec files back to `target_arch=None` which builds for the current architecture. This is the most reliable approach.

To build for a specific architecture on an Apple Silicon Mac:

```bash
# Build for ARM64 (native)
./build_macos.sh

# Build for Intel (using Rosetta)
arch -x86_64 ./build_macos.sh
```

## For Distribution

1. **Primary Users (Apple Silicon):** Use `build_macOS.sh` on an M1/M2/M3/M4 Mac
2. **Intel Users:** Either:
   - Build on an Intel Mac, OR
   - Use Rosetta 2: `arch -x86_64 ./build_macos.sh` on Apple Silicon
   
3. Distribute both DMG files with clear architecture labels

## Summary

**Current status:** Architecture-specific builds (RECOMMENDED)
**To create universal binaries:** Would require reinstalling all Python packages as universal binaries (complex and may not work with PyTorch)
**Recommended approach:** Keep architecture-specific builds and distribute both versions
