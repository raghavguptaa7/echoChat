from fastapi import FastAPI

from app.api.chats import router as chats_router
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EchoChat API",
    description="Chat with AI personas built from conversation history",
    version="0.1.0"
)

app.include_router(chats_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}