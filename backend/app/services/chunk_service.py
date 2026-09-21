from sqlalchemy.orm import Session

from app.models import ConversationChunk
from app.services.embedding_service import generate_embedding


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

        embedding = generate_embedding(content)

        chunk = ConversationChunk(
            chat_id=chat_id,
            chunk_index=len(chunks),
            content=content,
            embedding=embedding
        )

        db.add(chunk)
        chunks.append(chunk)

    db.commit()

    return chunks