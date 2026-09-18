from datetime import datetime

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    sender: str
    timestamp: datetime | None
    content: str

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    id: int
    filename: str
    message_count: int