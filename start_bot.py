#!/usr/bin/env python3
"""
Quick start script for the Slack Tweet Approval Bot
This script starts both the webhook server and the main bot process
"""

import os
import sys
import time
import subprocess
import threading
from dotenv import load_dotenv
from logger_config import get_logger, setup_logging

# Initialize logging first
setup_logging()
logger = get_logger("startup")


def check_env_vars():
    """Check if all required environment variables are set"""
    load_dotenv()

    required_vars = [
        "GEMINI_API_KEY",
        "API_KEY",
        "API_SECRET",
        "ACCESS_TOKEN",
        "ACCESS_TOKEN_SECRET",
        "GMAIL_USER",
        "GMAIL_APP_PASSWORD",
        "SLACK_BOT_TOKEN",
        "SLACK_CHANNEL",
        "SLACK_SIGNING_SECRET",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error("❌ Missing environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("📝 Please check your .env file and setup_guide.md")
        return False

    logger.info("✅ All environment variables are set!")
    return True


def start_webhook_server():
    """Start the Flask webhook server"""
    logger.info("🚀 Starting Slack webhook server...")
    try:
        subprocess.run([sys.executable, "slack_webhook.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Webhook server failed: {e}")
    except KeyboardInterrupt:
        logger.info("🛑 Webhook server stopped")


def start_main_bot():
    """Start the main bot process"""
    logger.info("🤖 Starting main bot process...")
    time.sleep(2)  # Give webhook server time to start
    try:
        subprocess.run([sys.executable, "tweet.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Main bot failed: {e}")
    except KeyboardInterrupt:
        logger.info("🛑 Main bot stopped")


def main():
    """Main function to orchestrate bot startup"""
    logger.info("🚀 Starting Slack Tweet Approval Bot...")
    logger.info("=" * 50)

    # Check environment variables
    if not check_env_vars():
        sys.exit(1)

    logger.info("📋 Starting components...")
    logger.info("   1. Slack webhook server (Flask)")
    logger.info("   2. Main bot process")
    logger.info("🔧 Make sure ngrok is running if using local development!")
    logger.info("   Command: ngrok http 5000")
    logger.info("=" * 50)

    try:
        # Start webhook server in a separate thread
        webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
        webhook_thread.start()

        # Start main bot in current thread
        start_main_bot()

    except KeyboardInterrupt:
        logger.info("🛑 Shutting down bot...")
        logger.info("✅ Bot stopped successfully!")


if __name__ == "__main__":
    main()
