from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from rag_service import answer_question, get_rag_pipeline


app = FastAPI(title="Enterprise Maintenance AI Assistant")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


@app.on_event("startup")
def startup_event() -> None:
    """Prepare RAG pipeline once when API starts."""
    get_rag_pipeline()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest) -> dict[str, Any]:
    return answer_question(request.question)