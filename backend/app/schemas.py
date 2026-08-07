from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None


class ResponseMessage(BaseModel):
    role: str
    content: str


class RelatedDocument(BaseModel):
    id: str
    name: str


class ChatResponse(BaseModel):
    user: ResponseMessage
    reply: str
    conversation_id: UUID
    related_documents: List[RelatedDocument] = []


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    summary: str
    suggestions: List[str]


class DocumentInfo(BaseModel):
    filename: str
    chunks: int


class SummaryRequest(BaseModel):
    document: str


class SummaryResponse(BaseModel):
    summary: str
    key_points: List[str]
