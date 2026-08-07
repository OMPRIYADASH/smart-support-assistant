"""
routes/chat.py

The route orchestrates:
- Load conversation
- Retrieve relevant document chunks (RAG)
- Send context to Gemini
- Save conversation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse, ResponseMessage
from app.services.llm import SYSTEM, LLMError, generate_reply
from app.services.rag import retrieve, retrieve_with_documents


router = APIRouter()


@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db)):
    conversations = (
        db.execute(
            select(Conversation).order_by(desc(Conversation.created_at))
        )
        .scalars()
        .all()
    )

    result = []

    for conv in conversations:
        first_message = (
            db.execute(
                select(Message.content)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at)
                .limit(1)
            )
            .scalar_one_or_none()
        )

        result.append(
            {
                "id": str(conv.id),
                "title": first_message[:40] if first_message else "New Chat",
                "created_at": conv.created_at,
            }
        )

    return result


@router.get("/chat/{conversation_id}")
def get_chat_history(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    messages = (
        db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        .scalars()
        .all()
    )

    return [
        {
            "role": msg.role,
            "content": msg.content,
        }
        for msg in messages
    ]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        conv = crud.get_or_create_conversation(
            db,
            req.conversation_id,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation_id",
        )

    except LookupError:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # Save user message
    crud.save_message(
        db,
        conv.id,
        "user",
        req.message,
    )

    # Load conversation history

    history = crud.load_history(
        db,
        conv.id,
    )
    related_documents = []

    question = req.message.lower()

    document_questions = [
        "summary",
        "summarize",
        "overview",
        "about this document",
        "about this pdf",
        "what is this pdf",
        "what is this document",
        "tell me about this pdf",
        "tell me about this document",
        "explain this pdf",
        "explain this document",
    ]

    if any(q in question for q in document_questions):

        from app.services.rag import (
            get_latest_document,
            get_document_text,
        )

        latest_doc = get_latest_document(db)

        if latest_doc:
            context = get_document_text(
                db,
                latest_doc.filename,
            )
        else:
            context = ""

    else:
        # Existing retrieval (kept for answer generation)
        document_keywords = [
            "document",
            "pdf",
            "file",
            "summary",
            "summarize",
            "explain",
            "what is in",
            "tell me about",
        ]

    use_rag = any(
        keyword in req.message.lower()
        for keyword in document_keywords
    )

    retrieved_chunks = retrieve(db, req.message)

    print("\n========== RETRIEVED CHUNKS ==========")
    print(retrieved_chunks)
    print("=====================================\n")

    if len(retrieved_chunks) >= 2:
        context = "\n\n".join(retrieved_chunks)
    else:
        context = ""

    # New retrieval with document information
    retrieved_data = retrieve_with_documents(db, req.message)

    related_documents = []

    seen = set()

    for item in retrieved_data:
        if item["document_id"] not in seen:
            seen.add(item["document_id"])

            related_documents.append(
                {
                    "id": str(item["document_id"]),
                    "name": item["document_name"],
                }
            )

    system = SYSTEM

    if len(retrieved_chunks) > 0:

        system += """

You are Smart Support Assistant.

You answer ONLY using the uploaded document.

Rules:

- Never say you cannot access the document.
- Never ask the user to upload it again.
- Use ONLY the DOCUMENT below.
- If the answer is not present, reply exactly:

"I couldn't find that information in the uploaded document."

"""

        history[-1]["content"] = f"""

print("\n========== CONTEXT ==========")
print(context)
print("================================\n")
DOCUMENT:

{context}

-------------------------

QUESTION:

{req.message}

Answer ONLY from the DOCUMENT.
"""

    try:
        reply = generate_reply(
            history=history,
            system=system,
        )

    except LLMError:
        db.rollback()

        raise HTTPException(
            status_code=502,
            detail="Assistant unavailable, please retry",
        )

    crud.save_message(
        db,
        conv.id,
        "assistant",
        reply,
    )

    db.commit()

    return ChatResponse(
        user=ResponseMessage(
            role="user",
            content=req.message,
        ),
        reply=reply,
        conversation_id=str(conv.id),
        related_documents=related_documents,
    )
