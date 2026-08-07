"""
services/llm.py
Owns all contact with the model provider. Routes call generate_reply() and
handle the two outcomes: a string, or an exception.
"""
import hashlib
import logging
import os
import time
from openai import OpenAI

logger = logging.getLogger("llm")

# Chat model configuration. Can be overridden via the OPENROUTER_MODEL env var.
MODEL = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
MAX_TOKENS = 2048
EMBEDDING_DIM = 768

# System prompt stored server-side.
SYSTEM = (
    "You are a helpful support assistant. Answer concisely. "
    "If you do not know something, say so plainly instead of guessing."
)

client = None


class LLMError(Exception):
    """Raised for any failure talking to the model. Routes catch this one
    type and don't need to know *why* it failed — only that it did."""


def _fallback_embedding(text: str) -> list[float]:
    """Create a deterministic embedding vector when the provider is unavailable."""
    vec: list[float] = []
    for index in range(EMBEDDING_DIM):
        digest = hashlib.sha256(f"{text}:{index}".encode("utf-8")).digest()
        value = (int.from_bytes(digest[:4], "big") % 2000 - 1000) / 1000.0
        vec.append(round(value, 6))
    return vec


def _fallback_embeddings(texts: list[str]) -> list[list[float]]:
    return [_fallback_embedding(text) for text in texts]


def _extract_response_text(response) -> str:
    """Extract text from an OpenAI Responses API response object."""
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output = getattr(response, "output", None) or []
    texts: list[str] = []
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict):
                content = item.get("content")
                if isinstance(content, str):
                    texts.append(content)
                elif isinstance(content, list):
                    for fragment in content:
                        if isinstance(fragment, dict) and fragment.get("type") == "output_text":
                            texts.append(fragment.get("text", ""))
                        elif isinstance(fragment, str):
                            texts.append(fragment)
    # Fallback: try attributes commonly present (choices/messages)
    if not texts:
        choices = getattr(response, "choices", None) or []
        for c in choices:
            if isinstance(c, dict):
                msg = c.get("message")
                if isinstance(msg, dict):
                    txt = msg.get("content") or msg.get("text")
                    if isinstance(txt, str):
                        texts.append(txt)
                elif "text" in c:
                    t = c.get("text")
                    if isinstance(t, str):
                        texts.append(t)
    return "\n".join(line.strip() for line in texts if line and line.strip())


def generate_reply(history: list[dict], system: str = SYSTEM) -> str:
    """
    history: [{"role": "user"|"assistant", "content": "..."}, ...]
    in chronological order, already capped by the caller (see crud.load_history).
    Returns the assistant's reply text, or raises LLMError.

    `system` defaults to the plain SYSTEM prompt. The RAG chat flow passes an
    augmented version (SYSTEM + retrieved context + "answer only from context")
    so the same function serves both grounded and ungrounded replies.
    """
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY missing; using fallback reply")
        return "The AI service is currently unavailable. Please try again later."

    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

    messages = [{"role": "system", "content": system}]
    for msg in history:
        role = "user" if msg["role"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["content"]})

    try:
        start = time.time()
        response = client.responses.create(
            model=MODEL,
            input=messages,
            max_output_tokens=MAX_TOKENS,
        )
        logger.info("OpenRouter reply took %.2f seconds", time.time() - start)

        reply = _extract_response_text(response)
        if reply:
            return reply

        logger.warning("Model returned an empty reply")
        return "The AI service is currently unavailable. Please try again later."

    except Exception:
        logger.exception("OpenRouter request failed; using fallback reply")
        return "The AI service is currently unavailable. Please try again later."


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of strings, returning one 768-float vector per input,
    in the same order. Used by the document pipeline (services/rag.py)
    to turn chunks into vectors before storing them.

    OpenRouter chat models do not provide embeddings via this SDK path.
    This function therefore always returns local fallback embeddings. For
    production, use a dedicated embedding provider and update this function.
    """
    if not texts:
        return []
    return _fallback_embeddings(texts)


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
    history = [
        {
            "role": "user",
            "content": text[:12000]
        }
    ]

    return generate_reply(
        history,
        system=SUMMARY_SYSTEM,
    )


SUGGESTION_SYSTEM = """
You are an AI assistant.

Read the uploaded document and generate exactly five short questions.

Return only the questions.

One question per line.
"""


def generate_suggestions(text: str) -> list[str]:
    history = [
        {
            "role": "user",
            "content": f"""
Based on the following document, generate exactly 5 questions that a user might ask.

Document:

{text[:6000]}

Return only the questions, one per line.
"""
        }
    ]

    response = generate_reply(history)

    return [
        line.strip("-•1234567890. ")
        for line in response.splitlines()
        if line.strip()
    ]


def embed_query(text: str) -> list[float]:
    """
    Embed a single search query into one 768-float vector.

    OpenRouter chat models do not provide embeddings via this SDK path.
    This function therefore returns the local fallback embedding.
    """
    return _fallback_embedding(text)
