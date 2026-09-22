from sqlalchemy.orm import Session

from app.models import ConversationChunk
from app.services.embedding_service import generate_embedding


def search_chunks(
    db: Session,
    chat_id: int,
    query: str,
    limit: int = 5,
    threshold: float = 0.1,
    target_person: str | None = None
):
    query_embedding = generate_embedding(query)

    distance = ConversationChunk.embedding.cosine_distance(
        query_embedding
    )

    # Retrieve more candidates than we finally return.
    candidate_limit = max(limit * 3, 15)

    results = (
        db.query(
            ConversationChunk,
            distance.label("distance")
        )
        .filter(
            ConversationChunk.chat_id == chat_id
        )
        .order_by(distance)
        .limit(candidate_limit)
        .all()
    )

    candidates = []

    for chunk, distance_value in results:

        similarity = 1 - distance_value

        if similarity < threshold:
            continue

        target_score = 0

        if target_person:
            target_prefix = f"{target_person}:"

            for line in chunk.content.split("\n"):
                if line.startswith(target_prefix):
                    target_score += 1

        candidates.append(
            {
                "chunk": chunk,
                "similarity": similarity,
                "target_score": target_score
            }
        )

    # Prioritize chunks containing the selected person's messages,
    # while still considering semantic similarity.
    if target_person:
        candidates.sort(
            key=lambda item: (
                item["target_score"],
                item["similarity"]
            ),
            reverse=True
        )
    else:
        candidates.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

    return candidates[:limit]