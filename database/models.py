from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """User model for storing Telegram users"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="user")
    reports = relationship("AnalysisReport", back_populates="user")


class Message(Base):
    """Message model for storing chat messages"""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    chat_id = Column(BigInteger, nullable=False, index=True)
    thread_id = Column(BigInteger, nullable=True)  # For topics/threads
    topic_name = Column(String(255), nullable=True)  # Topic name
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="messages")


class AnalysisReport(Base):
    """Analysis report model"""
    __tablename__ = 'analysis_reports'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    report_text = Column(Text, nullable=False)
    messages_analyzed = Column(Integer, default=0)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="reports")
