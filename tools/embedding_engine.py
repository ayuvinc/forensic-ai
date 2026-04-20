"""Semantic embedding engine for document retrieval.

Wraps sentence-transformers + ChromaDB. Two-layer fallback (R-NEW-07):
  Layer 1: ImportError on sentence_transformers or chromadb → available = False
  Layer 2: First-run model download failure → available = False, log warning
Callers check engine.available before calling embed_document / retrieve.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 800       # characters per chunk
_CHUNK_OVERLAP = 80     # overlap between consecutive chunks
_MAX_CONTEXT_CHARS = 8_000  # hard cap on total retrieved context per query


@dataclass
class ChunkResult:
    chunk_text: str
    source_doc_id: str
    source_filename: str
    chunk_index: int
    source_citation: str  # formatted as "{filename}, chunk {n}"


class EmbeddingEngine:
    """Per-case semantic embedding and retrieval engine.

    Usage:
        engine = EmbeddingEngine("my-case-id")
        if engine.available:
            engine.embed_document(doc_entry)
            results = engine.retrieve("fraud indicators")
        else:
            # fall back to full-document context
    """

    def __init__(self, case_id: str) -> None:
        self.case_id = case_id
        self.available = False
        self._collection = None
        self._model = None

        try:
            import sentence_transformers  # noqa: F401
            import chromadb              # noqa: F401
        except ImportError:
            logger.warning(
                "EmbeddingEngine unavailable — sentence-transformers or chromadb not installed. "
                "Install with: pip install sentence-transformers chromadb"
            )
            return

        self._init_store()

    def _init_store(self) -> None:
        """Initialise ChromaDB collection and load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as exc:
            # First-run model download failure (R-NEW-07)
            logger.warning(
                f"EmbeddingEngine: model load failed — falling back to full-document context. "
                f"Error: {exc}"
            )
            return

        try:
            import chromadb
            db_path = Path("cases") / self.case_id / ".chromadb"
            db_path.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(db_path))
            # ChromaDB collection names must be alphanumeric — sanitise case_id
            safe_name = "".join(c if c.isalnum() else "_" for c in self.case_id)[:63] or "default"
            self._collection = client.get_or_create_collection(safe_name)
            self.available = True
        except Exception as exc:
            logger.warning(f"EmbeddingEngine: ChromaDB init failed: {exc}")

    # ── Chunking ───────────────────────────────────────────────────────────────

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks of _CHUNK_SIZE characters."""
        if not text:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            chunks.append(text[start : start + _CHUNK_SIZE])
            start += _CHUNK_SIZE - _CHUNK_OVERLAP
        return chunks

    # ── Indexing ───────────────────────────────────────────────────────────────

    def embed_document(self, doc_entry) -> None:
        """Chunk and embed a document into the case vector store.

        doc_entry may be a dataclass, Pydantic model, or plain dict with keys:
        doc_id, filename, content.  No-op if engine is unavailable.
        """
        if not self.available or self._collection is None or self._model is None:
            return

        def _get(obj, key: str, default=""):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        doc_id   = _get(doc_entry, "doc_id")
        filename = _get(doc_entry, "filename")
        content  = _get(doc_entry, "content")

        if not content:
            return

        chunks = self._chunk_text(content)
        if not chunks:
            return

        embeddings = self._model.encode(chunks).tolist()
        ids        = [f"{doc_id}__chunk_{i}" for i in range(len(chunks))]
        metadatas  = [
            {"doc_id": doc_id, "filename": filename, "chunk_index": i}
            for i in range(len(chunks))
        ]

        # Upsert — safe if document is re-registered
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

    def chunk_count(self, doc_id: str) -> int:
        """Return number of chunks stored for doc_id. Returns 0 if unavailable."""
        if not self.available or self._collection is None:
            return 0
        try:
            results = self._collection.get(where={"doc_id": doc_id}, include=[])
            return len(results.get("ids", []))
        except Exception:
            return 0

    # ── Retrieval ──────────────────────────────────────────────────────────────

    def retrieve(
        self, query: str, case_id: str | None = None, top_k: int = 5
    ) -> list[ChunkResult]:
        """Return top-k semantically similar chunks for a query.

        Returns empty list if unavailable — callers must fall back to
        full-document context.  Total context capped at _MAX_CONTEXT_CHARS.
        """
        if not self.available or self._collection is None or self._model is None:
            return []

        try:
            count = self._collection.count()
            if count == 0:
                return []

            query_embedding = self._model.encode([query]).tolist()
            results = self._collection.query(
                query_embeddings=query_embedding,
                n_results=min(top_k, count),
            )
        except Exception as exc:
            logger.warning(f"EmbeddingEngine.retrieve failed: {exc}")
            return []

        chunk_results: list[ChunkResult] = []
        total_chars = 0

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for doc_text, meta in zip(documents, metadatas):
            if total_chars + len(doc_text) > _MAX_CONTEXT_CHARS:
                break
            chunk_idx = meta.get("chunk_index", 0)
            filename  = meta.get("filename", "unknown")
            chunk_results.append(ChunkResult(
                chunk_text=doc_text,
                source_doc_id=meta.get("doc_id", ""),
                source_filename=filename,
                chunk_index=chunk_idx,
                source_citation=f"{filename}, chunk {chunk_idx + 1}",
            ))
            total_chars += len(doc_text)

        return chunk_results

    def get_context_for_query(self, query: str, max_chars: int = _MAX_CONTEXT_CHARS) -> str:
        """Return a formatted context string from top retrieved chunks.

        Returns empty string if unavailable — caller falls back to
        full DocumentManager content.
        """
        chunks = self.retrieve(query)
        if not chunks:
            return ""

        parts: list[str] = []
        total = 0
        for chunk in chunks:
            block = f"[{chunk.source_citation}]\n{chunk.chunk_text}"
            if total + len(block) > max_chars:
                break
            parts.append(block)
            total += len(block)

        return "\n\n".join(parts)
