from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.parser import parse_chat
from app.services.chat_service import save_chat

router = APIRouter(prefix="/api/chats", tags=["Chats"])


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

        return {
            "chat_id": chat.id,
            "filename": chat.filename,
            "message_count": len(messages)
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save chat"
        )

    finally:
        db.close()