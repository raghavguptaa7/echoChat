from fastapi import FastAPI, UploadFile, File, HTTPException
from app.parser import parse_chat

app = FastAPI(
    title="EchoChat API",
    description="Chat with AI personas built from conversation history",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/chats/upload")
async def upload_chat(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt chat files are supported"
        )

    content = await file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Unable to decode the chat file"
        )

    messages = parse_chat(text)

    if not messages:
        raise HTTPException(
            status_code=400,
            detail="No valid messages found in the chat"
        )

    return {
        "filename": file.filename,
        "message_count": len(messages),
        "messages": messages
    }