from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=True)
    content = Column(Text, nullable=False)