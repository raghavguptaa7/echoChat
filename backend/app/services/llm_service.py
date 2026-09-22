import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "openai/gpt-oss-120b"


def get_content(response):
    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    return content.strip()


def generate_response(
    context: str,
    query: str,
    persona_profile: str = "",
    conversation_history: str = ""
):
    prompt = f"""
You are an AI persona reconstructed from a person's conversation history.

PERSONA PROFILE:
{persona_profile}

RELEVANT CONVERSATION:
{context}

PREVIOUS CONVERSATION:
{conversation_history}

USER MESSAGE:
{query}

Rules:
- Respond naturally and conversationally.
- Match the persona's language, tone, and communication style.
- Use Hinglish or casual expressions when supported by the evidence.
- Maintain continuity with previous conversation.
- Do not invent personal facts.
- Do not mention the persona profile or retrieved context.
- Do not claim to literally be the real person.
- Answer as an AI representation of the persona.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI persona reconstructed "
                    "from conversation history."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        include_reasoning=False,
        temperature=0.8,
        max_completion_tokens=500
    )

    return get_content(response)

def generate_persona_batch_summary(conversation: str):
    prompt = f"""
Analyze the following messages from one person.

Create a concise evidence-based summary covering:

- Communication style
- Tone
- Language preferences
- Hinglish usage
- Common expressions
- Interests
- Preferences
- Recurring opinions
- Emotional communication patterns
- Typical response style
- Important recurring facts or memories

Only use information supported by the messages.
Do not invent facts.

MESSAGES:

{conversation}

Return ONLY the summary.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        reasoning_effort="low",
        include_reasoning=False,
        temperature=0.2,
        max_completion_tokens=600
    )

    return get_content(response)


def generate_final_persona_profile(summaries: str):
    prompt = f"""
Create a final persona profile from the following summaries of one person.

The profile will be given to another AI so it can reproduce this person's
communication style accurately.

Include:

- Communication style
- Tone
- Language and Hinglish usage
- Frequently used expressions
- Interests
- Preferences
- Personality traits demonstrated in conversation
- Emotional communication patterns
- Typical response style
- Recurring facts, memories and viewpoints

Rules:

- Use only evidence from the summaries.
- Do not invent facts.
- Do not exaggerate.
- Do not repeat information unnecessarily.
- Prioritize patterns that occur repeatedly.
- Keep the profile concise but informative.

SUMMARIES:

{summaries}

Return ONLY the final persona profile.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        reasoning_effort="low",
        include_reasoning=False,
        temperature=0.2,
        max_completion_tokens=700
    )

    return get_content(response)