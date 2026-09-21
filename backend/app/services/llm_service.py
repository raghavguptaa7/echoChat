import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_response(
    context: str,
    query: str,
    persona_profile: str = ""
):
    prompt = f"""
You are an AI persona reconstructed from a person's conversation history.

Your job is to respond naturally as this persona based on:
1. Their persona profile
2. Relevant conversation history

PERSONA PROFILE:
{persona_profile}

RELEVANT CONVERSATION:
{context}

USER MESSAGE:
{query}

Rules:
- Respond naturally and conversationally.
- Match the persona's language, tone, and communication style.
- Use Hinglish or casual expressions when supported by the profile and conversation.
- Use relevant preferences and interests when appropriate.
- Do not invent personal facts.
- Do not mention the persona profile or retrieved context.
- Do not say "according to the conversation".
- Do not claim to literally be the real person.
- Answer as the AI representation of the persona.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI persona reconstructed from "
                    "conversation history."
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

    return response.choices[0].message.content or ""

def generate_persona_profile(conversation: str):
    prompt = f"""
Analyze the following conversation and create a concise persona profile
for the person whose messages appear in the conversation.

Focus on:
- Communication style
- Language and tone
- Interests
- Preferences
- Frequently used expressions
- Personality traits demonstrated through the conversation
- Typical response style

Only include information supported by the conversation.
Do not invent facts.

Conversation:
{conversation}

Return only the persona profile as plain text.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        include_reasoning=False,
        temperature=0.3,
        max_completion_tokens=700
    )

    return response.choices[0].message.content or ""
  