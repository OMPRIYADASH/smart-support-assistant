"""
services/llm.py

Owns all contact with the model provider.
Routes call generate_reply() and handle the two outcomes:
a string, or an exception.
"""

import hashlib
import logging
import os
import time

from openai import OpenAI

logger = logging.getLogger("llm")

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

MODEL = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
MAX_TOKENS = 2048
EMBEDDING_DIM = 768

SYSTEM = (
    "You are a helpful support assistant. "
    "Answer concisely. "
    "If you do not know something, say so plainly instead of guessing."
)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


class LLMError(Exception):
    """Raised when the LLM request fails."""


# -------------------------------------------------------------------
# Local fallback embeddings
# -------------------------------------------------------------------

def _fallback_embedding(text: str) -> list[float]:
    """
    Create a deterministic embedding vector when
    no embedding model is available.
    """

    vec: list[float] = []

    for index in range(EMBEDDING_DIM):
        digest = hashlib.sha256(
            f"{text}:{index}".encode("utf-8")
        ).digest()

        value = (
            (int.from_bytes(digest[:4], "big") % 2000) - 1000
        ) / 1000.0

        vec.append(round(value, 6))

    return vec


def _fallback_embeddings(texts: list[str]) -> list[list[float]]:
    return [_fallback_embedding(text) for text in texts]


# -------------------------------------------------------------------
# OpenRouter response parser
# -------------------------------------------------------------------

def _extract_response_text(response) -> str:
    """
    Extract assistant text from OpenAI/OpenRouter Responses API.
    """

    output_text = getattr(response, "output_text", None)

    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    texts: list[str] = []

    output = getattr(response, "output", None) or []

    if isinstance(output, list):

        for item in output:

            if not hasattr(item, "content"):
                continue

            for content in item.content:

                if getattr(content, "type", "") == "output_text":
                    texts.append(content.text)

    return "\n".join(
        line.strip()
        for line in texts
        if line.strip()
    )
# -------------------------------------------------------------------
# Chat completion
# -------------------------------------------------------------------


def generate_reply(
    history: list[dict],
    system: str = SYSTEM,
) -> str:
    """
    Generate a reply using OpenRouter.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        logger.warning("OPENROUTER_API_KEY missing")
        return "The AI service is currently unavailable. Please try again later."

    messages = [
        {
            "role": "system",
            "content": system,
        }
    ]

    for msg in history:
        messages.append(
            {
                "role": msg["role"],
                "content": msg["content"],
            }
        )

    try:

        start = time.time()

        response = client.responses.create(
            model=MODEL,
            input=messages,
            max_output_tokens=MAX_TOKENS,
        )

        logger.info(
            "OpenRouter reply took %.2f seconds",
            time.time() - start,
        )

        reply = _extract_response_text(response)

        if reply.strip():
            return reply

        logger.warning("Model returned an empty response")

        return "The AI service is currently unavailable. Please try again later."

    except Exception as exc:

        logger.exception("OpenRouter request failed")

        raise LLMError(str(exc))


# -------------------------------------------------------------------
# Embeddings
# -------------------------------------------------------------------

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    OpenRouter chat models do not provide embeddings.

    We therefore use deterministic local embeddings so
    pgvector continues working.
    """

    if not texts:
        return []

    logger.info("Using local fallback embeddings")

    return _fallback_embeddings(texts)


def embed_query(text: str) -> list[float]:
    """
    Embed a query for pgvector similarity search.
    """

    logger.info("Using local fallback query embedding")

    return _fallback_embedding(text)
# -------------------------------------------------------------------
# Document Summary
# -------------------------------------------------------------------


SUMMARY_SYSTEM = """
You are an expert document summarizer.

Generate a concise summary of the document.

Include:

- Main topic
- Important points
- Conclusion

Keep it under 200 words.
"""


def generate_summary(text: str) -> str:
    """
    Generate a summary for an uploaded document.
    """

    history = [
        {
            "role": "user",
            "content": text[:12000],
        }
    ]

    return generate_reply(
        history=history,
        system=SUMMARY_SYSTEM,
    )


# -------------------------------------------------------------------
# Suggested Questions
# -------------------------------------------------------------------

SUGGESTION_SYSTEM = """
You are an AI assistant.

Read the uploaded document and generate exactly five short questions.

Return only the questions.

One question per line.

Example:

Summarize this document
Explain the important points
Generate interview questions
Create study notes
Explain this in simple words
"""


def generate_suggestions(text: str) -> list[str]:
    """
    Generate five suggested questions from a document.
    """

    history = [
        {
            "role": "user",
            "content": f"""
Based on the following document, generate exactly 5 questions that a user might ask.

Document:

{text[:6000]}

Return only the questions, one per line.
""",
        }
    ]

    response = generate_reply(
        history=history,
        system=SUGGESTION_SYSTEM,
    )

    return [
        line.strip("-•1234567890. ").strip()
        for line in response.splitlines()
        if line.strip()
    ]
