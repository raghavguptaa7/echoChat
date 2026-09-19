from sqlalchemy.orm import Session

from app.models import ConversationChunk


def create_chunks(
    db: Session,
    chat_id: int,
    messages: list,
    chunk_size: int = 10
):
    chunks = []

    for i in range(0, len(messages), chunk_size):
        batch = messages[i:i + chunk_size]

        content = "\n".join(
            f"{message.sender}: {message.content}"
            for message in batch
        )

        chunk = ConversationChunk(
            chat_id=chat_id,
            chunk_index=len(chunks),
            content=content
        )

        db.add(chunk)
        chunks.append(chunk)

    db.commit()

    return chunks