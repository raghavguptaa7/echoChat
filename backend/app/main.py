from fastapi import FastAPI

app = FastAPI(
    title="EchoChat API",
    description="Chat with AI personas built from conversation history",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}