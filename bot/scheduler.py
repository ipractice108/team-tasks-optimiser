import os
import logging
from datetime import datetime, time
from typing import List, Tuple
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import ContextTypes, Application
from database import Database

logger = logging.getLogger(__name__)


class AnalysisScheduler:
    """Scheduler for automatic analysis"""

    def __init__(self, db: Database, bot_handlers):
        self.db = db
        self.bot_handlers = bot_handlers
        self.scheduler = AsyncIOScheduler()
        self.admin_id = int(os.getenv('ADMIN_USER_ID', 0))

    def setup(self, application: Application):
        """Setup scheduled tasks"""
        # Get schedule from environment
        schedules = self._parse_schedule()

        for day, hour, minute in schedules:
            trigger = CronTrigger(
                day_of_week=day,
                hour=hour,
                minute=minute,
                timezone='UTC'
            )

            self.scheduler.add_job(
                self._run_scheduled_analysis,
                trigger=trigger,
                args=[application],
                id=f'analysis_{day}_{hour}_{minute}',
                replace_existing=True
            )

            logger.info(f"Scheduled analysis: day={day}, time={hour}:{minute:02d}")

    def _parse_schedule(self) -> List[Tuple[int, int, int]]:
        """Parse schedule from environment variables"""
        schedules = []

        # Default: Monday and Thursday at 10:00
        default_schedules = [
            (0, 10, 0),  # Monday 10:00
            (3, 10, 0),  # Thursday 10:00
        ]

        try:
            # Try to parse custom schedule
            day1 = int(os.getenv('ANALYSIS_SCHEDULE_DAY_1', 0))
            time1 = os.getenv('ANALYSIS_SCHEDULE_TIME_1', '10:00')
            hour1, min1 = map(int, time1.split(':'))
            schedules.append((day1, hour1, min1))

            day2 = int(os.getenv('ANALYSIS_SCHEDULE_DAY_2', 3))
            time2 = os.getenv('ANALYSIS_SCHEDULE_TIME_2', '10:00')
            hour2, min2 = map(int, time2.split(':'))
            schedules.append((day2, hour2, min2))

        except Exception as e:
            logger.warning(f"Error parsing schedule, using defaults: {e}")
            schedules = default_schedules

        return schedules

    async def _run_scheduled_analysis(self, application: Application):
        """Run scheduled analysis for all monitored chats"""
        logger.info("Running scheduled analysis...")

        try:
            # Get all chats from database
            session = self.db.get_session()
            from database.models import Message
            from sqlalchemy import distinct

            # Get unique chat IDs that have messages
            chat_ids = session.query(distinct(Message.chat_id)).all()
            chat_ids = [c[0] for c in chat_ids]

            logger.info(f"Found {len(chat_ids)} chats to analyze")

            # Perform analysis for each chat
            for chat_id in chat_ids:
                try:
                    # Send analysis to admin
                    await self.bot_handlers.perform_analysis(
                        self.admin_id,
                        chat_id,
                        application
                    )

                    logger.info(f"Completed analysis for chat {chat_id}")

                except Exception as e:
                    logger.error(f"Error analyzing chat {chat_id}: {e}")

            session.close()

        except Exception as e:
            logger.error(f"Error in scheduled analysis: {e}")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
