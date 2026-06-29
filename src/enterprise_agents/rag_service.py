"""
`rag_service.py` is the **orchestrator**.

It connects the separate pieces into one working flow.

**Mental Model**

Each file has one job:


ingestion.py     -> load documents
chunking.py      -> split documents
retrieval.py     -> find relevant chunks
generation.py    -> create answer using LLM
guardrails.py    -> decide risk/refusal/human review
evaluation.py    -> test the whole system
```

`rag_service.py` connects them:


question
    ↓
guardrails
    ↓
retrieval
    ↓
generation
    ↓
guardrails warning
    ↓
final response


**Why `rag_service.py` Exists**

Without `rag_service.py`, FastAPI would need to call everything manually:


load docs
chunk docs
build retriever
retrieve chunks
generate answer
apply guardrails
format response


That would make `api.py` messy.

So we keep:


api.py = thin API layer
rag_service.py = business logic / orchestration layer


**What `rag_service.py` Should Do**

It should do only the connected flow:


1. Receive user question
2. Check guardrails
3. If refused, return refusal response
4. Get RAG pipeline
5. Retrieve evidence
6. Generate answer
7. Add warning if high risk
8. Extract sources
9. Return structured response


**What `rag_service.py` Should Not Do**

It should not contain all low-level logic.

Avoid putting these inside `rag_service.py`:


document loading logic
chunking logic
embedding logic details
keyword lists
FastAPI route definitions
Streamlit UI code
evaluation test loops


Those belong in separate files.

**Crux**

rag_service.py = the conductor.
Other files = the instruments.


In industry wording:


rag_service.py is the application service layer that orchestrates guardrails, retrieval, generation, and response formatting.

"""







from dataclasses import dataclass
from typing import Any

from langchain_core.documents import Document

from src.enterprise_agents.chunking import split_documents
from src.enterprise_agents.generation import answer_with_citations, create_language_model
from src.enterprise_agents.ingestion import POLICIES_DIRECTORY, load_policy_documents
from src.enterprise_agents.retrieval import build_retriever, retrieve_documents


@dataclass(frozen=True)
class RagPipeline:
    """Prepared RAG components used to answer questions."""

    retriever: Any
    language_model: Any


_PIPELINE: RagPipeline | None = None


def initialize_rag_pipeline() -> RagPipeline:
    """Load documents, create chunks, build retriever, and create LLM once."""

    # Startup Step 1: Load documents.
    loaded_policy_documents = load_policy_documents(POLICIES_DIRECTORY)

    # Startup Step 2: Split documents into retrieval chunks.
    retrieval_chunks = split_documents(loaded_policy_documents)

    # Startup Step 3: Build semantic retriever from chunks.
    semantic_retriever = build_retriever(retrieval_chunks)

    # Startup Step 4: Create language model.
    language_model = create_language_model()

    return RagPipeline(
        retriever=semantic_retriever,
        language_model=language_model,
    )


def get_rag_pipeline() -> RagPipeline:
    """Return the prepared RAG pipeline, creating it only once."""
    global _PIPELINE

    if _PIPELINE is None:
        _PIPELINE = initialize_rag_pipeline()

    return _PIPELINE


def extract_sources(evidence_chunks: list[Document]) -> list[str]:
    """Extract unique source names from retrieved evidence chunks."""
    sources: list[str] = []

    for evidence_chunk in evidence_chunks:
        source_name = evidence_chunk.metadata.get("source", "Unknown source")

        if source_name not in sources:
            sources.append(source_name)

    return sources


def answer_question(user_question: str) -> dict[str, Any]:
    """Answer a user question using the prepared RAG pipeline."""

    # Runtime Step 1: Get prepared retriever and LLM.
    rag_pipeline = get_rag_pipeline()

    # Runtime Step 2: Retrieve relevant evidence chunks.
    evidence_chunks = retrieve_documents(
        question=user_question,
        retriever=rag_pipeline.retriever,
    )

    # Runtime Step 3: Generate grounded answer from evidence.
    final_answer = answer_with_citations(
        user_question=user_question,
        evidence_chunks=evidence_chunks,
        language_model=rag_pipeline.language_model,
    )

    # Runtime Step 4: Return answer and source list.
    sources = extract_sources(evidence_chunks)

    return {
        "question": user_question,
        "answer": final_answer,
        "sources": sources,
    }


def main() -> None:
    """Run a local smoke test for the RAG service."""
    user_question = input("Ask a maintenance question: ")

    response = answer_question(user_question)

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(response["answer"])

    print()
    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in response["sources"]:
        print(f"- {source}")


if __name__ == "__main__":
    main()