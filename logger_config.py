import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console output"""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        # Format the message
        formatted = super().format(record)
        return formatted


def setup_logging():
    """Configure logging for the entire project"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Formatter for files (detailed)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Formatter for console (simplified with colors)
    console_formatter = ColoredFormatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"
    )

    # === FILE HANDLERS ===

    # Main application log (rotating)
    main_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "tweet_bot.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    main_file_handler.setLevel(logging.INFO)
    main_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(main_file_handler)

    # Error log (only errors and critical)
    error_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_file_handler)

    # Debug log (everything, for development)
    debug_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "debug.log",
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=2,
    )
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(debug_file_handler)

    # === CONSOLE HANDLER ===
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # === COMPONENT-SPECIFIC LOGGERS ===

    # Gmail logger
    gmail_logger = logging.getLogger("gmail")
    gmail_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "gmail.log", maxBytes=5 * 1024 * 1024, backupCount=2
    )
    gmail_file_handler.setFormatter(file_formatter)
    gmail_logger.addHandler(gmail_file_handler)

    # Slack logger
    slack_logger = logging.getLogger("slack")
    slack_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "slack.log", maxBytes=5 * 1024 * 1024, backupCount=2
    )
    slack_file_handler.setFormatter(file_formatter)
    slack_logger.addHandler(slack_file_handler)

    # Twitter logger
    twitter_logger = logging.getLogger("twitter")
    twitter_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "twitter.log", maxBytes=5 * 1024 * 1024, backupCount=2
    )
    twitter_file_handler.setFormatter(file_formatter)
    twitter_logger.addHandler(twitter_file_handler)

    # LLM logger
    llm_logger = logging.getLogger("llm")
    llm_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "llm.log", maxBytes=5 * 1024 * 1024, backupCount=2
    )
    llm_file_handler.setFormatter(file_formatter)
    llm_logger.addHandler(llm_file_handler)

    # Webhook logger
    webhook_logger = logging.getLogger("webhook")
    webhook_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "webhook.log", maxBytes=5 * 1024 * 1024, backupCount=2
    )
    webhook_file_handler.setFormatter(file_formatter)
    webhook_logger.addHandler(webhook_file_handler)

    # === INITIAL LOG MESSAGE ===
    logging.info("=" * 60)
    logging.info("🚀 Tweet Automation Bot - Logging System Initialized")
    logging.info(f"📅 Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific component"""
    return logging.getLogger(name)


# Performance logging decorator
def log_performance(func):
    """Decorator to log function performance"""

    def wrapper(*args, **kwargs):
        import time

        logger = get_logger(func.__module__)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            logger.debug(
                f"⚡ {func.__name__} completed in {end_time - start_time:.2f}s"
            )
            return result
        except Exception as e:
            end_time = time.time()
            logger.error(
                f"💥 {func.__name__} failed after {end_time - start_time:.2f}s: {e}"
            )
            raise

    return wrapper


# Initialize logging when module is imported
if __name__ != "__main__":
    setup_logging()
