from sqlalchemy.orm import Session

from app.models import ConversationChunk
from app.services.embedding_service import generate_embeddings


def create_chunks(
    db: Session,
    chat_id: int,
    messages: list,
    chunk_size: int = 50
):
    chunks = []

    for i in range(0, len(messages), chunk_size):
        batch = messages[i:i + chunk_size]

        content = "\n".join(
            f"{message.sender}: {message.content}"
            for message in batch
        )

        chunks.append(
            ConversationChunk(
                chat_id=chat_id,
                chunk_index=len(chunks),
                content=content
            )
        )

    contents = [
        chunk.content
        for chunk in chunks
    ]

    embeddings = generate_embeddings(contents)

    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding
        db.add(chunk)

    db.commit()

    return chunks