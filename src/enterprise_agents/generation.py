import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from src.enterprise_agents.chunking import split_documents
from src.enterprise_agents.ingestion import POLICIES_DIRECTORY, load_policy_documents
from src.enterprise_agents.retrieval import build_retriever, retrieve_documents


def create_language_model() -> Any:
    """Create the Groq language model from environment variables."""
    load_dotenv()

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    groq_model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    language_model = ChatGroq(
        model=groq_model_name,
        temperature=0,
        max_retries=2,
    )

    return language_model


def build_evidence_context(evidence_chunks: list[Document]) -> str:
    """Convert retrieved evidence chunks into source-labeled context text."""
    evidence_blocks: list[str] = []

    for source_number, evidence_chunk in enumerate(evidence_chunks, start=1):
        source_name = evidence_chunk.metadata.get("source", "Unknown source")
        source_content = evidence_chunk.page_content.strip()

        evidence_block = (
            f"[Source {source_number}: {source_name}]\n"
            f"{source_content}"
        )

        evidence_blocks.append(evidence_block)

    evidence_context = "\n\n".join(evidence_blocks)

    return evidence_context


def generate_grounded_answer(
    user_question: str,
    evidence_context: str,
    language_model: Any,
) -> str:
    """Use the LLM to answer the user question using only evidence context."""
    rag_prompt = f"""
You are an internal maintenance knowledge assistant.

Answer the user's question using only the context below.

Rules:
- Use only the provided context.
- If the context does not contain the answer, say:
  "I do not know based on the available documents."
- Keep the answer clear and practical.
- Mention the source references that support the answer.
- Do not invent maintenance actions.
- Do not recommend actions outside the user's authorization.
- Remind the user to verify cited sources before taking maintenance action.

Question:
{user_question}

Context:
{evidence_context}

Answer:
"""

    llm_response = language_model.invoke(rag_prompt)

    if hasattr(llm_response, "content"):
        final_answer = str(llm_response.content).strip()
    else:
        final_answer = str(llm_response).strip()

    return final_answer


def answer_with_citations(
    user_question: str,
    evidence_chunks: list[Document],
    language_model: Any,
) -> str:
    """Create a grounded answer from retrieved evidence chunks."""
    if not evidence_chunks:
        return "I do not know based on the available documents."

    evidence_context = build_evidence_context(evidence_chunks)

    final_answer = generate_grounded_answer(
        user_question=user_question,
        evidence_context=evidence_context,
        language_model=language_model,
    )

    return final_answer


def main() -> None:
    """Run the RAG answer-generation flow from the terminal."""
    print("Enterprise Agent is running")

    # Phase 1: Load policy documents.
    loaded_policy_documents = load_policy_documents(POLICIES_DIRECTORY)

    # Phase 2: Split loaded documents into retrieval chunks.
    retrieval_chunks = split_documents(loaded_policy_documents)

    # Phase 3: Build semantic retriever from chunks.
    semantic_retriever = build_retriever(retrieval_chunks)

    # Phase 4: Create the LLM.
    language_model = create_language_model()

    # Phase 5: Receive user question.
    user_question = input("Ask a maintenance question: ")

    # Phase 6: Retrieve evidence chunks for this question.
    evidence_chunks = retrieve_documents(
        question=user_question,
        retriever=semantic_retriever,
    )

    # Phase 7: Generate final grounded answer.
    final_answer = answer_with_citations(
        user_question=user_question,
        evidence_chunks=evidence_chunks,
        language_model=language_model,
    )

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(final_answer)


if __name__ == "__main__":
    main()