from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
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

    persona = relationship(
        "Persona",
        back_populates="chat",
        uselist=False,
        cascade="all, delete-orphan"
    )
    sessions = relationship(
    "ChatSession",
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
    embedding = Column(Vector(384), nullable=True)

    chat = relationship(
        "Chat",
        back_populates="chunks"
    )
    
class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)

    chat_id = Column(
        Integer,
        ForeignKey("chats.id"),
        nullable=False,
        unique=True
    )

    target_person = Column(
        String,
        nullable=False
    )

    profile = Column(
        Text,
        nullable=False
    )

    chat = relationship(
        "Chat",
        back_populates="persona"
    )

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        Integer,
        ForeignKey("chats.id"),
        nullable=False
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    chat = relationship(
        "Chat",
        back_populates="sessions"
    )

    messages = relationship(
        "SessionMessage",
        back_populates="session",
        cascade="all, delete-orphan"
    )

class SessionMessage(Base):
    __tablename__ = "session_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id"),
        nullable=False
    )
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    session = relationship(
        "ChatSession",
        back_populates="messages"
    )