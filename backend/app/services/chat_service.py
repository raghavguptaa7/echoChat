from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Chat, Message


def save_chat(db: Session, filename: str, messages: list):
    chat = Chat(filename=filename)
    db.add(chat)
    db.flush()

    for item in messages:
        timestamp = None

        try:
            timestamp = datetime.strptime(
                item["timestamp"],
                "%d/%m/%y %I:%M %p"
            )
        except ValueError:
            pass

        message = Message(
            chat_id=chat.id,
            sender=item["sender"],
            timestamp=timestamp,
            content=item["message"]
        )

        db.add(message)

    db.commit()
    db.refresh(chat)

    return chat