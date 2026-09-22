from sqlalchemy.orm import Session

from app.models import Message, Persona
from app.services.llm_service import (
    generate_persona_batch_summary,
    generate_final_persona_profile
)


TARGET_BATCHES = 12
MAX_MESSAGES_PER_BATCH = 100
MAX_BATCH_CHARACTERS = 6000


def create_persona(
    db: Session,
    chat_id: int,
    target_person: str
):
    messages = (
        db.query(Message)
        .filter(
            Message.chat_id == chat_id,
            Message.sender == target_person
        )
        .order_by(Message.id)
        .all()
    )

    if not messages:
        raise ValueError(
            f"No messages found for participant: {target_person}"
        )

    total_messages = len(messages)

    print(
        f"Found {total_messages} messages "
        f"from {target_person}."
    )

    # Divide the complete timeline into sections.
    section_size = max(
        1,
        (total_messages + TARGET_BATCHES - 1)
        // TARGET_BATCHES
    )

    batches = []

    for start in range(0, total_messages, section_size):

        section = messages[
            start:start + section_size
        ]

        # Sample evenly from each section.
        if len(section) > MAX_MESSAGES_PER_BATCH:

            step = (
                len(section)
                / MAX_MESSAGES_PER_BATCH
            )

            selected = [
                section[int(i * step)]
                for i in range(MAX_MESSAGES_PER_BATCH)
            ]

        else:
            selected = section

        current_batch = []
        current_characters = 0

        for message in selected:

            content = message.content.strip()

            if not content:
                continue

            line = f"{target_person}: {content}"

            if (
                current_characters + len(line)
                > MAX_BATCH_CHARACTERS
            ):
                break

            current_batch.append(line)
            current_characters += len(line)

        if current_batch:
            batches.append(
                "\n".join(current_batch)
            )

    print(
        f"Created {len(batches)} persona batches."
    )

    summaries = []

    for index, batch in enumerate(batches):

        print(
            f"Generating persona summary "
            f"{index + 1}/{len(batches)}..."
        )

        try:
            summary = generate_persona_batch_summary(
                batch
            )

            summaries.append(summary)

        except Exception as error:

            print(
                f"Batch {index + 1} failed: {error}"
            )

    if not summaries:
        raise ValueError(
            "Unable to generate persona summaries. "
            "Check the terminal for the Groq error."
        )

    combined_summaries = "\n\n".join(
        f"SUMMARY {index + 1}:\n{summary}"
        for index, summary in enumerate(summaries)
    )

    # Keep final synthesis request safely bounded.
    combined_summaries = combined_summaries[:16000]

    print(
        f"Generating final persona profile "
        f"from {len(summaries)} summaries..."
    )

    profile = generate_final_persona_profile(
        combined_summaries
    )

    persona = (
        db.query(Persona)
        .filter(
            Persona.chat_id == chat_id
        )
        .first()
    )

    if persona:

        persona.target_person = target_person
        persona.profile = profile

    else:

        persona = Persona(
            chat_id=chat_id,
            target_person=target_person,
            profile=profile
        )

        db.add(persona)

    db.commit()
    db.refresh(persona)

    print("Persona profile saved successfully.")

    return persona