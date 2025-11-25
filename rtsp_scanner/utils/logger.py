"""Logging utility for RTSP Scanner"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class RTSPLogger:
    """Custom logger for RTSP scanner with debug capabilities"""

    def __init__(self, name: str = "rtsp_scanner", debug: bool = False, log_file: str = None):
        """
        Initialize logger

        Args:
            name: Logger name
            debug: Enable debug mode
            log_file: Optional file path for logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

        # Remove existing handlers
        self.logger.handlers = []

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)

        # Format
        if debug:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
        else:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)


def setup_logger(debug: bool = False, log_file: str = None) -> RTSPLogger:
    """
    Setup and return a logger instance

    Args:
        debug: Enable debug mode
        log_file: Optional file path for logging

    Returns:
        RTSPLogger instance
    """
    return RTSPLogger(debug=debug, log_file=log_file)
