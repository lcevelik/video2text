"""
Enhanced Model Bundling Script - Bundle ANY Whisper model size

This script downloads and bundles Whisper models of any size for offline use.
Since you don't care about size, you can bundle the best models!

Usage:
    python bundle_models_enhanced.py --models tiny base small medium large
    python bundle_models_enhanced.py --all  # Bundle ALL models (~4.5GB)
    python bundle_models_enhanced.py --recommended  # Base + small + medium (~1.1GB)

Model sizes:
    tiny     - ~39MB  (fastest, lowest quality)
    base     - ~74MB  (fast, good quality)
    small    - ~244MB (balanced)
    medium   - ~769MB (high quality)
    large    - ~3GB   (best quality)

English-only variants (faster for English):
    tiny.en, base.en, small.en, medium.en
"""

import os
import sys
import logging
import argparse
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Model information
MODELS = {
    'tiny': {'size': '39 MB', 'speed': '100x RT'},
    'tiny.en': {'size': '39 MB', 'speed': '100x RT', 'lang': 'English only'},
    'base': {'size': '74 MB', 'speed': '67x RT'},
    'base.en': {'size': '74 MB', 'speed': '67x RT', 'lang': 'English only'},
    'small': {'size': '244 MB', 'speed': '33x RT'},
    'small.en': {'size': '244 MB', 'speed': '33x RT', 'lang': 'English only'},
    'medium': {'size': '769 MB', 'speed': '11x RT'},
    'medium.en': {'size': '769 MB', 'speed': '11x RT', 'lang': 'English only'},
    'large': {'size': '3 GB', 'speed': '5.5x RT'},
}


def get_model_info(model_name):
    """Get formatted model information."""
    info = MODELS.get(model_name, {})
    size = info.get('size', 'Unknown')
    speed = info.get('speed', 'Unknown')
    lang = info.get('lang', '99 languages')
    return f"{size:>8} | {speed:>8} | {lang}"


def bundle_models(model_names, models_dir="bundled_models"):
    """Download and bundle specified Whisper models."""
    try:
        import whisper
        import torch

        logger.info("=" * 80)
        logger.info("WHISPER MODEL BUNDLER - Enhanced Edition")
        logger.info("=" * 80)

        # Create models directory
        models_path = Path(models_dir)
        models_path.mkdir(exist_ok=True)
        logger.info(f"📁 Models directory: {models_path.absolute()}")
        logger.info("")

        # Show what will be downloaded
        logger.info("Models to bundle:")
        logger.info("-" * 80)
        logger.info(f"{'Model':<12} | {'Size':>8} | {'Speed':>8} | {'Languages'}")
        logger.info("-" * 80)

        total_size = 0
        for model_name in model_names:
            if model_name not in MODELS:
                logger.warning(f"⚠️  Unknown model: {model_name}")
                continue
            logger.info(f"{model_name:<12} | {get_model_info(model_name)}")

        logger.info("-" * 80)
        logger.info("")

        # Download each model
        success_count = 0
        failed_models = []

        for i, model_name in enumerate(model_names, 1):
            if model_name not in MODELS:
                logger.warning(f"Skipping unknown model: {model_name}")
                continue

            try:
                logger.info(f"[{i}/{len(model_names)}] Downloading {model_name}...")
                logger.info(f"    Size: {MODELS[model_name]['size']}")
                logger.info(f"    This may take a few minutes...")

                # Download model
                model = whisper.load_model(
                    model_name,
                    download_root=str(models_path)
                )

                # Verify it loaded
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                logger.info(f"    ✅ {model_name} downloaded and verified on {device}")
                logger.info("")

                success_count += 1

            except Exception as e:
                logger.error(f"    ❌ Failed to download {model_name}: {e}")
                failed_models.append(model_name)
                logger.info("")

        # Summary
        logger.info("=" * 80)
        logger.info("BUNDLING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"✅ Successfully bundled: {success_count}/{len(model_names)} models")

        if failed_models:
            logger.warning(f"❌ Failed models: {', '.join(failed_models)}")

        logger.info(f"📁 Location: {models_path.absolute()}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Run: python build_standalone_enhanced.py --bundle-models")
        logger.info("  2. Distribute the entire package folder")
        logger.info("  3. Users can run offline - no installation needed!")
        logger.info("")

        return success_count > 0

    except ImportError as e:
        logger.error("❌ Required packages not found!")
        logger.error("Install with: pip install openai-whisper torch")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bundle Whisper models for offline distribution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bundle_models_enhanced.py --models base small
  python bundle_models_enhanced.py --all
  python bundle_models_enhanced.py --recommended
  python bundle_models_enhanced.py --models large  # Best quality, ~3GB
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--models',
        nargs='+',
        choices=list(MODELS.keys()),
        help='Specific models to bundle'
    )
    group.add_argument(
        '--all',
        action='store_true',
        help='Bundle ALL models (~4.5GB total)'
    )
    group.add_argument(
        '--recommended',
        action='store_true',
        help='Bundle base, small, medium (~1.1GB) - good balance'
    )

    parser.add_argument(
        '--output-dir',
        default='bundled_models',
        help='Output directory for bundled models (default: bundled_models)'
    )

    args = parser.parse_args()

    # Determine which models to bundle
    if args.all:
        models_to_bundle = list(MODELS.keys())
        logger.info("📦 Bundling ALL models (~4.5GB)")
    elif args.recommended:
        models_to_bundle = ['base', 'small', 'medium']
        logger.info("📦 Bundling recommended models (base, small, medium)")
    else:
        models_to_bundle = args.models

    # Bundle the models
    success = bundle_models(models_to_bundle, args.output_dir)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
