from app.models import Chunk, Document
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse, ResponseMessage
from app.services.llm import embed_query, embed_texts

router = APIRouter()

"""
services/rag.py

The document pipeline:
extract text -> chunk -> embed -> store in PostgreSQL -> retrieve for RAG.
"""


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_document_text(db: Session, filename: str) -> str:
    """
    Return the text of the latest uploaded document
    having the given filename.
    """

    document = (
        db.execute(
            select(Document)
            .where(Document.filename == filename)
            .order_by(desc(Document.uploaded_at), desc(Document.id))
        )
        .scalars()
        .first()
    )

    if document is None:
        return ""

    chunks = (
        db.execute(
            select(Chunk.content)
            .where(Chunk.document_id == document.id)
            .order_by(Chunk.chunk_index)
        )
        .scalars()
        .all()
    )

    return "\n".join(chunks)


def get_latest_document(db: Session):
    """Return the latest uploaded document."""

    return (
        db.execute(
            select(Document)
            .order_by(desc(Document.uploaded_at), desc(Document.id))
            .limit(1)
        )
        .scalars()
        .first()
    )


def chunk_text(
    text: str,
    size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks."""

    text = text.strip()

    if not text:
        return []

    step = max(1, size - overlap)

    chunks = []

    for start in range(0, len(text), step):
        chunk = text[start:start + size].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def store_chunks(db: Session, document: str, chunks: list[str]) -> int:
    """Embed and store document chunks."""

    if not chunks:
        return 0

    embeddings = embed_texts(chunks)

    doc = Document(filename=document)
    db.add(doc)
    db.flush()

    for chunk_index, (content, embedding) in enumerate(
        zip(chunks, embeddings),
        start=1,
    ):
        db.add(
            Chunk(
                document_id=doc.id,
                chunk_index=chunk_index,
                content=content,
                embedding=embedding,
            )
        )

    # Don't commit here.
    # documents.py already commits after store_chunks() returns.

    return len(chunks)


def retrieve(db: Session, question: str, k: int = 8) -> list[str]:
    """Retrieve relevant chunks."""

    try:
        latest_doc = get_latest_document(db)

        if latest_doc is None:
            print("No document found.")
            return []

        chunks = (
            db.execute(
                select(Chunk)
                .where(Chunk.document_id == latest_doc.id)
                .order_by(Chunk.chunk_index)
            )
            .scalars()
            .all()
        )

        if not chunks:
            print("No chunks stored.")
            return []

        q_emb = embed_query(question)

        scored = []

        for chunk in chunks:
            try:
                score = chunk.embedding.cosine_distance(q_emb)
            except Exception:
                score = 0

            scored.append((score, chunk.content))

        scored.sort(key=lambda x: x[0])

        results = [content for _, content in scored[:k]]

        print("\n========== RETRIEVED CHUNKS ==========")
        print(f"Question: {question}")
        print(f"Retrieved: {len(results)} chunks")
        print("======================================\n")

        return results

    except Exception as exc:
        logging.exception(exc)
        return []


def retrieve_with_documents(db: Session, question: str, k: int = 4):
    """Retrieve the most relevant chunks along with their document information.
        This function does NOT replace retrieve().
    """

    try:
        q_emb = embed_query(question)

        latest_doc = get_latest_document(db)

        if latest_doc is None:
            return []

        rows = db.execute(
            select(
                Chunk.document_id,
                Document.filename,
                Chunk.content,
            )
            .join(Document, Chunk.document_id == Document.id)
            .where(Chunk.document_id == latest_doc.id)
            .order_by(Chunk.embedding.cosine_distance(q_emb))
            .limit(k)
        ).all()

        results = []

        for row in rows:
            results.append(
                {
                    "document_id": row.document_id,
                    "document_name": row.filename,
                    "content": row.content,
                }
            )

        return results

    except Exception as exc:
        logging.warning(
            "RAG retrieval disabled; pgvector operator unavailable: %s",
            exc,
        )
        return []
