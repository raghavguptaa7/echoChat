from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Chat, Message
from app.parser import parse_chat
from app.schemas.chat import MessageResponse
from app.services.chat_service import save_chat
from app.services.chunk_service import create_chunks
from app.services.search_service import search_chunks

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
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content
            }
            for chunk in results
        ]

    finally:
        db.close()