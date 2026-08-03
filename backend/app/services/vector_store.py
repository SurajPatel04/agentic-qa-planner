import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import VectorStoreRetriever

from app.utils.embeddings import get_embeddings
from app.core.config import settings

logger = logging.getLogger("qa_planner.vector_store")


class VectorStoreService:
    """Qdrant-backed vector store service for QA standards & testing guidelines knowledge base."""

    def __init__(self, collection_name: str = "qa_guidelines"):
        self.collection_name = collection_name
        self.qdrant_url = settings.QDRANT_URL
        self.qdrant_api_key = settings.QDRANT_API_KEY

        if not self.qdrant_url or not self.qdrant_api_key:
            logger.warning("QDRANT_URL or QDRANT_API_KEY is not set! Qdrant vector search will fail.")

        logger.info("Initializing VectorStoreService with get_embeddings() from utils...")
        self.embeddings = get_embeddings()

        if not self.embeddings:
            logger.warning("get_embeddings() returned None. Qdrant vector search will fail.")

        # Initialize the Qdrant client
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
        )
        
        self._vectorstore: Optional[QdrantVectorStore] = None

    @property
    def vectorstore(self) -> QdrantVectorStore:
        """Lazy loads the vectorstore or ingests documents if collection is missing."""
        if self._vectorstore is None:
            # Check if collection exists
            if not self.client.collection_exists(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' not found. Ingesting docs...")
                # Create the collection explicitly if needed, or let QdrantVectorStore.from_documents do it
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                self._vectorstore = self.ingest_docs()
            else:
                logger.info(f"Collection '{self.collection_name}' exists. Loading QdrantVectorStore...")
                self._vectorstore = QdrantVectorStore(
                    client=self.client,
                    collection_name=self.collection_name,
                    embedding=self.embeddings,
                )
                
            if self._vectorstore is None:
                raise RuntimeError("Failed to load or ingest Qdrant vectorstore.")
                
        return self._vectorstore

    def ingest_docs(self, docs_dir: str = "app/docs") -> Optional[QdrantVectorStore]:
        """Loads markdown docs, extracts metadata, chunks, and creates Qdrant index."""
        resolved_docs_dir = Path(docs_dir).resolve()
        if not resolved_docs_dir.exists():
            raise FileNotFoundError(f"Documentation directory not found at: {resolved_docs_dir}")

        logger.info(f"Ingesting QA standards & guidelines from {resolved_docs_dir}...")

        # Load markdown files
        loader = DirectoryLoader(
            str(resolved_docs_dir),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        raw_documents = loader.load()

        if not raw_documents:
            logger.warning(f"No markdown documents found in {resolved_docs_dir}")
            return None

        # Split documents with adjusted chunk parameters
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "],
        )

        all_chunked_docs = []
        for raw_doc in raw_documents:
            # Enhance metadata
            filename = Path(raw_doc.metadata.get("source", "unknown.md")).name
            raw_doc.metadata["filename"] = filename
            
            # Simple domain extraction from filename
            raw_doc.metadata["domain"] = filename.replace(".md", "").replace("_", " ")

            chunks = splitter.split_documents([raw_doc])
            all_chunked_docs.extend(chunks)
            logger.info(f"{filename}\n↓\n{len(chunks)} chunks\n")

        # Build Qdrant vector store
        new_vectorstore = QdrantVectorStore.from_documents(
            documents=all_chunked_docs,
            embedding=self.embeddings,
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            collection_name=self.collection_name,
            force_recreate=True,
        )

        logger.info(f"Qdrant index successfully saved to cloud collection {self.collection_name}")

        self._vectorstore = new_vectorstore
        return self._vectorstore

    def get_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """Returns a LangChain retriever interface for the vectorstore."""
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def similarity_search(self, query: str, top_k: int = 5) -> List[Document]:
        """Searches Qdrant vectorstore for QA guidelines relevant to the query."""
        retriever = self.get_retriever(k=top_k)
        docs = retriever.invoke(query)
        return docs
