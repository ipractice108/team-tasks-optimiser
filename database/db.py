import os
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session, joinedload
from .models import Base, User, Message, AnalysisReport


class Database:
    """Database manager class"""

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./chat_analyzer.db')

        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    # User operations
    def get_or_create_user(self, telegram_id: int, username: str = None,
                          first_name: str = None, last_name: str = None) -> User:
        """Get existing user or create new one"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()

    def set_admin(self, telegram_id: int, is_admin: bool = True):
        """Set user as admin"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.is_admin = is_admin
                session.commit()
        finally:
            session.close()

    def is_admin(self, telegram_id: int) -> bool:
        """Check if user is admin"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            return user.is_admin if user else False
        finally:
            session.close()

    # Message operations
    def save_message(self, message_id: int, telegram_id: int, chat_id: int,
                    text: str, thread_id: Optional[int] = None,
                    topic_name: Optional[str] = None,
                    username: str = None, first_name: str = None,
                    last_name: str = None) -> Message:
        """Save message to database"""
        session = self.get_session()
        try:
            user = self.get_or_create_user(telegram_id, username, first_name, last_name)

            message = Message(
                message_id=message_id,
                user_id=user.id,
                chat_id=chat_id,
                thread_id=thread_id,
                topic_name=topic_name,
                text=text,
                created_at=datetime.utcnow()
            )
            session.add(message)
            session.commit()
            return message
        finally:
            session.close()

    def get_messages(self, chat_id: int, days_back: int = 7,
                    topic_name: Optional[str] = None) -> List[Message]:
        """Get messages from chat for specified period"""
        session = self.get_session()
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            query = session.query(Message).options(joinedload(Message.user)).filter(
                Message.chat_id == chat_id,
                Message.created_at >= since
            )

            if topic_name:
                query = query.filter(Message.topic_name == topic_name)

            messages = query.order_by(Message.created_at).all()

            # Expunge objects from session so they can be used after session closes
            for msg in messages:
                session.expunge(msg)
                session.expunge(msg.user)

            return messages
        finally:
            session.close()

    def get_topics(self, chat_id: int, days_back: int = 7) -> List[str]:
        """Get unique topic names from chat"""
        session = self.get_session()
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            topics = session.query(Message.topic_name).filter(
                Message.chat_id == chat_id,
                Message.created_at >= since,
                Message.topic_name.isnot(None)
            ).distinct().all()
            return [t[0] for t in topics if t[0]]
        finally:
            session.close()

    # Analysis report operations
    def save_report(self, telegram_id: int, chat_id: int, report_text: str,
                   messages_analyzed: int, period_start: datetime,
                   period_end: datetime) -> AnalysisReport:
        """Save analysis report"""
        session = self.get_session()
        try:
            user = self.get_or_create_user(telegram_id)

            report = AnalysisReport(
                user_id=user.id,
                chat_id=chat_id,
                report_text=report_text,
                messages_analyzed=messages_analyzed,
                period_start=period_start,
                period_end=period_end
            )
            session.add(report)
            session.commit()
            return report
        finally:
            session.close()

    def get_last_report(self, telegram_id: int, chat_id: int) -> Optional[AnalysisReport]:
        """Get last report for user and chat"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                return None

            report = session.query(AnalysisReport).filter_by(
                user_id=user.id,
                chat_id=chat_id
            ).order_by(desc(AnalysisReport.created_at)).first()
            return report
        finally:
            session.close()
