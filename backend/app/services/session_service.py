from sqlalchemy.orm import Session

from app.models import ChatSession, SessionMessage


def create_session(db: Session, chat_id: int):
    session = ChatSession(
        chat_id=chat_id
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def add_message(
    db: Session,
    session_id: int,
    role: str,
    content: str
):
    message = SessionMessage(
        session_id=session_id,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_session_messages(
    db: Session,
    session_id: int
):
    return (
        db.query(SessionMessage)
        .filter(
            SessionMessage.session_id == session_id
        )
        .order_by(SessionMessage.created_at)
        .all()
    )