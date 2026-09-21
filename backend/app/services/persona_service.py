from sqlalchemy.orm import Session

from app.models import Message, Persona
from app.services.llm_service import generate_persona_profile


def create_persona(db: Session, chat_id: int):
    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.id)
        .all()
    )

    conversation = "\n".join(
        f"{message.sender}: {message.content}"
        for message in messages
    )

    profile = generate_persona_profile(conversation)

    persona = (
        db.query(Persona)
        .filter(Persona.chat_id == chat_id)
        .first()
    )

    if persona:
        persona.profile = profile
    else:
        persona = Persona(
            chat_id=chat_id,
            profile=profile
        )
        db.add(persona)

    db.commit()
    db.refresh(persona)

    return persona