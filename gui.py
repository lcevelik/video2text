"""
GUI Module

This module provides the graphical user interface for the video transcription application.
Built with Tkinter for cross-platform compatibility.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from pathlib import Path
import os
import time

from audio_extractor import AudioExtractor
from transcriber import Transcriber

logger = logging.getLogger(__name__)


class TranscriptionApp:
    """Main GUI application for video transcription."""
    
    def __init__(self, root):
        """
        Initialize the GUI application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Video/Audio to Text - Whisper Transcription")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
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
        
        # Initialize components
        self.audio_extractor = AudioExtractor()
        self.transcriber = None
        
        # Setup logging to GUI
        self.setup_logging()
        
        # Build UI
        self.build_ui()
        
        # Initialize model description
        self.on_model_change()
        
        # Center window
        self.center_window()
    
    def setup_logging(self):
        """Setup logging handler to display logs in GUI."""
        self.log_handler = GUILogHandler(self)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        """Build the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Video to Text Transcription",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Media File (Video or Audio)", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Selected File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(
            file_frame,
            text="Browse...",
            command=self.browse_file
        ).grid(row=0, column=2, padx=5)
        
        # Model selection
        model_frame = ttk.LabelFrame(main_frame, text="Whisper Model", padding="10")
        model_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(model_frame, text="Model Size:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=Transcriber.MODEL_SIZES,
            state="readonly",
            width=15
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        model_combo.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # Model info label
        self.model_info_label = ttk.Label(
            model_frame,
            text="(base: balanced speed/accuracy)",
            foreground="gray",
            font=("Arial", 8)
        )
        self.model_info_label.grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Model help button
        help_button = ttk.Button(
            model_frame,
            text="?",
            width=3,
            command=self.show_model_help
        )
        help_button.grid(row=0, column=3, padx=5)
        
        # Language selection
        language_frame = ttk.LabelFrame(main_frame, text="Language", padding="10")
        language_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(language_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        # Common languages supported by Whisper (99 total, showing most common)
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
            text="(Auto-detect recommended for multilingual content)",
            foreground="gray",
            font=("Arial", 8)
        ).grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Output format
        format_frame = ttk.LabelFrame(main_frame, text="Output Format", padding="10")
        format_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
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
        
        # Instructions/Prompt field for speaker recognition
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions for Transcription (Optional)", padding="10")
        instructions_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
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
            height=4,
            font=("Arial", 9)
        )
        self.instructions_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Add example text as placeholder
        example_text = "Example: This is a conversation between multiple speakers. Speaker 1: John, Speaker 2: Sarah. The topic is about project management."
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
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(
            control_frame,
            text="Start Transcription",
            command=self.start_transcription,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            control_frame,
            text="Stop",
            command=self.stop_transcription,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Make save button more prominent
        self.save_button = ttk.Button(
            control_frame,
            text="[DOWNLOAD] Save Transcription",
            command=self.save_transcription,
            state=tk.DISABLED
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
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
        text_frame = ttk.LabelFrame(main_frame, text="Transcription", padding="10")
        text_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Consolas", 10)
        )
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def on_model_change(self, event=None):
        """Handle model selection change."""
        model_size = self.model_var.get()
        model_desc = Transcriber.get_model_description(model_size)
        self.model_info_label.config(text=f"({model_size}: {model_desc['description']})")
    
    def show_model_help(self):
        """Show detailed model information in a popup window."""
        model_size = self.model_var.get()
        model_desc = Transcriber.get_model_description(model_size)
        
        # Check if GPU is available
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
"""
        
        messagebox.showinfo(f"Model Information: {model_size.upper()}", help_text)
    
    def browse_file(self):
        """Open file browser to select video or audio file."""
        from audio_extractor import AudioExtractor
        
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
            self.video_path = file_path  # Keep variable name for backward compatibility
            file_name = Path(file_path).name
            self.file_label.config(text=file_name, foreground="black")
            self.start_button.config(state=tk.NORMAL)
            
            # Determine file type
            file_type = "audio" if self.audio_extractor.is_audio_file(file_path) else "video"
            self.status_var.set(f"{file_type.capitalize()} file selected: {file_name}")
            logger.info(f"Selected {file_type} file: {file_path}")
            
            # Get media duration (works for both video and audio)
            try:
                self.video_duration = self.audio_extractor.get_media_duration(file_path)
                if self.video_duration:
                    duration_str = Transcriber._format_estimated_time(self.video_duration)
                    self.status_var.set(f"{file_type.capitalize()} file selected: {file_name} ({duration_str})")
                else:
                    self.status_var.set(f"{file_type.capitalize()} file selected: {file_name} (duration unknown)")
            except Exception as e:
                logger.warning(f"Could not get {file_type} duration: {e}")
                self.video_duration = None
    
    def start_transcription(self):
        """Start the transcription process in a separate thread."""
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video or audio file first.")
            return
        
        if self.is_transcribing:
            messagebox.showwarning("Warning", "Transcription is already in progress.")
            return
        
        # Disable controls
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        self.is_transcribing = True
        
        # Clear previous results
        self.text_area.delete(1.0, tk.END)
        self.transcription_result = None
        
        # Reset progress bar
        self.progress_bar['value'] = 0
        self.progress_percent_var.set("")
        
        # Start transcription in background thread
        self.transcription_thread = threading.Thread(
            target=self._transcription_worker,
            daemon=True
        )
        self.transcription_thread.start()
    
    def _transcription_worker(self):
        """Worker thread for transcription process."""
        # Timing tracking
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
            
            # Step 2: Initialize transcriber with selected model
            model_size = self.model_var.get()
            model_loaded = False
            if self.transcriber is None or self.transcriber.model_size != model_size:
                self.update_progress(f"Loading Whisper model '{model_size}'...", 20)
                timing_data['loading_start'] = time.time()
                self.transcriber = Transcriber(model_size=model_size)
                
                # Progress callback for model loading
                def model_loading_progress(msg):
                    self.update_progress(msg, 25)
                
                self.transcriber.load_model(progress_callback=model_loading_progress)
                timing_data['loading_end'] = time.time()
                loading_time = timing_data['loading_end'] - timing_data['loading_start']
                logger.info(f"Model loading completed in {loading_time:.2f} seconds")
                self.update_progress("Model loaded successfully", 30)
            else:
                model_loaded = True
                logger.info("Model already loaded, skipping load step")
                self.update_progress("Model already loaded", 30)
            
            # Step 3: Get instructions/prompt
            instructions = self.instructions_text.get(1.0, tk.END).strip()
            example_text = "Example: This is a conversation between multiple speakers. Speaker 1: John, Speaker 2: Sarah. The topic is about project management."
            if instructions == example_text or not instructions:
                instructions = None  # Don't use placeholder text
            
            # Step 4: Transcribe
            self.update_progress("Transcribing audio...", 35)
            timing_data['transcription_start'] = time.time()
            
            # Start progress update thread
            transcription_start = time.time()
            progress_stop_event = threading.Event()
            
            def update_progress_thread():
                """Background thread to update progress bar during transcription."""
                # Calculate estimated transcription time based on video duration and model performance
                # This is used internally for progress calculation, not displayed to user
                import torch
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                
                # Get real-time factor for the model and device
                realtime_factor = Transcriber.SPEED_FACTORS.get(model_size, {}).get(device, 10.0)
                
                # Estimate transcription time based on video duration
                # This scales with video length: short videos = fast progress, long videos = slow progress
                if self.video_duration and self.video_duration > 0 and realtime_factor > 0:
                    estimated_transcription_time = self.video_duration / realtime_factor
                else:
                    # Fallback: use a reasonable default (assume 5 minutes for unknown duration)
                    estimated_transcription_time = 300
                
                base_progress = 35
                max_progress = 95
                progress_range = max_progress - base_progress
                
                # Update progress every 0.3 seconds for smooth updates
                while not progress_stop_event.is_set():
                    elapsed = time.time() - transcription_start
                    
                    # Calculate progress based on elapsed time vs estimated time
                    # Progress from 35% to 95% during transcription phase
                    if estimated_transcription_time > 0:
                        # Use a smooth curve: progress = 35 + 60 * (elapsed / est_time)
                        # Cap at 95% until transcription actually completes
                        progress_ratio = min(1.0, elapsed / estimated_transcription_time)
                        progress = base_progress + (progress_range * progress_ratio)
                    else:
                        # Fallback: slow linear progress
                        progress = base_progress + min(progress_range, (elapsed / 300) * progress_range)
                    
                    logger.debug(f"Progress update: elapsed={elapsed:.1f}s, est_time={estimated_transcription_time:.1f}s, progress={progress:.1f}%")
                    self.update_progress("Transcribing audio...", progress)
                    
                    # Wait 0.3 seconds before next update
                    if progress_stop_event.wait(0.3):
                        break  # Stop if event is set
            
            # Start progress update thread
            progress_thread = threading.Thread(target=update_progress_thread, daemon=True)
            progress_thread.start()
            
            # Get selected language
            selected_language_name = self.language_var.get()
            selected_language_code = self.languages.get(selected_language_name, None)
            
            if selected_language_code:
                logger.info(f"Transcribing with language: {selected_language_name} ({selected_language_code})")
            else:
                logger.info("Transcribing with auto language detection")
            
            try:
                self.transcription_result = self.transcriber.transcribe(
                    self.audio_path,
                    language=selected_language_code,  # Pass selected language (None = auto-detect)
                    initial_prompt=instructions,
                    progress_callback=None  # Don't use callback, use thread instead
                )
            finally:
                # Stop progress thread
                progress_stop_event.set()
            timing_data['transcription_end'] = time.time()
            transcription_time = timing_data['transcription_end'] - timing_data['transcription_start']
            logger.info(f"Transcription completed in {transcription_time:.2f} seconds")
            self.update_progress("Transcription completed!", 95)
            
            # Calculate total time
            timing_data['total_end'] = time.time()
            total_time = timing_data['total_end'] - start_time
            
            # Get device info
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            device_name = f"GPU ({torch.cuda.get_device_name(0)})" if device == 'cuda' else "CPU"
            
            # Log detailed timing information
            file_type = "audio" if self.audio_extractor.is_audio_file(self.video_path) else "video"
            logger.info("="*60)
            logger.info("TRANSCRIPTION TIMING SUMMARY")
            logger.info("="*60)
            logger.info(f"{file_type.capitalize()} duration: {self.video_duration:.2f} seconds ({self.video_duration/60:.2f} minutes)" if self.video_duration else f"{file_type.capitalize()} duration: Unknown")
            logger.info(f"Model: {model_size}")
            logger.info(f"Device: {device_name}")
            logger.info(f"Model already loaded: {model_loaded}")
            logger.info("-"*60)
            logger.info(f"Audio extraction: {extraction_time:.2f} seconds")
            if timing_data['loading_start']:
                logger.info(f"Model loading: {loading_time:.2f} seconds")
            else:
                logger.info(f"Model loading: 0.00 seconds (already loaded)")
            logger.info(f"Transcription: {transcription_time:.2f} seconds")
            logger.info("-"*60)
            logger.info(f"TOTAL TIME: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
            
            # Calculate real-time factor
            if self.video_duration and self.video_duration > 0:
                realtime_factor = self.video_duration / transcription_time if transcription_time > 0 else 0
                logger.info(f"Real-time factor: {realtime_factor:.2f}x (processed {realtime_factor:.2f}x faster than real-time)")
            logger.info("="*60)
            
            # Store timing data for display
            self.timing_data = timing_data
            self.total_time = total_time
            self.transcription_time = transcription_time
            
            # Step 5: Display results
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
    
    def _display_transcription(self, total_time=None):
        """Display transcription results in the text area."""
        if self.transcription_result:
            text = self.transcription_result.get('text', '')
            detected_language = self.transcription_result.get('language', 'unknown')
            
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, text)
            self.save_button.config(state=tk.NORMAL)
            
            # Log detected language
            if detected_language != 'unknown':
                logger.info(f"Detected language: {detected_language}")
                # Find language name from code
                language_name = "Unknown"
                for name, code in self.languages.items():
                    if code == detected_language:
                        language_name = name
                        break
                logger.info(f"Detected language name: {language_name}")
            
            # Get language name for display
            language_name = "Unknown"
            if detected_language != 'unknown':
                for name, code in self.languages.items():
                    if code == detected_language:
                        language_name = name
                        break
            
            # Display timing information
            if total_time:
                time_str = Transcriber._format_estimated_time(total_time)
                
                # Build language info string
                language_info = f" | Language: {language_name}" if detected_language != 'unknown' else ""
                
                if self.video_duration and self.transcription_time:
                    realtime_factor = self.video_duration / self.transcription_time
                    status_msg = f"Completed in {time_str} | Speed: {realtime_factor:.1f}x real-time{language_info} | Check log for details"
                    # Also show a brief info message
                    messagebox.showinfo(
                        "Transcription Complete",
                        f"Transcription completed successfully!\n\n"
                        f"Total time: {time_str}\n"
                        f"Processing speed: {realtime_factor:.1f}x real-time\n"
                        f"Detected language: {language_name}\n\n"
                        f"Detailed timing information has been logged.\n"
                        f"Check 'transcription.log' for full analysis."
                    )
                else:
                    status_msg = f"Completed in {time_str}{language_info} | Check log for details"
                self.status_var.set(status_msg)
            else:
                language_info = f" | Language: {language_name}" if detected_language != 'unknown' else ""
                self.status_var.set(f"Transcription completed successfully{language_info}")
        
        self._transcription_finished()
    
    def _transcription_finished(self):
        """Reset UI after transcription completes."""
        self.is_transcribing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_percent_var.set("")
        self.progress_var.set("Ready")
    
    def stop_transcription(self):
        """Stop the transcription process."""
        if not self.is_transcribing:
            return
        
        # Note: Whisper doesn't have a built-in stop mechanism
        # This will just mark as stopped and wait for current operation
        self.is_transcribing = False
        self.update_progress("Stopping transcription...")
        messagebox.showinfo("Info", "Transcription will stop after current operation completes.")
        self._transcription_finished()
    
    def update_progress(self, message, percent=None):
        """Update progress bar and label."""
        # Use after() to safely update GUI from background thread
        # Capture values in local variables to avoid closure issues
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
            logger.info(f"{message} (percent: {percent:.1f}%)")
        else:
            logger.info(message)
    
    def _update_progress_bar(self, percent):
        """Update progress bar value and percentage label."""
        try:
            percent_val = min(100, max(0, float(percent)))
            # Update progress bar value - use configure method which is more reliable
            self.progress_bar.configure(value=percent_val)
            # Update percentage label
            self.progress_percent_var.set(f"{int(percent_val)}%")
            # Force immediate GUI update - use update() for immediate redraw
            self.progress_bar.update()
            logger.info(f"Progress bar updated to {int(percent_val)}%")
        except Exception as e:
            logger.error(f"Error updating progress bar: {e}", exc_info=True)
    
    def save_transcription(self):
        """Save transcription to file."""
        if not self.transcription_result:
            messagebox.showwarning("Warning", "No transcription to save.")
            return
        
        output_format = self.format_var.get()
        default_ext = '.txt' if output_format == 'txt' else '.srt'
        default_name = Path(self.video_path).stem + default_ext
        
        file_path = filedialog.asksaveasfilename(
            title="Save Transcription",
            defaultextension=default_ext,
            filetypes=[
                ("Text files", "*.txt"),
                ("SRT files", "*.srt"),
                ("All files", "*.*")
            ],
            initialfile=default_name
        )
        
        if file_path:
            try:
                if output_format == 'srt':
                    content = self.transcriber.format_as_srt(self.transcription_result)
                else:
                    content = self.transcription_result.get('text', '')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo(
                    "Success", 
                    f"Transcription saved successfully!\n\nFile: {file_path}\n\nYou can now find and download the file from this location."
                )
                self.status_var.set(f"Saved to: {Path(file_path).name} - Ready to download")
                logger.info(f"Transcription saved to: {file_path}")
                
                # Optionally open the file location in file explorer
                try:
                    import subprocess
                    import platform
                    if platform.system() == "Windows":
                        subprocess.Popen(f'explorer /select,"{file_path}"')
                except:
                    pass  # Silently fail if we can't open explorer
                
            except Exception as e:
                error_msg = f"Failed to save file: {str(e)}"
                messagebox.showerror("Error", error_msg)
                logger.error(error_msg, exc_info=True)


class GUILogHandler(logging.Handler):
    """Custom logging handler that displays logs in the GUI status bar."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
    
    def emit(self, record):
        """Emit a log record to the GUI."""
        try:
            msg = self.format(record)
            # Only show important messages in status bar
            if record.levelno >= logging.WARNING:
                self.app.root.after(0, lambda: self.app.status_var.set(msg[:100]))
        except:
            pass

