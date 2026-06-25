from pathlib import Path
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_core.documents import Document



POLICIES_DIRECTORY = Path("data/demo_policies")

def load_policy_documents(directory:Path)->list[Document]:
    """This function loads the policy documents"""
    loader = DirectoryLoader(
        
        str(directory),
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        
        )
    return loader.load()

def main() -> None:
    """Run the Enterprise Agent document-ingestion demonstration."""
    print("Enterprise Agent is running")

    documents = load_policy_documents(POLICIES_DIRECTORY)
    
    for document in documents:
        print(document.page_content)
        print(document.metadata)

    print("----DETAILS OF LOADED DOCUMENTS----------------------")

    print(f"Loaded {len(documents)} documents.")

    print("--------------------------")

        




if __name__=="__main__":
    main()

    
