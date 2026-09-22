from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    return model.encode(text).tolist()


def generate_embeddings(texts: list[str]):
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True
    )

    return embeddings.tolist()