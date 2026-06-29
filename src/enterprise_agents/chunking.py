from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.enterprise_agents.ingestion import POLICIES_DIRECTORY, load_policy_documents


CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

def split_documents(documents: list[Document]) -> list[Document]:

    """Split documents into chunks of CHUNK_SIZE with CHUNK_OVERLAP."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n"],
        keep_separator=True,
    )
    chunks_ = splitter.split_documents(documents)
    return chunks_   


def main()-> None:
    """This function is the main function of the Enterprise Agent"""
    print("Enterprise Agent is running")
    documents = load_policy_documents(POLICIES_DIRECTORY)
    chunks = split_documents(documents)
    print(chunks[0].page_content), print(len(chunks))
    # for chunk in chunks:
    #     print(chunk.page_content)
    #     print(chunk.metadata)

if __name__=="__main__":   
    main()