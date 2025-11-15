"""
Enhanced GUI Module with Basic/Advanced Modes

This module provides a dual-mode GUI for the video transcription application:
- Basic Mode: Simple, automatic transcription with drag-and-drop
- Advanced Mode: Full control with all options and audio recording

Built with Tkinter for cross-platform compatibility.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from pathlib import Path
import os
import time
import json
from typing import Optional, Dict, Any

from audio_extractor import AudioExtractor
from transcriber import Transcriber

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for persistent settings."""

    CONFIG_FILE = "app_config.json"

    @staticmethod
    def load() -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(Config.CONFIG_FILE):
            try:
                with open(Config.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"mode": "basic", "theme": "light"}

    @staticmethod
    def save(config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(Config.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save config: {e}")


class EnhancedTranscriptionApp:
    """Enhanced GUI application with Basic/Advanced modes."""

    def __init__(self, root):
        """
        Initialize the Enhanced GUI application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Video/Audio to Text - Whisper Transcription")
        self.root.geometry("950x850")
        self.root.resizable(True, True)

        # Load configuration
        self.config = Config.load()
        self.current_mode = self.config.get("mode", "basic")

        # Application state
        self.video_path = None
        self.video_duration = None
        self.audio_path = None
        self.transcription_result = None
        self.is_transcribing = False
        self.transcription_thread = None
        self.timing_data = None
        self.total_time = None
        self.transcription_time = None
        self.recording = False
        self.recorded_audio_path = None

        # Initialize components
        self.audio_extractor = AudioExtractor()
        self.transcriber = None

        # Auto model selection state
        self.auto_model_enabled = True
        self.model_upgrade_attempts = 0

        # Setup logging to GUI
        self.setup_logging()

        # Build UI
        self.build_ui()

        # Center window
        self.center_window()

        # Show appropriate mode
        self.switch_mode(self.current_mode)

    def setup_logging(self):
        """Setup logging handler to display logs in GUI."""
        self.log_handler = GUILogHandler(self)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.log_handler)

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def build_ui(self):
        """Build the complete user interface."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(10, weight=1)

        # Mode switcher at top
        self.build_mode_switcher()

        # Build both modes (will show/hide based on selection)
        self.build_basic_mode()
        self.build_advanced_mode()

        # Common elements (progress bar and transcription display)
        self.build_common_elements()

        # Status bar
        self.build_status_bar()

    def build_mode_switcher(self):
        """Build the mode switcher section."""
        switcher_frame = ttk.Frame(self.main_frame, padding="5")
        switcher_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(
            switcher_frame,
            text="Video/Audio to Text Transcription",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT, padx=10)

        # Mode buttons
        mode_buttons_frame = ttk.Frame(switcher_frame)
        mode_buttons_frame.pack(side=tk.RIGHT)

        self.basic_mode_btn = ttk.Button(
            mode_buttons_frame,
            text="📱 Basic Mode",
            command=lambda: self.switch_mode("basic"),
            width=15
        )
        self.basic_mode_btn.pack(side=tk.LEFT, padx=2)

        self.advanced_mode_btn = ttk.Button(
            mode_buttons_frame,
            text="⚙️ Advanced Mode",
            command=lambda: self.switch_mode("advanced"),
            width=15
        )
        self.advanced_mode_btn.pack(side=tk.LEFT, padx=2)

    def build_basic_mode(self):
        """Build the Basic Mode UI."""
        self.basic_frame = ttk.Frame(self.main_frame)
        self.basic_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.basic_frame.columnconfigure(0, weight=1)

        # Description
        desc_text = "Simple, automatic transcription. Just drop your file and click Transcribe!"
        ttk.Label(
            self.basic_frame,
            text=desc_text,
            font=("Arial", 10),
            foreground="gray"
        ).grid(row=0, column=0, pady=10)

        # Large drag-and-drop area
        self.drop_frame = tk.Frame(
            self.basic_frame,
            bg="#f0f0f0",
            relief=tk.RIDGE,
            borderwidth=2,
            height=200
        )
        self.drop_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10, padx=20)

        # Drag-drop label
        self.drop_label = tk.Label(
            self.drop_frame,
            text="🎬 Drag & Drop Video/Audio File Here\n\nor click Browse to select file",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#666"
        )
        self.drop_label.pack(expand=True, fill=tk.BOTH, pady=50)

        # Make drop area clickable
        self.drop_label.bind("<Button-1>", lambda e: self.browse_file())
        self.drop_frame.bind("<Button-1>", lambda e: self.browse_file())

        # Setup drag and drop (simplified)
        self.setup_drag_drop()

        # Selected file display
        self.basic_file_label = ttk.Label(
            self.basic_frame,
            text="No file selected",
            foreground="gray",
            font=("Arial", 10)
        )
        self.basic_file_label.grid(row=2, column=0, pady=5)

        # Recording button (Basic mode)
        record_frame = ttk.Frame(self.basic_frame)
        record_frame.grid(row=3, column=0, pady=10)

        self.basic_record_btn = ttk.Button(
            record_frame,
            text="🎤 Record Audio (Mic + Speaker)",
            command=self.show_recording_dialog,
            width=30
        )
        self.basic_record_btn.pack(side=tk.LEFT, padx=5)

        ttk.Label(
            record_frame,
            text="(Records both microphone and system audio simultaneously)",
            font=("Arial", 8),
            foreground="gray"
        ).pack(side=tk.LEFT, padx=5)

        # Large transcribe button
        self.basic_transcribe_btn = ttk.Button(
            self.basic_frame,
            text="✨ Transcribe Now",
            command=self.start_transcription,
            state=tk.DISABLED
        )
        self.basic_transcribe_btn.grid(row=4, column=0, pady=20)

        # Configure button style for larger size
        style = ttk.Style()
        style.configure("Large.TButton", font=("Arial", 12, "bold"), padding=10)
        self.basic_transcribe_btn.configure(style="Large.TButton")

        # Info text
        info_text = "🤖 Auto-selection: Starts with fastest model, upgrades if needed for better quality"
        ttk.Label(
            self.basic_frame,
            text=info_text,
            font=("Arial", 9),
            foreground="blue"
        ).grid(row=5, column=0, pady=5)

    def build_advanced_mode(self):
        """Build the Advanced Mode UI (enhanced version of original)."""
        self.advanced_frame = ttk.Frame(self.main_frame)
        self.advanced_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.advanced_frame.columnconfigure(1, weight=1)

        row = 0

        # File selection
        file_frame = ttk.LabelFrame(self.advanced_frame, text="Media File (Video or Audio)", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Selected File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.adv_file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.adv_file_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        ttk.Button(
            file_frame,
            text="Browse...",
            command=self.browse_file
        ).grid(row=0, column=2, padx=5)

        row += 1

        # Audio Recording Section
        record_frame = ttk.LabelFrame(self.advanced_frame, text="Audio Recording", padding="10")
        record_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.record_btn = ttk.Button(
            record_frame,
            text="🎤 Start Recording (Mic + Speaker)",
            command=self.toggle_recording,
            width=30
        )
        self.record_btn.pack(side=tk.LEFT, padx=5)

        self.record_status_label = ttk.Label(
            record_frame,
            text="Records both microphone and speaker audio simultaneously",
            foreground="gray"
        )
        self.record_status_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            record_frame,
            text="⚙️ Audio Settings",
            command=self.show_audio_settings,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        row += 1

        # Model selection with auto mode
        model_frame = ttk.LabelFrame(self.advanced_frame, text="Whisper Model", padding="10")
        model_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Auto mode checkbox
        self.auto_model_var = tk.BooleanVar(value=True)
        auto_check = ttk.Checkbutton(
            model_frame,
            text="🤖 Auto-select model (starts with tiny, upgrades if needed)",
            variable=self.auto_model_var,
            command=self.toggle_auto_model
        )
        auto_check.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        ttk.Label(model_frame, text="Model Size:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.model_var = tk.StringVar(value="tiny")
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=Transcriber.MODEL_SIZES,
            state="disabled",  # Disabled by default (auto mode)
            width=15
        )
        self.model_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_change)

        # Model info label
        self.model_info_label = ttk.Label(
            model_frame,
            text="(Auto: starts with tiny for speed)",
            foreground="gray",
            font=("Arial", 8)
        )
        self.model_info_label.grid(row=1, column=2, sticky=tk.W, padx=5)

        # Model help button
        ttk.Button(
            model_frame,
            text="?",
            width=3,
            command=self.show_model_help
        ).grid(row=1, column=3, padx=5)

        row += 1

        # Language selection with multi-language support
        language_frame = ttk.LabelFrame(self.advanced_frame, text="Language Settings", padding="10")
        language_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(language_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=5)

        # Common languages supported by Whisper
        self.languages = {
            "Auto-detect": None,
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese (Mandarin)": "zh",
            "Arabic": "ar",
            "Dutch": "nl",
            "Polish": "pl",
            "Turkish": "tr",
            "Swedish": "sv",
            "Norwegian": "no",
            "Finnish": "fi",
            "Greek": "el",
            "Czech": "cs",
            "Hungarian": "hu",
            "Romanian": "ro",
            "Hindi": "hi",
            "Thai": "th",
            "Vietnamese": "vi",
            "Indonesian": "id",
            "Hebrew": "he",
            "Ukrainian": "uk",
            "Catalan": "ca",
            "Danish": "da"
        }

        self.language_var = tk.StringVar(value="Auto-detect")
        language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=list(self.languages.keys()),
            state="readonly",
            width=25
        )
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(
            language_frame,
            text="(Auto-detect handles multi-language content)",
            foreground="gray",
            font=("Arial", 8)
        ).grid(row=0, column=2, sticky=tk.W, padx=5)

        # Multi-language detection option
        self.detect_languages_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            language_frame,
            text="🌍 Detect multiple languages in same file",
            variable=self.detect_languages_var
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        row += 1

        # Output format
        format_frame = ttk.LabelFrame(self.advanced_frame, text="Output Format", padding="10")
        format_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.format_var = tk.StringVar(value="txt")
        ttk.Radiobutton(
            format_frame,
            text="Plain Text (.txt)",
            variable=self.format_var,
            value="txt"
        ).grid(row=0, column=0, sticky=tk.W, padx=5)

        ttk.Radiobutton(
            format_frame,
            text="SRT Subtitles (.srt)",
            variable=self.format_var,
            value="srt"
        ).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Radiobutton(
            format_frame,
            text="VTT Subtitles (.vtt)",
            variable=self.format_var,
            value="vtt"
        ).grid(row=0, column=2, sticky=tk.W, padx=5)

        row += 1

        # Instructions/Prompt field
        instructions_frame = ttk.LabelFrame(self.advanced_frame, text="Instructions for Transcription (Optional)", padding="10")
        instructions_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        instructions_frame.columnconfigure(0, weight=1)

        ttk.Label(
            instructions_frame,
            text="Add context to help with speaker recognition and accuracy:",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Instructions text area
        self.instructions_text = scrolledtext.ScrolledText(
            instructions_frame,
            wrap=tk.WORD,
            width=80,
            height=3,
            font=("Arial", 9)
        )
        self.instructions_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # Add example text as placeholder
        example_text = "Example: Meeting between John (CEO) and Sarah (CTO) about Q4 project roadmap."
        self.instructions_text.insert(1.0, example_text)
        self.instructions_text.config(foreground="gray")

        # Bind events to clear placeholder
        def on_focus_in(event):
            if self.instructions_text.get(1.0, tk.END).strip() == example_text:
                self.instructions_text.delete(1.0, tk.END)
                self.instructions_text.config(foreground="black")

        def on_focus_out(event):
            if not self.instructions_text.get(1.0, tk.END).strip():
                self.instructions_text.insert(1.0, example_text)
                self.instructions_text.config(foreground="gray")

        self.instructions_text.bind('<FocusIn>', on_focus_in)
        self.instructions_text.bind('<FocusOut>', on_focus_out)

        row += 1

        # Control buttons
        control_frame = ttk.Frame(self.advanced_frame)
        control_frame.grid(row=row, column=0, columnspan=3, pady=10)

        self.adv_start_button = ttk.Button(
            control_frame,
            text="Start Transcription",
            command=self.start_transcription,
            state=tk.DISABLED
        )
        self.adv_start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            control_frame,
            text="Stop",
            command=self.stop_transcription,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(
            control_frame,
            text="💾 Save Transcription",
            command=self.save_transcription,
            state=tk.DISABLED
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

    def build_common_elements(self):
        """Build elements common to both modes."""
        # Progress section
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400,
            maximum=100
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # Progress percentage label
        self.progress_percent_var = tk.StringVar(value="")
        self.progress_percent_label = ttk.Label(
            progress_frame,
            textvariable=self.progress_percent_var,
            font=("Arial", 9, "bold"),
            foreground="blue"
        )
        self.progress_percent_label.grid(row=2, column=0, sticky=tk.E, pady=(2, 0))

        # Transcription text area
        text_frame = ttk.LabelFrame(self.main_frame, text="Transcription Result", padding="10")
        text_frame.grid(row=10, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Consolas", 10)
        )
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def build_status_bar(self):
        """Build the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def setup_drag_drop(self):
        """Setup drag and drop functionality (simplified for basic compatibility)."""
        # Basic click-to-browse functionality
        # Full drag-drop requires tkinterdnd2; if unavailable or initialization fails we degrade gracefully.
        try:
            from tkinterdnd2 import DND_FILES  # type: ignore
            try:
                self.drop_frame.drop_target_register(DND_FILES)
                self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
                logger.info("Drag-and-drop enabled")
            except Exception as e:
                logger.warning(f"Drag-and-drop registration failed, disabling feature: {e}")
        except ImportError:
            logger.info("tkinterdnd2 not available, using click-to-browse only")

    def on_drop(self, event):
        """Handle file drop event."""
        file_path = event.data
        # Clean up the path (remove curly braces if present)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        self.load_file(file_path)

    def toggle_auto_model(self):
        """Toggle automatic model selection."""
        self.auto_model_enabled = self.auto_model_var.get()

        if self.auto_model_enabled:
            self.model_combo.config(state="disabled")
            self.model_var.set("tiny")
            self.model_info_label.config(text="(Auto: starts with tiny for speed)")
        else:
            self.model_combo.config(state="readonly")
            self.on_model_change()

    def on_model_change(self, event=None):
        """Handle model selection change."""
        model_size = self.model_var.get()
        model_desc = Transcriber.get_model_description(model_size)
        self.model_info_label.config(text=f"({model_size}: {model_desc['description']})")

    def show_model_help(self):
        """Show detailed model information."""
        model_size = self.model_var.get()
        model_desc = Transcriber.get_model_description(model_size)

        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        device_name = f"GPU ({torch.cuda.get_device_name(0)})" if device == 'cuda' else "CPU"

        help_text = f"""Model: {model_size.upper()}

{model_desc['description']}

Speed: {model_desc['speed']}
Accuracy: {model_desc['accuracy']}
Model Size: {model_desc['size']}

Best For: {model_desc['use_case']}

Current Device: {device_name}

Auto-Selection: When enabled, starts with 'tiny' for speed,
then upgrades to larger models if quality is insufficient.
"""

        messagebox.showinfo(f"Model Information: {model_size.upper()}", help_text)

    def switch_mode(self, mode: str):
        """Switch between Basic and Advanced modes."""
        self.current_mode = mode
        self.config["mode"] = mode
        Config.save(self.config)

        if mode == "basic":
            self.basic_frame.grid()
            self.advanced_frame.grid_remove()
            self.basic_mode_btn.config(state=tk.DISABLED)
            self.advanced_mode_btn.config(state=tk.NORMAL)
        else:
            self.basic_frame.grid_remove()
            self.advanced_frame.grid()
            self.basic_mode_btn.config(state=tk.NORMAL)
            self.advanced_mode_btn.config(state=tk.DISABLED)

        logger.info(f"Switched to {mode} mode")

    def browse_file(self):
        """Open file browser to select video or audio file."""
        # Build file type filter
        video_exts = " ".join([f"*{ext}" for ext in AudioExtractor.SUPPORTED_VIDEO_FORMATS])
        audio_exts = " ".join([f"*{ext}" for ext in AudioExtractor.SUPPORTED_AUDIO_FORMATS])
        all_exts = video_exts + " " + audio_exts

        file_path = filedialog.askopenfilename(
            title="Select Video or Audio File",
            filetypes=[
                ("All supported media", all_exts),
                ("Video files", video_exts),
                ("Audio files", audio_exts),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """Load a video or audio file."""
        self.video_path = file_path
        file_name = Path(file_path).name

        # Update file labels
        if self.current_mode == "basic":
            self.basic_file_label.config(text=f"Selected: {file_name}", foreground="black")
            self.drop_label.config(text=f"✅ {file_name}\n\nClick to select different file")
            self.basic_transcribe_btn.config(state=tk.NORMAL)
        else:
            self.adv_file_label.config(text=file_name, foreground="black")
            self.adv_start_button.config(state=tk.NORMAL)

        # Determine file type
        file_type = "audio" if self.audio_extractor.is_audio_file(file_path) else "video"
        self.status_var.set(f"{file_type.capitalize()} file selected: {file_name}")
        logger.info(f"Selected {file_type} file: {file_path}")

        # Get media duration
        try:
            self.video_duration = self.audio_extractor.get_media_duration(file_path)
            if self.video_duration:
                duration_str = Transcriber._format_estimated_time(self.video_duration)
                self.status_var.set(f"{file_type.capitalize()} file selected: {file_name} ({duration_str})")
        except Exception as e:
            logger.warning(f"Could not get {file_type} duration: {e}")
            self.video_duration = None

    def toggle_recording(self):
        """Toggle audio recording."""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start audio recording."""
        self.show_recording_dialog()

    def stop_recording(self):
        """Stop audio recording."""
        if self.recording:
            self.recording = False
            self.record_btn.config(text="🎤 Start Recording (Mic + Speaker)")
            self.record_status_label.config(text="Recording stopped", foreground="green")
            logger.info("Recording stopped")

    def show_recording_dialog(self):
        """Show recording dialog for simultaneous mic + speaker recording."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Audio Recording")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(
            dialog,
            text="Audio Recording - Mic + Speaker",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        ttk.Label(
            dialog,
            text="Records both microphone and speaker audio simultaneously",
            font=("Arial", 9),
            foreground="gray"
        ).pack(pady=5)

        # Info frame
        info_frame = ttk.LabelFrame(dialog, text="What will be recorded:", padding="10")
        info_frame.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(
            info_frame,
            text="🎤 Microphone: Your voice and ambient sounds",
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=2)

        ttk.Label(
            info_frame,
            text="🔊 Speaker: System audio, music, video calls, etc.",
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=2)

        ttk.Label(
            info_frame,
            text="📝 Both sources will be mixed into one recording",
            font=("Arial", 9),
            foreground="blue"
        ).pack(anchor=tk.W, pady=2)

        # Status display
        status_label = ttk.Label(
            dialog,
            text="Ready to record",
            foreground="gray",
            font=("Arial", 10)
        )
        status_label.pack(pady=10)

        # Duration display
        duration_label = ttk.Label(
            dialog,
            text="Duration: 0:00",
            font=("Arial", 9, "bold"),
            foreground="blue"
        )
        duration_label.pack(pady=5)

        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)

        recording_active = [False]  # Mutable flag
        start_time = [None]  # Recording start time

        def update_duration():
            """Update recording duration display."""
            if recording_active[0] and start_time[0]:
                elapsed = time.time() - start_time[0]
                mins = int(elapsed // 60)
                secs = int(elapsed % 60)
                duration_label.config(text=f"Duration: {mins}:{secs:02d}")
                dialog.after(1000, update_duration)

        def start_record():
            # Check if audio devices are available first
            try:
                import sounddevice as sd
                devices = sd.query_devices()
                has_input = any(d['max_input_channels'] > 0 for d in devices)

                if not has_input:
                    status_label.config(
                        text="❌ No audio input devices found! Please connect a microphone.",
                        foreground="red"
                    )
                    return
            except Exception as e:
                logger.error(f"Error checking audio devices: {e}")

            recording_active[0] = True
            start_time[0] = time.time()
            status_label.config(text="🔴 Recording from Microphone + Speaker...", foreground="red")
            duration_label.config(foreground="red")
            start_btn.config(state=tk.DISABLED)
            stop_btn.config(state=tk.NORMAL)

            logger.info("Started simultaneous recording (mic + speaker)")

            # Start recording in background thread
            threading.Thread(
                target=self._record_audio_simultaneous,
                args=(recording_active, status_label, duration_label),
                daemon=True
            ).start()

            # Start duration update
            update_duration()

        def stop_record():
            recording_active[0] = False
            status_label.config(text="⏹️ Stopping recording...", foreground="orange")
            start_btn.config(state=tk.NORMAL)
            stop_btn.config(state=tk.DISABLED)

        start_btn = ttk.Button(
            button_frame,
            text="🔴 Start Recording",
            command=start_record,
            width=20
        )
        start_btn.pack(side=tk.LEFT, padx=5)

        stop_btn = ttk.Button(
            button_frame,
            text="⏹️ Stop Recording",
            command=stop_record,
            state=tk.DISABLED,
            width=20
        )
        stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # Help text
        help_frame = ttk.Frame(dialog)
        help_frame.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(
            help_frame,
            text="💡 Tip: Perfect for recording video calls, meetings, or any scenario\nwhere you need both your voice and system audio captured.",
            font=("Arial", 8),
            foreground="gray",
            justify=tk.LEFT
        ).pack()

        ttk.Label(
            help_frame,
            text="⚠️ Note: Recording will be saved and automatically loaded for transcription.",
            font=("Arial", 8),
            foreground="orange",
            justify=tk.LEFT
        ).pack(pady=(5, 0))

    def _record_audio_simultaneous(self, recording_active: list, status_label, duration_label):
        """Record both microphone and speaker audio simultaneously."""
        try:
            import sounddevice as sd
            import numpy as np
            from scipy.io import wavfile

            sample_rate = 16000  # Whisper's preferred sample rate

            logger.info("Starting simultaneous recording (microphone + speaker)")
            logger.info(f"Sample rate: {sample_rate}Hz")

            # Query available devices
            devices = sd.query_devices()
            logger.info("Available audio devices:")
            for idx, device in enumerate(devices):
                logger.info(f"  [{idx}] {device['name']} - "
                           f"In:{device['max_input_channels']} Out:{device['max_output_channels']}")

            # Storage for both streams
            mic_chunks = []
            speaker_chunks = []

            # Find microphone device (default or first available input device)
            mic_device = None

            try:
                default_input = sd.default.device[0]
                if default_input is not None and default_input >= 0:
                    # Verify the default device has input channels
                    if devices[default_input]['max_input_channels'] > 0:
                        mic_device = default_input
                        logger.info(f"Using default microphone: {devices[default_input]['name']} (index {default_input})")
            except Exception as e:
                logger.warning(f"Could not get default device: {e}")

            # If no valid default, find first available input device
            if mic_device is None:
                logger.info("No valid default microphone, searching for available input devices...")
                for idx, device in enumerate(devices):
                    if device['max_input_channels'] > 0:
                        # Skip loopback devices for microphone
                        device_name_lower = device['name'].lower()
                        if not any(keyword in device_name_lower for keyword in
                                 ['stereo mix', 'loopback', 'monitor', 'what u hear', 'wave out', 'blackhole']):
                            mic_device = idx
                            logger.info(f"Using microphone: {device['name']} (index {idx})")
                            break

            if mic_device is None:
                error_msg = "No microphone device found! Please check your audio device connections."
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Try to find loopback/stereo mix device for system audio
            loopback_device = None

            # Look for loopback devices (Windows: Stereo Mix, Linux: Monitor, Mac: varies)
            for idx, device in enumerate(devices):
                if idx == mic_device:  # Skip the mic device
                    continue

                device_name_lower = device['name'].lower()
                if any(keyword in device_name_lower for keyword in
                       ['stereo mix', 'loopback', 'monitor', 'what u hear', 'wave out', 'blackhole']):
                    if device['max_input_channels'] > 0:
                        loopback_device = idx
                        logger.info(f"Found loopback device: {device['name']} (index {idx})")
                        break

            if loopback_device is None:
                logger.warning("No loopback device found for system audio capture")
                logger.warning("Will record microphone only")
                logger.warning("To enable system audio:")
                logger.warning("  Windows: Enable 'Stereo Mix' in Sound Settings")
                logger.warning("  Linux: Use PulseAudio monitor")
                logger.warning("  macOS: May require BlackHole or similar virtual audio device")

            # Callback for microphone
            def mic_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Mic status: {status}")
                mic_chunks.append(indata.copy())

            # Callback for speaker (if available)
            def speaker_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Speaker status: {status}")
                speaker_chunks.append(indata.copy())

            # Start recording from both sources
            mic_stream = None
            speaker_stream = None

            try:
                # Open microphone stream
                logger.info(f"Opening microphone stream (device {mic_device})")
                mic_stream = sd.InputStream(
                    device=mic_device,
                    samplerate=sample_rate,
                    channels=1,
                    callback=mic_callback
                )
                mic_stream.start()
                logger.info("✓ Microphone recording started")

                # Open speaker stream if loopback device available
                if loopback_device is not None:
                    logger.info(f"Opening speaker stream (device {loopback_device})")
                    try:
                        speaker_stream = sd.InputStream(
                            device=loopback_device,
                            samplerate=sample_rate,
                            channels=1,
                            callback=speaker_callback
                        )
                        speaker_stream.start()
                        logger.info("✓ Speaker recording started")
                    except Exception as e:
                        logger.error(f"Could not start speaker recording: {e}")
                        speaker_stream = None

                # Record while active
                while recording_active[0]:
                    sd.sleep(100)

            finally:
                # Stop streams
                if mic_stream:
                    mic_stream.stop()
                    mic_stream.close()
                    logger.info("Microphone recording stopped")

                if speaker_stream:
                    speaker_stream.stop()
                    speaker_stream.close()
                    logger.info("Speaker recording stopped")

            # Process and combine recordings
            if mic_chunks or speaker_chunks:
                # Convert chunks to arrays
                mic_data = None
                speaker_data = None

                if mic_chunks:
                    mic_data = np.concatenate(mic_chunks, axis=0)
                    logger.info(f"Microphone: {len(mic_data)} samples")

                if speaker_chunks:
                    speaker_data = np.concatenate(speaker_chunks, axis=0)
                    logger.info(f"Speaker: {len(speaker_data)} samples")

                # Mix both sources
                if mic_data is not None and speaker_data is not None:
                    # Ensure same length (pad shorter one with zeros)
                    max_len = max(len(mic_data), len(speaker_data))

                    if len(mic_data) < max_len:
                        mic_data = np.pad(mic_data, ((0, max_len - len(mic_data)), (0, 0)))
                    if len(speaker_data) < max_len:
                        speaker_data = np.pad(speaker_data, ((0, max_len - len(speaker_data)), (0, 0)))

                    # Mix: 50% mic + 50% speaker (you can adjust these ratios)
                    mixed_data = (mic_data * 0.6 + speaker_data * 0.4)

                    # Normalize to prevent clipping
                    max_val = np.max(np.abs(mixed_data))
                    if max_val > 0:
                        mixed_data = mixed_data / max_val * 0.9

                    logger.info("✓ Mixed microphone and speaker audio")
                    final_data = mixed_data

                elif mic_data is not None:
                    logger.info("Using microphone audio only")
                    final_data = mic_data
                elif speaker_data is not None:
                    logger.info("Using speaker audio only")
                    final_data = speaker_data
                else:
                    raise ValueError("No audio data recorded")

                # Save to temporary file
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                self.recorded_audio_path = temp_file.name
                temp_file.close()

                # Convert to int16 for WAV file
                final_data_int16 = (final_data * 32767).astype(np.int16)
                wavfile.write(self.recorded_audio_path, sample_rate, final_data_int16)

                duration_seconds = len(final_data) / sample_rate
                logger.info(f"Recording saved to: {self.recorded_audio_path}")
                logger.info(f"Duration: {duration_seconds:.1f} seconds")

                # Update UI
                success_msg = f"✅ Recording complete! ({duration_seconds:.1f}s)"
                if speaker_chunks:
                    success_msg += "\n🎤 Mic + 🔊 Speaker mixed"
                else:
                    success_msg += "\n🎤 Mic only (no system audio detected)"

                self.root.after(0, lambda: self.load_file(self.recorded_audio_path))
                self.root.after(0, lambda: status_label.config(
                    text=success_msg,
                    foreground="green"
                ))
                self.root.after(0, lambda: duration_label.config(
                    text=f"✓ Saved: {duration_seconds:.1f}s",
                    foreground="green"
                ))
            else:
                self.root.after(0, lambda: status_label.config(
                    text="❌ No audio recorded",
                    foreground="red"
                ))

        except Exception as e:
            error_msg = f"Recording error: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Format user-friendly error message
            if "device" in str(e).lower():
                user_msg = "❌ Audio device error. Please check:\n1. Microphone is connected\n2. Audio drivers are installed\n3. Permissions are granted"
            elif "no microphone" in str(e).lower():
                user_msg = "❌ No microphone found. Please connect a microphone and try again."
            else:
                user_msg = f"❌ Recording error: {str(e)}"

            self.root.after(0, lambda: status_label.config(text=user_msg, foreground="red"))
            self.root.after(0, lambda: duration_label.config(text="❌ Failed", foreground="red"))

    def _record_audio(self, source: str, recording_active: list, status_label):
        """Record audio in background thread (legacy method for backward compatibility)."""
        try:
            import sounddevice as sd
            import numpy as np
            from scipy.io import wavfile

            sample_rate = 16000  # Whisper's preferred sample rate
            channels = 1  # Mono

            logger.info(f"Recording started: {source}, {sample_rate}Hz, {channels} channel(s)")

            # Record in chunks
            recording_chunks = []

            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Recording status: {status}")
                recording_chunks.append(indata.copy())

            with sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback):
                while recording_active[0]:
                    sd.sleep(100)

            # Combine chunks
            if recording_chunks:
                recording_data = np.concatenate(recording_chunks, axis=0)

                # Save to temporary file
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                self.recorded_audio_path = temp_file.name
                temp_file.close()

                wavfile.write(self.recorded_audio_path, sample_rate, recording_data)

                logger.info(f"Recording saved to: {self.recorded_audio_path}")

                # Update UI
                self.root.after(0, lambda: self.load_file(self.recorded_audio_path))
                self.root.after(0, lambda: status_label.config(
                    text=f"✅ Recording complete! ({len(recording_data) / sample_rate:.1f}s)",
                    foreground="green"
                ))
            else:
                self.root.after(0, lambda: status_label.config(
                    text="No audio recorded",
                    foreground="red"
                ))

        except Exception as e:
            error_msg = f"Recording error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.root.after(0, lambda: status_label.config(text=error_msg, foreground="red"))

    def show_audio_settings(self):
        """Show audio device settings."""
        try:
            import sounddevice as sd

            devices = sd.query_devices()

            dialog = tk.Toplevel(self.root)
            dialog.title("Audio Devices")
            dialog.geometry("600x400")
            dialog.transient(self.root)

            ttk.Label(
                dialog,
                text="Available Audio Devices",
                font=("Arial", 12, "bold")
            ).pack(pady=10)

            text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=70, height=20)
            text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            for idx, device in enumerate(devices):
                text.insert(tk.END, f"[{idx}] {device['name']}\n")
                text.insert(tk.END, f"    Max Input Channels: {device['max_input_channels']}\n")
                text.insert(tk.END, f"    Max Output Channels: {device['max_output_channels']}\n")
                text.insert(tk.END, f"    Default Sample Rate: {device['default_samplerate']}Hz\n\n")

            text.config(state=tk.DISABLED)

            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Could not query audio devices: {e}")

    def start_transcription(self):
        """Start the transcription process."""
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video or audio file first.")
            return

        if self.is_transcribing:
            messagebox.showwarning("Warning", "Transcription is already in progress.")
            return

        # Disable controls
        if self.current_mode == "basic":
            self.basic_transcribe_btn.config(state=tk.DISABLED)
        else:
            self.adv_start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

        self.save_button.config(state=tk.DISABLED)
        self.is_transcribing = True

        # Clear previous results
        self.text_area.delete(1.0, tk.END)
        self.transcription_result = None

        # Reset progress bar
        self.progress_bar['value'] = 0
        self.progress_percent_var.set("")

        # Reset model upgrade attempts
        self.model_upgrade_attempts = 0

        # Start transcription in background thread
        self.transcription_thread = threading.Thread(
            target=self._transcription_worker,
            daemon=True
        )
        self.transcription_thread.start()

    def _transcription_worker(self):
        """Worker thread for transcription process with automatic model selection."""
        start_time = time.time()
        timing_data = {
            'extraction_start': None,
            'extraction_end': None,
            'loading_start': None,
            'loading_end': None,
            'transcription_start': None,
            'transcription_end': None,
            'total_end': None
        }

        try:
            # Step 1: Extract/prepare audio
            file_type = "audio" if self.audio_extractor.is_audio_file(self.video_path) else "video"
            action = "Converting audio" if file_type == "audio" else "Extracting audio from video"
            self.update_progress(f"{action}...", 5)
            timing_data['extraction_start'] = time.time()
            self.audio_path = self.audio_extractor.extract_audio(self.video_path)
            timing_data['extraction_end'] = time.time()
            extraction_time = timing_data['extraction_end'] - timing_data['extraction_start']
            action_completed = "conversion" if file_type == "audio" else "extraction"
            logger.info(f"Audio {action_completed} completed in {extraction_time:.2f} seconds")
            self.update_progress(f"Audio {action_completed} completed", 15)

            # Step 2: Determine model to use
            if self.current_mode == "basic" or self.auto_model_enabled:
                # Auto model selection
                result = self._auto_transcribe(timing_data)
            else:
                # Manual model selection
                result = self._manual_transcribe(timing_data)

            if result:
                self.transcription_result = result

                # Calculate total time
                timing_data['total_end'] = time.time()
                total_time = timing_data['total_end'] - start_time

                # Display results
                self.update_progress("Finalizing...", 100)
                self.root.after(0, lambda: self._display_transcription(total_time))

        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, self._transcription_finished)
        finally:
            # Cleanup temporary audio file
            if self.audio_path and os.path.exists(self.audio_path):
                try:
                    self.audio_extractor.cleanup_temp_file(self.audio_path)
                except:
                    pass

    def _auto_transcribe(self, timing_data: dict):
        """Automatic model selection with quality checking."""
        models_to_try = ['tiny', 'base', 'small']
        quality_threshold = 0.7  # Confidence threshold

        result = None

        for model_size in models_to_try:
            logger.info(f"Trying model: {model_size}")
            self.update_progress(f"Loading {model_size} model...", 20)

            timing_data['loading_start'] = time.time()
            self.transcriber = Transcriber(model_size=model_size)
            self.transcriber.load_model()
            timing_data['loading_end'] = time.time()

            self.update_progress(f"Transcribing with {model_size} model...", 30)
            timing_data['transcription_start'] = time.time()

            # Get instructions if in advanced mode
            instructions = None
            if self.current_mode == "advanced":
                instructions = self.instructions_text.get(1.0, tk.END).strip()
                example_text = "Example: Meeting between John (CEO) and Sarah (CTO) about Q4 project roadmap."
                if instructions == example_text or not instructions:
                    instructions = None

            # Get language
            selected_language_code = None
            if self.current_mode == "advanced":
                selected_language_name = self.language_var.get()
                selected_language_code = self.languages.get(selected_language_name, None)

            result = self.transcriber.transcribe(
                self.audio_path,
                language=selected_language_code,
                initial_prompt=instructions
            )

            timing_data['transcription_end'] = time.time()

            # Check quality
            avg_confidence = self._calculate_confidence(result)
            logger.info(f"Model {model_size} confidence: {avg_confidence:.2f}")

            if avg_confidence >= quality_threshold or model_size == 'small':
                logger.info(f"Using model {model_size} (confidence: {avg_confidence:.2f})")
                break
            else:
                logger.info(f"Quality insufficient ({avg_confidence:.2f} < {quality_threshold}), upgrading model...")
                self.update_progress(f"Upgrading to better model for quality...", 25)

        return result

    def _manual_transcribe(self, timing_data: dict):
        """Manual model selection."""
        model_size = self.model_var.get()

        self.update_progress(f"Loading {model_size} model...", 20)
        timing_data['loading_start'] = time.time()

        if self.transcriber is None or self.transcriber.model_size != model_size:
            self.transcriber = Transcriber(model_size=model_size)
            self.transcriber.load_model()

        timing_data['loading_end'] = time.time()

        self.update_progress("Transcribing...", 30)
        timing_data['transcription_start'] = time.time()

        # Get instructions
        instructions = self.instructions_text.get(1.0, tk.END).strip()
        example_text = "Example: Meeting between John (CEO) and Sarah (CTO) about Q4 project roadmap."
        if instructions == example_text or not instructions:
            instructions = None

        # Get language
        selected_language_name = self.language_var.get()
        selected_language_code = self.languages.get(selected_language_name, None)

        result = self.transcriber.transcribe(
            self.audio_path,
            language=selected_language_code,
            initial_prompt=instructions
        )

        timing_data['transcription_end'] = time.time()

        return result

    def _calculate_confidence(self, result: dict) -> float:
        """Calculate average confidence from transcription segments."""
        segments = result.get('segments', [])
        if not segments:
            return 0.0

        # Whisper doesn't provide confidence directly, but we can use
        # the no_speech_prob as an inverse indicator
        total_confidence = 0.0
        count = 0

        for segment in segments:
            # no_speech_prob: higher = more likely to be silence
            # Convert to confidence: 1 - no_speech_prob
            no_speech = segment.get('no_speech_prob', 0.0)
            confidence = 1.0 - no_speech
            total_confidence += confidence
            count += 1

        return total_confidence / count if count > 0 else 0.0

    def _display_transcription(self, total_time=None):
        """Display transcription results."""
        if self.transcription_result:
            text = self.transcription_result.get('text', '')
            detected_language = self.transcription_result.get('language', 'unknown')

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, text)
            self.save_button.config(state=tk.NORMAL)

            # Get language name
            language_name = "Unknown"
            if detected_language != 'unknown':
                for name, code in self.languages.items():
                    if code == detected_language:
                        language_name = name
                        break

            logger.info(f"Detected language: {language_name}")

            # Display completion message
            if total_time:
                time_str = Transcriber._format_estimated_time(total_time)
                model_used = self.transcriber.model_size if self.transcriber else "unknown"

                messagebox.showinfo(
                    "Transcription Complete",
                    f"Transcription completed successfully!\n\n"
                    f"Model used: {model_used}\n"
                    f"Total time: {time_str}\n"
                    f"Detected language: {language_name}\n\n"
                    f"You can now save the transcription."
                )

                self.status_var.set(f"Completed in {time_str} | Model: {model_used} | Language: {language_name}")

        self._transcription_finished()

    def _transcription_finished(self):
        """Reset UI after transcription completes."""
        self.is_transcribing = False

        if self.current_mode == "basic":
            self.basic_transcribe_btn.config(state=tk.NORMAL)
        else:
            self.adv_start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

        self.progress_bar['value'] = 0
        self.progress_percent_var.set("")
        self.progress_var.set("Ready")

    def stop_transcription(self):
        """Stop the transcription process."""
        if not self.is_transcribing:
            return

        self.is_transcribing = False
        self.update_progress("Stopping transcription...")
        messagebox.showinfo("Info", "Transcription will stop after current operation completes.")
        self._transcription_finished()

    def update_progress(self, message, percent=None):
        """Update progress bar and label."""
        msg = str(message)
        pct = float(percent) if percent is not None else None

        def update_all():
            try:
                self.progress_var.set(msg)
                self.status_var.set(msg)
                if pct is not None:
                    self._update_progress_bar(pct)
            except Exception as e:
                logger.error(f"Error in update_all: {e}", exc_info=True)

        self.root.after(0, update_all)

        if percent is not None:
            logger.info(f"{message} ({percent:.1f}%)")
        else:
            logger.info(message)

    def _update_progress_bar(self, percent):
        """Update progress bar value."""
        try:
            percent_val = min(100, max(0, float(percent)))
            self.progress_bar.configure(value=percent_val)
            self.progress_percent_var.set(f"{int(percent_val)}%")
            self.progress_bar.update()
        except Exception as e:
            logger.error(f"Error updating progress bar: {e}", exc_info=True)

    def save_transcription(self):
        """Save transcription to file."""
        if not self.transcription_result:
            messagebox.showwarning("Warning", "No transcription to save.")
            return

        output_format = self.format_var.get()
        default_ext = f'.{output_format}'
        default_name = Path(self.video_path).stem + default_ext

        file_types = [
            ("Text files", "*.txt"),
            ("SRT files", "*.srt"),
            ("VTT files", "*.vtt"),
            ("All files", "*.*")
        ]

        file_path = filedialog.asksaveasfilename(
            title="Save Transcription",
            defaultextension=default_ext,
            filetypes=file_types,
            initialfile=default_name
        )

        if file_path:
            try:
                if output_format == 'srt':
                    content = self.transcriber.format_as_srt(self.transcription_result)
                elif output_format == 'vtt':
                    content = self._format_as_vtt(self.transcription_result)
                else:
                    content = self.transcription_result.get('text', '')

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                messagebox.showinfo(
                    "Success",
                    f"Transcription saved successfully!\n\nFile: {file_path}"
                )
                self.status_var.set(f"Saved to: {Path(file_path).name}")
                logger.info(f"Transcription saved to: {file_path}")

                # Open file location
                try:
                    import subprocess
                    import platform
                    if platform.system() == "Windows":
                        subprocess.Popen(f'explorer /select,"{file_path}"')
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.Popen(["open", "-R", file_path])
                    else:  # Linux
                        subprocess.Popen(["xdg-open", os.path.dirname(file_path)])
                except:
                    pass

            except Exception as e:
                error_msg = f"Failed to save file: {str(e)}"
                messagebox.showerror("Error", error_msg)
                logger.error(error_msg, exc_info=True)

    def _format_as_vtt(self, transcription_result: dict) -> str:
        """Format transcription as VTT subtitle file."""
        segments = transcription_result.get('segments', [])
        vtt_content = ["WEBVTT\n"]

        for i, segment in enumerate(segments, start=1):
            start_time = self._format_vtt_timestamp(segment['start'])
            end_time = self._format_vtt_timestamp(segment['end'])
            text = segment['text'].strip()

            vtt_content.append(f"{start_time} --> {end_time}\n{text}\n")

        return "\n".join(vtt_content)

    def _format_vtt_timestamp(self, seconds: float) -> str:
        """Format seconds as VTT timestamp (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


class GUILogHandler(logging.Handler):
    """Custom logging handler for GUI status bar."""

    def __init__(self, app):
        super().__init__()
        self.app = app

    def emit(self, record):
        """Emit a log record to the GUI."""
        try:
            msg = self.format(record)
            if record.levelno >= logging.WARNING:
                self.app.root.after(0, lambda: self.app.status_var.set(msg[:100]))
        except:
            pass
