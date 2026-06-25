import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from chunking import split_documents
from ingestion import POLICIES_DIRECTORY, load_policy_documents
from retrieval import build_retriever, retrieve_documents


def create_llm() -> Any:
    """Create the Groq LLM from environment configuration."""
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file before running."
        )

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    return ChatGroq(
        model=model,
        temperature=0,
        max_retries=2,
    )


def build_context(retrieved_chunks: list[Document]) -> str:
    """Convert retrieved chunks into source-labeled context text."""
    context_blocks: list[str] = []

    for index, value in enumerate(retrieved_chunks, start=1):
        source = value.metadata.get("source", "Unknown source")
        content = value.page_content.strip()

        context_blocks.append(
            f"[Source {index}: {source}]\n{content}"
        )

    return "\n\n".join(context_blocks)


def generate_llm_answer(question: str, context: str, llm: Any) -> str:
    """Use an LLM to answer the question using only the retrieved context."""
    prompt = f"""
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
{question}

Context:
{context}

Answer:
"""

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        return str(response.content).strip()

    return str(response).strip()


def answer_with_citations(
    question: str,
    retrieved_chunks: list[Document],
    llm: Any,
) -> str:
    """Create a grounded answer using retrieved chunks and an LLM."""
    if not retrieved_chunks:
        return "I do not know based on the available documents."

    context = build_context(retrieved_chunks)

    return generate_llm_answer(
        question=question,
        context=context,
        llm=llm,
    )


def main() -> None:
    """Run the RAG answer-generation flow from the terminal."""
    print("Enterprise Agent is running")

    all_documents = load_policy_documents(POLICIES_DIRECTORY)
    chunks = split_documents(all_documents)
    retriever = build_retriever(chunks)
    llm = create_llm()

    question = input("Ask a maintenance question: ")

    retrieved_chunks = retrieve_documents(question, retriever)

    answer = answer_with_citations(
        question=question,
        retrieved_chunks=retrieved_chunks,
        llm=llm,
    )

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()