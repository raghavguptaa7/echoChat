from sqlalchemy.orm import Session

from app.models import ConversationChunk
from app.services.embedding_service import generate_embedding


def search_chunks(
    db: Session,
    chat_id: int,
    query: str,
    limit: int = 5
):
    query_embedding = generate_embedding(query)

    results = (
        db.query(ConversationChunk)
        .filter(ConversationChunk.chat_id == chat_id)
        .order_by(
            ConversationChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(limit)
        .all()
    )

    return results