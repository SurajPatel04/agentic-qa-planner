import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import VectorStoreRetriever

from app.utils.embeddings import get_embeddings
from app.core.config import settings

logger = logging.getLogger("qa_planner.vector_store")


class VectorStoreService:
    """FAISS-backed vector store service for QA standards & testing guidelines knowledge base."""

    def __init__(self, index_dir: str = "app/data/faiss_index"):
        self.index_dir = str(Path(index_dir).resolve())

        logger.info("Initializing VectorStoreService with get_embeddings() from utils...")
        self.embeddings = get_embeddings()

        if not self.embeddings:
            logger.warning("get_embeddings() returned None. FAISS vector search will fail.")

        self._vectorstore: Optional[FAISS] = None

    @property
    def vectorstore(self) -> FAISS:
        """Lazy loads the vectorstore or ingests documents if index is missing."""
        if self._vectorstore is None:
            loaded_index = self.load_index()
            if loaded_index is None:
                self._vectorstore = self.ingest_docs()
            else:
                self._vectorstore = loaded_index
                
            if self._vectorstore is None:
                raise RuntimeError("Failed to load or ingest FAISS vectorstore.")
                
        return self._vectorstore

    def ingest_docs(self, docs_dir: str = "app/docs") -> Optional[FAISS]:
        """Loads markdown docs, extracts metadata, chunks, and creates FAISS index."""
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

        # Build FAISS vector store
        new_vectorstore = FAISS.from_documents(all_chunked_docs, self.embeddings)

        # Save to disk
        os.makedirs(self.index_dir, exist_ok=True)
        new_vectorstore.save_local(self.index_dir)
        logger.info(f"FAISS index successfully saved to {self.index_dir}")

        self._vectorstore = new_vectorstore
        return self._vectorstore

    def load_index(self) -> Optional[FAISS]:
        """Loads the FAISS vectorstore from local disk if it exists."""
        if not os.path.exists(os.path.join(self.index_dir, "index.faiss")):
            logger.info(f"No FAISS index found at {self.index_dir}.")
            return None

        try:
            loaded_vs = FAISS.load_local(
                self.index_dir,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info(f"Successfully loaded FAISS index from {self.index_dir}")
            return loaded_vs
        except Exception as e:
            logger.error(f"Failed to load FAISS index from {self.index_dir}: {e}")
            return None

    def get_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """Returns a LangChain retriever interface for the vectorstore."""
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def similarity_search(self, query: str, top_k: int = 5) -> List[Document]:
        """Searches FAISS vectorstore for QA guidelines relevant to the query."""
        retriever = self.get_retriever(k=top_k)
        docs = retriever.invoke(query)
        return docs
