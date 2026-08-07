from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import Base, engine
from app import models
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router
from app.routes.feature import router as feature_router
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()


# Import models BEFORE create_all()


app = FastAPI(
    title="Smart Support Assistant",
    description="API for AI-powered customer support",
    version="1.0.0",
)

# -----------------------------
# Database Initialization
# -----------------------------
with engine.begin() as conn:
    # Enable pgvector
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

# Create all tables first
Base.metadata.create_all(bind=engine)

# Optional schema updates
with engine.begin() as conn:
    conn.execute(text("""
    DO $$
    BEGIN

        -- Add created_at to document_chunks if missing
        IF EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema='public'
              AND table_name='document_chunks'
        ) THEN

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema='public'
                  AND table_name='document_chunks'
                  AND column_name='created_at'
            ) THEN
                ALTER TABLE public.document_chunks
                ADD COLUMN created_at TIMESTAMP DEFAULT now();
            END IF;

        END IF;

        -- Add uploaded_at to documents if missing
        IF EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema='public'
              AND table_name='documents'
        ) THEN

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema='public'
                  AND table_name='documents'
                  AND column_name='uploaded_at'
            ) THEN
                ALTER TABLE public.documents
                ADD COLUMN uploaded_at TIMESTAMP DEFAULT now();
            END IF;

        END IF;

    END
    $$;
    """))

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Health Check
# -----------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Routes
# -----------------------------
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(feature_router)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
