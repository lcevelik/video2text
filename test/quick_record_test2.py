import os
import sys
import shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication  # type: ignore
from PySide6.QtCore import QTimer  # type: ignore

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.workers import RecordingWorker, DEFAULT_SPEAKER_FOLLOW_SYSTEM  # type: ignore
from gui.utils import get_audio_devices  # type: ignore
import sounddevice as sd  # type: ignore


def pick_loopback_index() -> int:
    """Pick a likely-working system audio source index.

    Order of preference:
    1) Any input-capable device with monitor-like name (stereo mix, loopback, speakers wave, etc.)
    2) Any input-capable device among our simplified loopbacks list
    3) WASAPI output-only device (opened with loopback) from loopbacks list
    4) Fall back to DEFAULT_SPEAKER_FOLLOW_SYSTEM
    """
    try:
        _mics, loopbacks = get_audio_devices()
        devs = sd.query_devices()
        hostapis = sd.query_hostapis()

        # 1) Probe all devices for input-monitor style
        keywords = ['stereo mix', 'loopback', 'monitor', 'speakers wave', 'speakers', 'output', 'soundflower', 'blackhole']
        for i, info in enumerate(devs):
            try:
                name = str(info.get('name', '')).lower()
                if info.get('max_input_channels', 0) > 0 and any(k in name for k in keywords) and all(x not in name for x in ['mic', 'microphone']):
                    ha_name = hostapis[info['hostapi']]['name'].lower()
                    print(f"[quick_record_test] Using input-monitor: idx={i} name='{name}' hostapi={ha_name}")
                    return i
            except Exception:
                continue

        # 2) Any input-capable device from loopbacks list
        for idx, label in loopbacks:
            try:
                info = devs[idx]
                if info.get('max_input_channels', 0) > 0:
                    ha_name = hostapis[info['hostapi']]['name'].lower()
                    print(f"[quick_record_test] Using input in loopbacks: idx={idx} label='{label}' hostapi={ha_name}")
                    return idx
            except Exception:
                continue

        # 3) WASAPI output-only from loopbacks
        for idx, label in loopbacks:
            try:
                info = devs[idx]
                ha_name = hostapis[info['hostapi']]['name'].lower()
                if 'wasapi' in ha_name and info.get('max_output_channels', 0) > 0 and info.get('max_input_channels', 0) == 0:
                    print(f"[quick_record_test] Using WASAPI output loopback: idx={idx} label='{label}'")
                    return idx
            except Exception:
                continue
    except Exception as e:
        print(f"[quick_record_test] Device selection failed: {e}")
    return DEFAULT_SPEAKER_FOLLOW_SYSTEM


def configure_ffmpeg_in_process():
    """Try to make ffmpeg available to pydub in this process."""
    try:
        from pydub import AudioSegment  # type: ignore
        if shutil.which('ffmpeg'):
            # PATH already has ffmpeg; ensure pydub uses it
            AudioSegment.converter = 'ffmpeg'
            return
        local_winget = str(Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "WinGet" / "Packages")
        common_paths = [
            r"C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            r"C:\\Program Files\\FFmpeg\\bin\\ffmpeg.exe",
            str(Path.home() / "scoop" / "apps" / "ffmpeg" / "current" / "bin" / "ffmpeg.exe"),
            str(Path(local_winget) / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe" / "ffmpeg-8.0-full_build" / "bin" / "ffmpeg.exe"),
        ]
        for p in common_paths:
            if Path(p).exists():
                try:
                    AudioSegment.converter = p
                except Exception:
                    os.environ['FFMPEG_BINARY'] = p
                print(f"[quick_record_test] Using ffmpeg at: {p}")
                return
    except Exception:
        pass


def main():
    app = QApplication(sys.argv)

    out_dir = Path.home() / "FonixFlow" / "Recordings"
    out_dir.mkdir(parents=True, exist_ok=True)

    configure_ffmpeg_in_process()

    loopback_idx = pick_loopback_index()
    print("[quick_record_test] Starting 12s recording...")

    worker = RecordingWorker(
        output_dir=str(out_dir),
        mic_device=None,  # auto-detect mic
        speaker_device=loopback_idx,
        filter_settings={}
    )

    def on_complete(path, duration):
        print(f"[quick_record_test] Recording complete: {path} ({duration:.1f}s)")
        QTimer.singleShot(500, app.quit)

    def on_error(msg):
        print(f"[quick_record_test] Recording error: {msg}")
        QTimer.singleShot(500, app.quit)

    worker.recording_complete.connect(on_complete)
    worker.recording_error.connect(on_error)

    worker.start()

    # Stop after 12 seconds
    QTimer.singleShot(12000, worker.stop)
    # Safety quit after 15 seconds
    QTimer.singleShot(15000, app.quit)

    app.exec()


if __name__ == "__main__":
    main()
