from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Chat, Message,Persona
from app.parser import parse_chat
from app.schemas.chat import MessageResponse
from app.services.chat_service import save_chat
from app.services.chunk_service import create_chunks
from app.services.search_service import search_chunks
from app.services.llm_service import generate_response
from app.services.persona_service import create_persona
from app.services.session_service import create_session
from app.models import Chat, Message, Persona, ChatSession
from app.services.session_service import (
    create_session,
    add_message,
    get_session_messages
)
router = APIRouter(prefix="/api/chats", tags=["Chats"])


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
def get_chat_messages(chat_id: int):
    db: Session = SessionLocal()

    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        return chat.messages

    finally:
        db.close()


@router.post("/upload")
async def upload_chat(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt chat files are supported"
        )

    content = await file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Unable to decode the chat file"
        )

    messages = parse_chat(text)

    if not messages:
        raise HTTPException(
            status_code=400,
            detail="No valid messages found in the chat"
        )

    db: Session = SessionLocal()

    try:
        chat = save_chat(
            db,
            file.filename,
            messages
        )

        db_messages = (
            db.query(Message)
            .filter(Message.chat_id == chat.id)
            .order_by(Message.id)
            .all()
        )

        chunks = create_chunks(
            db,
            chat.id,
            db_messages
        )

        return {
            "chat_id": chat.id,
            "filename": chat.filename,
            "message_count": len(messages),
            "chunk_count": len(chunks)
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save chat"
        )

    finally:
        db.close()
        
@router.get("/{chat_id}/search")
def search_chat(
    chat_id: int,
    query: str,
    limit: int = 5
):
    db: Session = SessionLocal()

    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        results = search_chunks(
            db,
            chat_id,
            query,
            limit
        )

        return [
            {
                "chunk_id": result["chunk"].id,
                "chunk_index": result["chunk"].chunk_index,
                "similarity": round(result["similarity"], 4),
                "content": result["chunk"].content
            }
            for result in results
        ]

    finally:
        db.close()

@router.post("/{chat_id}/ask")
def ask_chat(
    chat_id: int,
    query: str,
    session_id: int,
    limit: int = 5
):
    db: Session = SessionLocal()

    try:
        chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id)
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        session = (
            db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.chat_id == chat_id
            )
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        results = search_chunks(
            db,
            chat_id,
            query,
            limit
        )

        persona = (
            db.query(Persona)
            .filter(Persona.chat_id == chat_id)
            .first()
        )

        persona_profile = ""

        if persona:
            persona_profile = persona.profile

        context = "\n\n".join(
            result["chunk"].content
            for result in results
        )

        previous_messages = get_session_messages(
            db,
            session_id
        )

        conversation_history = "\n".join(
            f"{message.role}: {message.content}"
            for message in previous_messages
        )

        answer = generate_response(
            context=context,
            query=query,
            persona_profile=persona_profile,
            conversation_history=conversation_history
        )

        add_message(
            db,
            session_id,
            "user",
            query
        )

        add_message(
            db,
            session_id,
            "assistant",
            answer
        )

        return {
            "answer": answer,
            "session_id": session_id,
            "sources": [
                {
                    "chunk_id": result["chunk"].id,
                    "similarity": round(
                        result["similarity"],
                        4
                    )
                }
                for result in results
            ]
        }

    finally:
        db.close()   
        
@router.post("/{chat_id}/persona")
def generate_chat_persona(chat_id: int):
    db: Session = SessionLocal()

    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        persona = create_persona(
            db,
            chat_id
        )

        return {
            "chat_id": chat_id,
            "profile": persona.profile
        }

    finally:
        db.close()    
        
@router.post("/{chat_id}/sessions")
def create_chat_session(chat_id: int):
    db: Session = SessionLocal()

    try:
        chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id)
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        session = create_session(
            db,
            chat_id
        )

        return {
            "session_id": session.id,
            "chat_id": chat_id
        }

    finally:
        db.close()