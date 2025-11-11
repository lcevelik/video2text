"""
GPU Diagnostic Tool

This script checks if your system is ready for GPU acceleration with Whisper.
"""

import sys

print("="*60)
print("GPU Diagnostic Tool")
print("="*60)

# Check 1: PyTorch installation
print("\n1. Checking PyTorch installation...")
try:
    import torch
    print(f"   [OK] PyTorch version: {torch.__version__}")
    
    # Check if CUDA is built into PyTorch
    cuda_built = hasattr(torch.version, 'cuda') and torch.version.cuda is not None
    if cuda_built:
        print(f"   [OK] PyTorch built with CUDA: {torch.version.cuda}")
    else:
        print("   [WARNING] PyTorch is CPU-only version (no CUDA support)")
        print("   [INFO] You need to install PyTorch with CUDA support")
        
except ImportError:
    print("   [ERROR] PyTorch not installed")
    sys.exit(1)

# Check 2: CUDA availability
print("\n2. Checking CUDA availability...")
if torch.cuda.is_available():
    print("   [OK] CUDA is available!")
    print(f"   [OK] GPU Count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"   [OK] GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"   [OK] GPU {i} Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
else:
    print("   [WARNING] CUDA is not available")
    
    # Check if it's because PyTorch doesn't have CUDA
    if not cuda_built:
        print("   [REASON] PyTorch was installed without CUDA support")
    else:
        print("   [REASON] Possible causes:")
        print("      - NVIDIA GPU drivers not installed")
        print("      - CUDA toolkit not installed")
        print("      - GPU not detected by system")

# Check 3: System GPU detection (Windows)
print("\n3. Checking system GPU detection (Windows)...")
try:
    import subprocess
    result = subprocess.run(
        ['nvidia-smi'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print("   [OK] NVIDIA GPU detected by system")
        print("   [INFO] nvidia-smi output:")
        lines = result.stdout.split('\n')[:5]
        for line in lines:
            if line.strip():
                print(f"      {line}")
    else:
        print("   [WARNING] nvidia-smi not found or failed")
        print("   [INFO] This might mean:")
        print("      - NVIDIA drivers not installed")
        print("      - No NVIDIA GPU in system")
except (FileNotFoundError, subprocess.TimeoutExpired):
    print("   [WARNING] nvidia-smi command not found")
    print("   [INFO] NVIDIA drivers may not be installed")

# Summary and recommendations
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if torch.cuda.is_available():
    print("[SUCCESS] Your system is ready for GPU acceleration!")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print("\nYour application will automatically use GPU when available.")
else:
    print("[INFO] GPU acceleration is not currently available.")
    print("\nTo enable GPU support:")
    print("\n1. Verify you have an NVIDIA GPU:")
    print("   - Check Device Manager > Display adapters")
    print("   - Look for NVIDIA GeForce, Quadro, or Tesla")
    
    print("\n2. Install NVIDIA GPU drivers:")
    print("   - Download from: https://www.nvidia.com/drivers")
    print("   - Install the latest Game Ready or Studio drivers")
    
    print("\n3. Install PyTorch with CUDA support:")
    print("   - Uninstall current PyTorch:")
    print("     pip uninstall torch torchaudio")
    print("   - Install CUDA version (check your CUDA version first):")
    print("     # For CUDA 11.8:")
    print("     pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("     # For CUDA 12.1:")
    print("     pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121")
    
    print("\n4. Check your CUDA version:")
    print("   - Run: nvidia-smi")
    print("   - Look for 'CUDA Version' in the output")
    
    if not cuda_built:
        print("\n[CURRENT ISSUE] PyTorch is CPU-only version")
        print("You need to reinstall PyTorch with CUDA support (see step 3 above)")

print("\n" + "="*60)

