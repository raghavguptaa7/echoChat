from sqlalchemy.orm import Session

from app.models import ConversationChunk
from app.services.embedding_service import generate_embedding


def search_chunks(
    db: Session,
    chat_id: int,
    query: str,
    limit: int = 5,
    threshold: float = 0.1
):
    query_embedding = generate_embedding(query)

    distance = ConversationChunk.embedding.cosine_distance(
        query_embedding
    )

    results = (
        db.query(
            ConversationChunk,
            distance.label("distance")
        )
        .filter(ConversationChunk.chat_id == chat_id)
        .order_by(distance)
        .limit(limit)
        .all()
    )

    return [
        {
            "chunk": chunk,
            "similarity": 1 - distance_value
        }
        for chunk, distance_value in results
        if 1 - distance_value >= threshold
    ]