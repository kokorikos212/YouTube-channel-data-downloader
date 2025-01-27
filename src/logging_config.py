import os
import logging
from logging.handlers import RotatingFileHandler

def logging_configuration():
    """
    Configures global logging settings for the project, including file rotation 
    and console output. Logging level can be set with the LOG_LEVEL environment variable.
    """
    # Set log directory and ensure it exists
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # Set log file path
    log_file_path = os.path.join(log_dir, 'app.log')

    # Set logging level from environment variable or default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = (
        '%(name)s - %(levelname)s - %(message)s '
        '- File: %(pathname)s - Func: %(funcName)s - Line: %(lineno)d '
        # '- Process: %(process)d - Thread: %(threadName)s'
    )

    # Prevent duplicate handlers if already configured
    if not logging.getLogger().hasHandlers():
        # Configure rotating file handler
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5  # 5MB per file, 5 backups
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))

        # Configure console handler for immediate feedback in CLI
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))

        # Set up root logger with both handlers
        logging.basicConfig(level=log_level, handlers=[file_handler, console_handler])
        
        logging.info("Logging configuration setup complete.")

        # Example: Log a startup message at the INFO level
        logging.info("Application started. Log level set to: %s", log_level)
