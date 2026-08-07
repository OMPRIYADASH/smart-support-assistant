import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import UploadResponse
from app.services.llm import (
    generate_summary,
    generate_suggestions,
)
from app.services.rag import chunk_text, store_chunks

router = APIRouter(prefix="/documents", tags=["documents"])


def extract_text(filename: str, raw: bytes) -> str:
    """Extract plain text from PDF or TXT files."""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    return raw.decode("utf-8", errors="ignore")


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile, db: Session = Depends(get_db)):
    print("Uploading:", file.filename)

    raw = await file.read()
    print("File size:", len(raw))

    text = extract_text(file.filename, raw)
    print("Text length:", len(text))

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text")

    # -----------------------------
    # Generate AI Summary
    # -----------------------------
    try:
        print("Generating AI summary...")
        summary = generate_summary(text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Summary generation failed:", repr(e))
        summary = ""
    # -----------------------------
    # Generate Suggested Questions
    # -----------------------------
    try:
        print("Generating suggested questions...")
        suggestions = generate_suggestions(text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Suggestion generation failed:", repr(e))
        suggestions = []

    # -----------------------------
    # Chunk the document
    # -----------------------------
    chunks = chunk_text(text)
    print("Chunks:", len(chunks))

    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text")

    # -----------------------------
    # Store document
    # -----------------------------
    count = store_chunks(db, file.filename, chunks)
    print("Stored:", count)

    db.commit()
    print("Commit successful")

    return UploadResponse(
        filename=file.filename,
        chunks=count,
        summary=summary,
        suggestions=suggestions,
    )


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    documents = (
        db.execute(
            select(Document).order_by(Document.uploaded_at.desc())
        )
        .scalars()
        .all()
    )

    return [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "uploaded_at": doc.uploaded_at,
        }
        for doc in documents
    ]
