"""Firm-level knowledge base embedding and retrieval engine (Sprint-KB-01).

Indexes all knowledge/ .md files into a firm-wide ChromaDB persistent store at
firm_profile/knowledge/.chromadb — separate from per-case EmbeddingEngine.

Three public methods:
  index_all()      — walk knowledge/, chunk, embed, upsert (idempotent)
  search(...)      — retrieve formatted context string (returns "" on fallback)
  needs_reindex()  — mtime check against last-indexed timestamp

Available = False when sentence-transformers or chromadb are not installed.
All methods are safe to call when unavailable.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_CHUNK_SIZE    = 500   # characters per chunk — smaller than case docs for precision
_CHUNK_OVERLAP = 50    # overlap between consecutive chunks
_KNOWLEDGE_DIR = Path("knowledge")
_DB_PATH       = Path("firm_profile") / "knowledge" / ".chromadb"
_TIMESTAMP_FILE = Path("firm_profile") / "knowledge" / ".last_indexed"
_COLLECTION_NAME = "firm_knowledge"
_MAX_RESULT_CHARS = 6_000  # raw cap before orchestrator slices to 3000/1500

# Maps orchestrator workflow names → knowledge/ subdirectory names for filtered search.
# Workflows not in this map (e.g. training, client_proposal) get unfiltered search.
_WORKFLOW_TO_DOMAIN: dict[str, str | None] = {
    "frm_risk_register":    "frm",
    "investigation_report": "investigation",
    "due_diligence":        "due_diligence",
    "due_diligence_report": "due_diligence",
    "sanctions_screening":  "sanctions_screening",
    "transaction_testing":  "transaction_testing",
    "policy_sop":           "policy_sop",
    "training":             None,
    "client_proposal":      None,
}


class FirmKnowledgeEngine:
    """Firm-wide knowledge base: semantic search across knowledge/ .md files.

    Usage:
        engine = FirmKnowledgeEngine()
        if engine.available and engine.needs_reindex():
            engine.index_all()
        context = engine.search("DFSA enforcement investigation UAE", workflow_type="investigation_report")
    """

    def __init__(self) -> None:
        self.available = False
        self._collection = None
        self._model = None

        try:
            import sentence_transformers  # noqa: F401
            import chromadb              # noqa: F401
        except ImportError:
            logger.warning(
                "FirmKnowledgeEngine unavailable — sentence-transformers or chromadb not installed. "
                "Install with: pip install sentence-transformers chromadb"
            )
            return

        self._init_store()

    def _init_store(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as exc:
            logger.warning(f"FirmKnowledgeEngine: model load failed — {exc}")
            return

        try:
            import chromadb
            _DB_PATH.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(_DB_PATH))
            self._collection = client.get_or_create_collection(_COLLECTION_NAME)
            self.available = True
        except Exception as exc:
            logger.warning(f"FirmKnowledgeEngine: ChromaDB init failed — {exc}")

    # ── Public API ──────────────────────────────────────────────────────────────

    def index_all(self) -> None:
        """Walk knowledge/ and upsert all .md files into ChromaDB.

        Idempotent — upsert overwrites existing chunks by ID.
        Called once at app startup in a background thread.
        """
        if not self.available or self._collection is None or self._model is None:
            return

        md_files = list(_KNOWLEDGE_DIR.rglob("*.md"))
        if not md_files:
            return

        indexed = 0
        for md_file in md_files:
            try:
                text = md_file.read_text(encoding="utf-8")
                if not text.strip():
                    continue
                # Derive domain from first subdirectory under knowledge/
                rel_parts = md_file.relative_to(_KNOWLEDGE_DIR).parts
                domain = rel_parts[0] if len(rel_parts) > 1 else "general"
                self._upsert_file(md_file, text, domain)
                indexed += 1
            except Exception as exc:
                logger.warning(f"FirmKnowledgeEngine: skipping {md_file} — {exc}")

        _TIMESTAMP_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TIMESTAMP_FILE.write_text(str(time.time()), encoding="utf-8")
        logger.info(f"FirmKnowledgeEngine: indexed {indexed} knowledge files")

    def search(
        self,
        query: str,
        workflow_type: str | None = None,
        top_k: int = 5,
    ) -> str:
        """Return formatted text of the top-k most relevant chunks.

        Returns "" if unavailable or no results — callers must handle gracefully.
        workflow_type filters results to the matching knowledge subdirectory.
        """
        if not self.available or self._collection is None or self._model is None:
            return ""

        try:
            count = self._collection.count()
            if count == 0:
                return ""

            query_embedding = self._model.encode([query]).tolist()
            where = self._build_where_filter(workflow_type)
            query_kwargs: dict = {
                "query_embeddings": query_embedding,
                "n_results": min(top_k, count),
            }
            if where:
                query_kwargs["where"] = where

            results = self._collection.query(**query_kwargs)
        except Exception as exc:
            logger.warning(f"FirmKnowledgeEngine.search failed — {exc}")
            return ""

        documents = results.get("documents", [[]])[0]
        metadatas  = results.get("metadatas",  [[]])[0]

        parts: list[str] = []
        total = 0
        for doc_text, meta in zip(documents, metadatas):
            if total + len(doc_text) > _MAX_RESULT_CHARS:
                break
            source = Path(meta.get("filename", "knowledge base")).name
            parts.append(f"[{source}]\n{doc_text}")
            total += len(doc_text)

        return "\n\n".join(parts)

    def needs_reindex(self) -> bool:
        """Return True if any knowledge/ .md file is newer than the last index run."""
        if not self.available:
            return False

        if not _TIMESTAMP_FILE.exists():
            return True

        try:
            last_indexed = float(_TIMESTAMP_FILE.read_text(encoding="utf-8").strip())
        except Exception:
            return True

        for md_file in _KNOWLEDGE_DIR.rglob("*.md"):
            if md_file.stat().st_mtime > last_indexed:
                return True

        return False

    # ── Internal ────────────────────────────────────────────────────────────────

    def _build_where_filter(self, workflow_type: str | None) -> dict | None:
        """Translate orchestrator workflow name to ChromaDB where clause."""
        if not workflow_type:
            return None
        domain = _WORKFLOW_TO_DOMAIN.get(workflow_type)
        if domain is None:
            return None  # unknown workflow or explicitly unmapped — no filter
        return {"workflow_type": domain}

    def _upsert_file(self, md_file: Path, text: str, domain: str) -> None:
        chunks = self._chunk_text(text)
        if not chunks or self._model is None:
            return

        embeddings = self._model.encode(chunks).tolist()
        filename = str(md_file)
        ids = [f"{filename}__chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {"workflow_type": domain, "filename": filename, "chunk_index": i}
            for i in range(len(chunks))
        ]
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

    @staticmethod
    def _chunk_text(text: str) -> list[str]:
        if not text:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            chunks.append(text[start: start + _CHUNK_SIZE])
            start += _CHUNK_SIZE - _CHUNK_OVERLAP
        return chunks
