from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)

    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan"
    )

    chunks = relationship(
        "ConversationChunk",
        back_populates="chat",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=True)
    content = Column(Text, nullable=False)

    chat = relationship(
        "Chat",
        back_populates="messages"
    )


class ConversationChunk(Base):
    __tablename__ = "conversation_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    chat = relationship(
        "Chat",
        back_populates="chunks"
    )