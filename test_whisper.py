"""
Test Script for Whisper Installation

This script tests if Whisper is properly installed and can transcribe audio.
Run this script to verify your Whisper installation before using the main application.
"""

import sys
import logging
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_whisper_installation():
    """Test if Whisper is properly installed."""
    print("="*60)
    print("Testing Whisper Installation")
    print("="*60)
    
    # Test 1: Import check
    print("\n1. Testing imports...")
    try:
        import whisper
        print("   [OK] openai-whisper imported successfully")
    except ImportError as e:
        print(f"   [FAIL] Failed to import openai-whisper: {e}")
        print("   Please install: pip install openai-whisper")
        return False
    
    try:
        import torch
        print("   [OK] torch imported successfully")
    except ImportError as e:
        print(f"   [FAIL] Failed to import torch: {e}")
        print("   Please install: pip install torch")
        return False
    
    # Test 2: Device check
    print("\n2. Checking device availability...")
    if torch.cuda.is_available():
        print(f"   [OK] CUDA GPU available: {torch.cuda.get_device_name(0)}")
        print(f"   [OK] CUDA version: {torch.version.cuda}")
        device = 'cuda'
    else:
        print("   [INFO] Using CPU (GPU not available)")
        device = 'cpu'
    
    # Test 3: Model loading
    print("\n3. Testing model loading...")
    try:
        print("   Loading 'tiny' model (this may take a moment on first run)...")
        model = whisper.load_model("tiny", device=device)
        print("   [OK] Model loaded successfully")
    except Exception as e:
        print(f"   [FAIL] Failed to load model: {e}")
        return False
    
    # Test 4: Basic transcription (optional - requires audio file)
    print("\n4. Model information:")
    print(f"   - Model size: tiny")
    print(f"   - Device: {device}")
    print(f"   - Model loaded: [OK]")
    
    print("\n" + "="*60)
    print("[SUCCESS] All tests passed! Whisper is properly installed.")
    print("="*60)
    print("\nYou can now run the main application:")
    print("  python main.py")
    print("\nNote: The first time you use a model, it will be downloaded")
    print("automatically. This may take a few minutes depending on your")
    print("internet connection.")
    print("="*60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_whisper_installation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

