import logging
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    RAG Vector Knowledge Base integrating ChromaDB for semantic document chunking,
    vector embedding storage, and similarity retrieval. Includes clean fallback
    to keyword scoring when running offline without ChromaDB.
    """
    def __init__(self):
        self.settings = get_settings()
        self.collection = None
        self._init_chroma()

    def _init_chroma(self) -> None:
        """Initialize connection to ChromaDB vector store or fallback client."""
        try:
            # Try connecting to external ChromaDB HTTP server if configured
            if self.settings.chroma_host != "localhost":
                client = chromadb.HttpClient(
                    host=self.settings.chroma_host,
                    port=self.settings.chroma_port,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
            else:
                # Use local persistent storage inside the workspace for zero-setup local dev
                client = chromadb.PersistentClient(
                    path="./chroma_data",
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
            self.collection = client.get_or_create_collection(
                name=self.settings.chroma_collection,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB vector store collection '%s' initialized cleanly.", self.settings.chroma_collection)
        except Exception as exc:
            logger.warning("Could not initialize external ChromaDB (%s). Using ephemeral in-memory client.", exc)
            try:
                client = chromadb.Client(ChromaSettings(anonymized_telemetry=False))
                self.collection = client.get_or_create_collection(name=self.settings.chroma_collection)
            except Exception as inner_exc:
                logger.error("Failed to initialize fallback ChromaDB client: %s", inner_exc)
                self.collection = None

    def chunk(self, text: str, size: int = 800, overlap: int = 100) -> List[str]:
        """
        Split document text into overlapping chunks suitable for vector embedding.
        """
        if not text or len(text.strip()) == 0:
            return []
        chunks = []
        step = max(1, size - overlap)
        for i in range(0, len(text), step):
            chunk_str = text[i:i + size].strip()
            if chunk_str:
                chunks.append(chunk_str)
        return chunks

    async def add_document(self, doc_id: int, filename: str, content: str) -> int:
        """
        Chunk document text and index chunks inside ChromaDB vector store.
        """
        chunks = self.chunk(content)
        if not chunks:
            return 0

        if self.collection is not None:
            try:
                ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [{"doc_id": doc_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]
                # ChromaDB default embedding function automatically computes vector embeddings for documents
                self.collection.add(
                    documents=chunks,
                    ids=ids,
                    metadatas=metadatas
                )
                logger.info("Indexed %d chunks for document ID %d into ChromaDB.", len(chunks), doc_id)
            except Exception as exc:
                logger.error("Error indexing chunks into ChromaDB: %s", exc)

        return len(chunks)

    async def retrieve(self, query: str, fallback_documents: Optional[List[Any]] = None, top_k: int = 3) -> str:
        """
        Perform semantic similarity search against ChromaDB.
        Falls back to keyword scoring against database documents if ChromaDB collection is empty.
        """
        if self.collection is not None:
            try:
                count = self.collection.count()
                if count > 0:
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=min(top_k, count)
                    )
                    documents = results.get("documents", [[]])[0]
                    if documents:
                        return "\n\n---\n\n".join(documents)[:2000]
            except Exception as exc:
                logger.warning("ChromaDB vector query failed: %s. Using fallback retrieval.", exc)

        # Fallback keyword scoring against relational database knowledge documents
        if fallback_documents:
            terms = set(query.lower().split())
            ranked = sorted(
                fallback_documents,
                key=lambda d: len(terms.intersection(d.content.lower().split())),
                reverse=True
            )
            if ranked:
                return ranked[0].content[:1500]

        return "No knowledge documents have been uploaded yet or no matching context found."
