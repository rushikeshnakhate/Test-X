"""
Generic logging configuration for the application.
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for a service.
    
    Args:
        service_name: Name of the service for logging
        log_level: Logging level (default: INFO)
        
    Returns:
        Logger instance configured for the service
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level))

    # Clear any existing handlers
    logger.handlers = []

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create file handler for DEBUG and above
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{service_name}_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Create console handler for INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # # Log initial setup information
    # logger.info(f"Logging initialized for service: {service_name}")
    # logger.info(f"Log file: {log_file}")
    # logger.info(f"Log level: {log_level}")

    return logger


def get_logger(service_name: str) -> logging.Logger:
    """
    Get a logger instance for a service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Logger instance for the service
    """
    return logging.getLogger(service_name)


def set_log_level(service_name: str, log_level: str) -> None:
    """
    Set the log level for a specific service.
    
    Args:
        service_name (str): Name of the service
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.info(f"Log level set to {log_level} for service: {service_name}")


def add_file_handler(service_name: str, log_file: str, log_level: str = "DEBUG") -> None:
    """
    Add a file handler to an existing logger.
    
    Args:
        service_name (str): Name of the service
        log_file (str): Path to the log file
        log_level (str): Logging level for this handler
    """
    logger = get_logger(service_name)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )

    # Create and configure file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)
    logger.info(f"Added file handler: {log_file} with level {log_level}")
