#!/usr/bin/env python3
"""
Telegram Chat Analyzer Bot
AI-powered bot for analyzing team chats and providing optimization insights
"""

import os
import sys
import logging
from dotenv import load_dotenv
from telegram.ext import Application

from database import Database
from analyzer import ClaudeAnalyzer
from bot import setup_handlers, AnalysisScheduler

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def validate_env():
    """Validate required environment variables"""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY', 'ADMIN_USER_ID']
    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file")
        return False

    return True


async def post_init(application: Application) -> None:
    """Actions to perform after bot initialization"""
    logger.info("Bot initialized successfully")
    bot_info = await application.bot.get_me()
    logger.info(f"Bot username: @{bot_info.username}")
    logger.info(f"Bot ID: {bot_info.id}")


async def post_shutdown(application: Application) -> None:
    """Actions to perform after bot shutdown"""
    logger.info("Bot shutting down...")


def main():
    """Main function to run the bot"""
    logger.info("="*60)
    logger.info("Starting Telegram Chat Analyzer Bot")
    logger.info("="*60)

    # Validate environment
    if not validate_env():
        sys.exit(1)

    # Initialize database
    logger.info("Initializing database...")
    db = Database()
    db.init_db()
    logger.info("Database initialized")

    # Set admin user
    admin_id = int(os.getenv('ADMIN_USER_ID'))
    db.set_admin(admin_id, True)
    logger.info(f"Admin user set: {admin_id}")

    # Initialize analyzer
    logger.info("Initializing AI analyzer...")
    analyzer = ClaudeAnalyzer()
    logger.info("AI analyzer initialized")

    # Create application
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = Application.builder().token(token).build()

    # Setup handlers
    logger.info("Setting up bot handlers...")
    bot_handlers = setup_handlers(application, db, analyzer)
    logger.info("Bot handlers configured")

    # Setup scheduler
    logger.info("Setting up analysis scheduler...")
    scheduler = AnalysisScheduler(db, bot_handlers)
    scheduler.setup(application)
    scheduler.start()
    logger.info("Scheduler started")

    # Add shutdown handler
    async def on_shutdown(application):
        scheduler.shutdown()
        await post_shutdown(application)

    application.post_shutdown = on_shutdown

    # Start the bot
    logger.info("="*60)
    logger.info("Bot is running! Press Ctrl+C to stop.")
    logger.info("="*60)

    try:
        application.run_polling(
            allowed_updates=['message', 'channel_post'],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("Received stop signal")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise
    finally:
        scheduler.shutdown()
        logger.info("Bot stopped")


if __name__ == '__main__':
    main()
