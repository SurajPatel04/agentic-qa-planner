import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.vector_store import VectorStoreService


def main():
    print("Initializing FAISS Vector Store ingestion...")
    service = VectorStoreService()
    try:
        vectorstore = service.ingest_docs(docs_dir="app/docs")
        if vectorstore:
            print("Successfully built and saved FAISS index for QA knowledge base!")
        else:
            print("Ingestion returned empty vectorstore.")
    except Exception as e:
        print(f"Error during vector store ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
