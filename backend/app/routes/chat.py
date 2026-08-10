"""
routes/chat.py

Handles:
- Conversation creation/loading
- Document retrieval using RAG
- Sending document context to the LLM
- Saving user and assistant messages
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse, ResponseMessage
from app.services.llm import SYSTEM, LLMError, generate_reply
from app.services.rag import (
    retrieve,
    retrieve_with_documents,
    get_latest_document,
    get_document_text,
)

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

    question = req.message.lower().strip()

    # ---------------------------------------------------------
    # Detect summary / vague / general document questions
    # ---------------------------------------------------------

    document_overview_questions = [
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
        "important information",
        "any important information",
        "anything important",
        "important points",
        "key information",
        "key points",
        "anything useful",
        "anything specific",
        "any specific information",
        "specific information",
        "what is important",
        "what are the important points",
        "what are the key points",
    ]

    is_document_overview_question = any(
        q in question
        for q in document_overview_questions
    )

    context = ""
    retrieved_chunks = []

    # ---------------------------------------------------------
    # Get latest uploaded document
    # ---------------------------------------------------------

    from app.services.rag import (
        get_latest_document,
        get_document_text,
    )

    latest_doc = get_latest_document(db)

    # ---------------------------------------------------------
    # General / vague document questions
    # Use the complete latest document
    # ---------------------------------------------------------

    if is_document_overview_question:

        if latest_doc:
            context = get_document_text(
                db,
                latest_doc.filename,
            )

            related_documents.append(
                {
                    "id": str(latest_doc.id),
                    "name": latest_doc.filename,
                }
            )

    # ---------------------------------------------------------
    # Specific document questions
    # Use normal RAG retrieval
    # ---------------------------------------------------------

    else:

        document_keywords = [
            "document",
            "pdf",
            "file",
            "report",
            "paper",
            "topic",
            "information",
            "explain",
            "what is",
            "what are",
            "tell me about",
            "describe",
            "focus",
            "purpose",
        ]

        use_rag = any(
            keyword in question
            for keyword in document_keywords
        )

        if use_rag:

            retrieved_chunks = retrieve(
                db,
                req.message,
            )

            print("\n========== RETRIEVED CHUNKS ==========")
            print(f"RAG enabled: {use_rag}")
            print(f"Retrieved: {len(retrieved_chunks)}")
            print("=======================================\n")

            if retrieved_chunks:
                context = "\n\n".join(retrieved_chunks)

            retrieved_data = retrieve_with_documents(
                db,
                req.message,
            )

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

    # ---------------------------------------------------------
    # Fallback:
    # If RAG finds nothing, use the latest document
    # ---------------------------------------------------------

    if not context and latest_doc:

        print(
            "RAG returned no context. "
            "Falling back to latest document."
        )

        context = get_document_text(
            db,
            latest_doc.filename,
        )

        if not related_documents:

            related_documents.append(
                {
                    "id": str(latest_doc.id),
                    "name": latest_doc.filename,
                }
            )

    # ---------------------------------------------------------
    # Build prompt
    # ---------------------------------------------------------

    system = SYSTEM

    if context:

        system += """
You are Smart Support Assistant.

Your job is to answer the CURRENT USER QUESTION using the uploaded
document as the primary source.

Important rules:

1. Always answer the CURRENT question.
2. Do not simply repeat a previous assistant answer.
3. Use the uploaded document as the primary source of information.
4. If the answer is clearly available in the document, answer it
   directly and naturally.
5. If the question is vague or general, identify the most relevant
   important or specific information from the document.
6. If the user asks about something that is NOT mentioned in the
   document, do not simply say "I couldn't find that information."
   Instead, give a natural and helpful response based on what can
   reasonably be determined from the document.

For example:

User: "Does NALCO produce gold?"

If the document lists NALCO's products and gold is not among them,
respond naturally, for example:

"No. Gold is not listed as a product produced by NALCO in the
document. The document mentions products such as alumina, aluminium,
ingots, billets, wire rods, and alloy wire rods."

7. When answering a question about something not mentioned in the
   document, do NOT invent facts or use unrelated outside knowledge.
8. If the document does not provide enough information to determine
   whether something is true or false, say so naturally. For example:

"The document does not mention whether NALCO produces gold, so I
can't confirm that from the document."

9. Keep answers relevant to the user's exact question.
10. Do not unnecessarily mention that you are an AI.
11. Do not answer based on previous questions unless the CURRENT
    question clearly refers to them.
"""

        history.append(
            {
                "role": "user",
                "content": f"""
DOCUMENT CONTEXT:

{context}

CURRENT QUESTION:

{req.message}

Answer the CURRENT QUESTION using only the DOCUMENT CONTEXT.
""",
            }
        )

    else:

        history.append(
            {
                "role": "user",
                "content": req.message,
            }
        )

    # ---------------------------------------------------------
    # Generate AI response
    # ---------------------------------------------------------

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

    # Save assistant response
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
