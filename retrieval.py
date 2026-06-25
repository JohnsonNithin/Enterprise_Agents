from langchain_core.documents import Document

from chunking import split_documents
from ingestion import POLICIES_DIRECTORY, load_policy_documents
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RETRIEVAL_TOP_K = 3


def build_retriever(chunks: list[Document]) -> VectorStoreRetriever:
    """Build a semantic retriever from document chunks."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    return vector_store.as_retriever(
        search_kwargs={"k": RETRIEVAL_TOP_K},
    )

def retrieve_documents(question:str,retriever:VectorStoreRetriever)->list[Document]:
    """This function retrieves the relevant documents for the question asked by the user"""
    # converts the questions to embeddings and then searches for the closest matches from the embeddings inside embedding vector db
    
    return retriever.invoke(question)


def main()->None:
    """This function is the main function of the Enterprise Agent"""
    print("Enterprise Agent is running")
    documents = load_policy_documents(POLICIES_DIRECTORY)


    chunks = split_documents(documents)

    retriever = build_retriever(chunks)

    print("Semantic retriever is ready.")

    question = input("Enter your question related to the enterprise maintenance equipment: ")
    
    retrieved_documents = retrieve_documents(question,retriever)

    #NOTES:
    #retrieve_documents = the function
    #retrieved_documents = the list returned by that function
    
    for rank, document in enumerate(retrieved_documents, start=1):
        print(f"Result {rank}")
        print("Source:", document.metadata["source"])
        print("Content:", document.page_content)

if __name__=="__main__":    
    main()