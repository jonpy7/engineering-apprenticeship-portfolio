"""
Utility functions for the ETL pipeline.

This module contains shared utilities used across extraction, transformation,
and loading stages.
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
import colorlog


def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Configure structured logging with color output and file logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("etl_pipeline")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    console_format = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: str = "./config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Substitute environment variables
    config = _substitute_env_vars(config)
    
    return config


def _substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively substitute environment variables in config.
    
    Supports syntax: ${VAR_NAME} or ${VAR_NAME:default_value}
    """
    import re
    
    def substitute(value):
        if isinstance(value, str):
            # Pattern to match ${VAR_NAME} or ${VAR_NAME:default}
            pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
            
            def replacer(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else ""
                return os.environ.get(var_name, default_value)
            
            return re.sub(pattern, replacer, value)
        elif isinstance(value, dict):
            return {k: substitute(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [substitute(item) for item in value]
        else:
            return value
    
    return substitute(config)


def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        Timestamp string (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_file_exists(file_path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).is_file()


class PipelineMetrics:
    """Track pipeline execution metrics."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.records_extracted = 0
        self.records_transformed = 0
        self.records_loaded = 0
        self.errors = []
    
    def start(self):
        """Mark pipeline start."""
        self.start_time = datetime.now()
    
    def end(self):
        """Mark pipeline end."""
        self.end_time = datetime.now()
    
    def add_error(self, error: str):
        """Add an error to the metrics."""
        self.errors.append({
            'timestamp': get_timestamp(),
            'error': error
        })
    
    def get_duration(self) -> float:
        """Get pipeline duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            'duration_seconds': self.get_duration(),
            'records_extracted': self.records_extracted,
            'records_transformed': self.records_transformed,
            'records_loaded': self.records_loaded,
            'error_count': len(self.errors),
            'errors': self.errors,
            'success_rate': (
                self.records_loaded / self.records_extracted * 100 
                if self.records_extracted > 0 else 0
            )
        }
