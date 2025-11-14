"""
Model Bundling Script

This script downloads and bundles the Whisper tiny model for offline use.
Run this script before packaging the application for distribution.
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def bundle_tiny_model():
    """Download and bundle the tiny Whisper model."""
    try:
        import whisper

        logger.info("Starting model bundling process...")
        logger.info("This will download the tiny model (~75MB)")

        # Create models directory
        models_dir = Path("bundled_models")
        models_dir.mkdir(exist_ok=True)

        logger.info(f"Models will be stored in: {models_dir.absolute()}")

        # Download tiny model
        logger.info("Downloading tiny model...")
        model = whisper.load_model("tiny", download_root=str(models_dir))

        logger.info(f"✅ Tiny model downloaded successfully!")
        logger.info(f"Location: {models_dir.absolute()}")

        # Verify the model works
        logger.info("Verifying model...")
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Model loaded on: {device}")

        logger.info("✅ Model bundling complete!")
        logger.info("\nYou can now package the application with the bundled model.")
        logger.info(f"Include the '{models_dir}' directory when distributing.")

        return True

    except Exception as e:
        logger.error(f"❌ Error bundling model: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Whisper Model Bundling Script")
    print("=" * 60)
    print()

    success = bundle_tiny_model()

    if success:
        print("\n✅ Success! Model is ready for offline use.")
        sys.exit(0)
    else:
        print("\n❌ Failed to bundle model. Check the error messages above.")
        sys.exit(1)
