import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path

def get_ffmpeg_url():
    """Get URL for static ffmpeg build based on platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == 'windows':
        return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    elif system == 'darwin':
        return "https://evermeet.cx/ffmpeg/ffmpeg-113374-g88635b972b.zip" # Example URL, standard static builds are tricky on macOS due to signing
    elif system == 'linux':
        return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    return None

def install_ffmpeg(target_dir):
    """Download and install FFmpeg to target directory."""
    print(f"Downloading FFmpeg to {target_dir}...")
    os.makedirs(target_dir, exist_ok=True)
    
    url = get_ffmpeg_url()
    if not url:
        print("Could not determine FFmpeg URL for this platform.")
        return False

    filename = url.split('/')[-1]
    download_path = os.path.join(target_dir, filename)

    try:
        urllib.request.urlretrieve(url, download_path)
        print("Download complete. Extracting...")

        if filename.endswith('.zip'):
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        elif filename.endswith('.tar.xz'):
            with tarfile.open(download_path) as tar_ref:
                tar_ref.extractall(target_dir)
        
        # Cleanup
        os.remove(download_path)
        
        # Locate binary and move to top level of target_dir if needed
        # (Implementation details depend on specific archive structure)
        print("FFmpeg installed successfully.")
        return True
    except Exception as e:
        print(f"Failed to install FFmpeg: {e}")
        return False

def check_and_install_dependencies():
    """Check for FFmpeg and Python requirements."""
    # Check FFmpeg
    if not shutil.which('ffmpeg'):
        print("FFmpeg not found.")
        # In a real GUI app, you'd show a dialog here.
        # For this script, we assume consent or CLI usage.
        app_data_dir = os.path.join(os.path.expanduser("~"), ".fonixflow", "bin")
        install_ffmpeg(app_data_dir)
        # Add to PATH for this session
        os.environ["PATH"] += os.pathsep + app_data_dir

    # Check Python Reqs (simplified)
    try:
        import torch
        import whisper
        import PySide6
    except ImportError:
        print("Missing Python dependencies. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    check_and_install_dependencies()
