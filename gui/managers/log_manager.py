"""
Log Manager for FonixFlow

Centralized logging system that:
- Saves logs to user's home directory (~/.fonixflow/logs/)
- Works in both development and installed/bundled modes
- Provides log rotation to prevent huge files
- Allows users to easily find and share logs
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


class LogManager:
    """Manages application-wide logging configuration."""
    
    _initialized = False
    _log_file_path: Optional[Path] = None
    _session_timestamp: Optional[str] = None
    
    @classmethod
    def get_log_directory(cls) -> Path:
        """
        Get the directory where logs should be stored.
        
        Returns:
            Path to log directory (e.g., ~/.fonixflow/logs/)
        """
        from .path_manager import PathManager
        return PathManager.get_logs_dir()
    
    @classmethod
    def get_log_file_path(cls) -> Path:
        """
        Get the path to the current session's log file.
        
        Returns:
            Path to log file (e.g., ~/.fonixflow/logs/fonixflow_20241126_143022.log)
        """
        if cls._log_file_path is None:
            log_dir = cls.get_log_directory()
            # Generate timestamp for this session if not already set
            if cls._session_timestamp is None:
                cls._session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            cls._log_file_path = log_dir / f"fonixflow_{cls._session_timestamp}.log"
        return cls._log_file_path
    
    @classmethod
    def get_session_timestamp(cls) -> str:
        """
        Get the timestamp for the current session.
        
        Returns:
            Timestamp string (e.g., '20241126_143022')
        """
        if cls._session_timestamp is None:
            cls._session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return cls._session_timestamp
    
    @classmethod
    def setup_logging(cls, level=logging.INFO, console_output=True):
        """
        Set up centralized logging for the application.
        
        Args:
            level: Logging level (default: INFO)
            console_output: Whether to also output to console (default: True)
        """
        if cls._initialized:
            return  # Already initialized
        
        log_file = cls.get_log_file_path()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # Generate timestamp for this session
        if cls._session_timestamp is None:
            cls._session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create new log file for this session (with timestamp in name)
        log_file = cls.get_log_file_path()
        
        # File handler with rotation (10MB per file, keep 5 backups)
        # Note: Each app run creates a new file, but rotation still works within a session
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8',
                mode='w'  # 'w' mode creates a new file for each session
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            # If we can't write to log file, at least log to console
            print(f"Warning: Could not set up file logging: {e}")
        
        # Console handler (optional)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Log startup information
        logger = logging.getLogger(__name__)
        logger.info("=" * 70)
        logger.info("FonixFlow Logging System Initialized")
        logger.info("=" * 70)
        logger.info(f"Session timestamp: {cls._session_timestamp}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        if getattr(sys, 'frozen', False):
            logger.info(f"Running as bundled application")
            if hasattr(sys, '_MEIPASS'):
                logger.info(f"PyInstaller temp directory: {sys._MEIPASS}")
        else:
            logger.info(f"Running from source")
        logger.info(f"Executable: {sys.executable}")
        logger.info("=" * 70)
        
        cls._initialized = True
    
    @classmethod
    def get_recent_logs(cls, lines=100) -> str:
        """
        Get recent log entries from the log file.
        
        Args:
            lines: Number of recent lines to retrieve (default: 100)
            
        Returns:
            String containing recent log entries
        """
        log_file = cls.get_log_file_path()
        if not log_file.exists():
            return "No log file found."
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent_lines)
        except Exception as e:
            return f"Error reading log file: {e}"
    
    @classmethod
    def get_log_file_size(cls) -> int:
        """
        Get the size of the log file in bytes.
        
        Returns:
            File size in bytes, or 0 if file doesn't exist
        """
        log_file = cls.get_log_file_path()
        if log_file.exists():
            return log_file.stat().st_size
        return 0
    
    @classmethod
    def clear_logs(cls) -> bool:
        """
        Clear the current session's log file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            log_file = cls.get_log_file_path()
            # Clear the current session's log file
            if log_file.exists():
                log_file.unlink()
            # Create new empty log file for this session
            log_file.touch()
            logger = logging.getLogger(__name__)
            logger.info(f"Current session log file cleared: {log_file}")
            return True
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to clear logs: {e}")
            return False
    
    @classmethod
    def get_all_log_files(cls) -> list:
        """
        Get a list of all log files in the log directory, sorted by modification time (newest first).
        
        Returns:
            List of Path objects for all fonixflow log files
        """
        log_dir = cls.get_log_directory()
        log_files = sorted(
            log_dir.glob("fonixflow_*.log*"),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True
        )
        return log_files
    
    @classmethod
    def get_log_info(cls) -> dict:
        """
        Get information about the log file.
        
        Returns:
            Dictionary with log file information
        """
        log_file = cls.get_log_file_path()
        info = {
            'path': str(log_file),
            'exists': log_file.exists(),
            'size': 0,
            'size_mb': 0.0,
            'modified': None
        }
        
        if log_file.exists():
            stat = log_file.stat()
            info['size'] = stat.st_size
            info['size_mb'] = round(stat.st_size / (1024 * 1024), 2)
            info['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return info
