"""KnowledgeRetriever — three-layer knowledge architecture retrieval.

Queries three ChromaDB collections:
  kb_base          — static framework knowledge (knowledge/*.md files)
  kb_user_sanitised — accumulated cross-case patterns (firm_profile/knowledge/)
  kb_engagement    — per-engagement documents (cases/{slug}/vector_index/)

Graceful fallback if any collection is empty or unavailable (ChromaDB or
sentence-transformers not installed).

BA: BA-KL-01
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_MAX_CHARS = 8000


@dataclass
class KnowledgeHit:
    doc_id: str
    filename: str
    chunk_text: str
    source_citation: str
    distance: float = 0.0
    layer: str = "base"  # "base" | "user" | "engagement"


@dataclass
class KnowledgeBundle:
    """Result from KnowledgeRetriever.retrieve().

    All three arrays are always present — empty lists if unavailable.
    """
    base_hits: list[KnowledgeHit] = field(default_factory=list)
    user_hits: list[KnowledgeHit] = field(default_factory=list)
    engagement_hits: list[KnowledgeHit] = field(default_factory=list)
    rules: dict[str, Any] = field(default_factory=dict)

    @property
    def all_hits(self) -> list[KnowledgeHit]:
        return self.base_hits + self.user_hits + self.engagement_hits

    def as_context_block(self, max_chars: int = _MAX_CHARS) -> str:
        """Format all hits as an injected context block for agent prompts."""
        if not self.all_hits:
            return ""
        lines = ["[KNOWLEDGE CONTEXT — retrieved from knowledge base]"]
        total = 0
        for hit in self.all_hits:
            block = (
                f"\nSource: {hit.source_citation} [{hit.layer}]\n"
                f"---\n{hit.chunk_text}\n---"
            )
            if total + len(block) > max_chars:
                break
            lines.append(block)
            total += len(block)
        lines.append("[END KNOWLEDGE CONTEXT]")
        return "\n".join(lines)


class KnowledgeRetriever:
    """Retrieves relevant knowledge fragments from the three-layer store.

    Falls back gracefully when ChromaDB is unavailable — returns an empty
    KnowledgeBundle so callers do not need to handle None.

    Usage:
        kr = KnowledgeRetriever(case_id="project-alpha-frm")
        bundle = kr.retrieve("AML red flags for fintech")
        context = bundle.as_context_block()
    """

    def __init__(self, case_id: Optional[str] = None) -> None:
        self.case_id = case_id
        self._available = self._check_available()

    def _check_available(self) -> bool:
        try:
            import chromadb  # noqa: F401
            import sentence_transformers  # noqa: F401
            return True
        except ImportError:
            logger.warning(
                "KnowledgeRetriever: chromadb or sentence-transformers not available — "
                "returning empty bundles."
            )
            return False

    def retrieve(self, query: str, case_context: Optional[dict] = None, top_k: int = 5) -> KnowledgeBundle:
        """Query all three knowledge layers and return a KnowledgeBundle.

        Never raises — returns empty bundle on any failure.
        """
        if not self._available:
            return KnowledgeBundle()

        try:
            return self._retrieve_inner(query, case_context or {}, top_k)
        except Exception as exc:
            logger.warning("KnowledgeRetriever.retrieve() failed: %s", exc)
            return KnowledgeBundle()

    def _retrieve_inner(self, query: str, case_context: dict, top_k: int) -> KnowledgeBundle:
        import chromadb
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        q_embedding = model.encode([query])[0].tolist()

        base_hits = self._query_collection(
            _base_client(), "kb_base", q_embedding, top_k, "base"
        )
        user_hits = self._query_collection(
            _user_client(), "kb_user_sanitised", q_embedding, top_k, "user"
        )
        engagement_hits: list[KnowledgeHit] = []
        if self.case_id:
            engagement_hits = self._query_collection(
                _engagement_client(self.case_id), f"case_{self.case_id}",
                q_embedding, top_k, "engagement"
            )

        return KnowledgeBundle(
            base_hits=base_hits,
            user_hits=user_hits,
            engagement_hits=engagement_hits,
        )

    def _query_collection(
        self,
        client: Any,
        collection_name: str,
        embedding: list[float],
        top_k: int,
        layer: str,
    ) -> list[KnowledgeHit]:
        """Query one ChromaDB collection. Returns [] on any error."""
        try:
            col = client.get_collection(collection_name)
            results = col.query(
                query_embeddings=[embedding],
                n_results=min(top_k, col.count()),
                include=["documents", "metadatas", "distances"],
            )
            hits = []
            for text, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                hits.append(KnowledgeHit(
                    doc_id=meta.get("doc_id", ""),
                    filename=meta.get("filename", ""),
                    chunk_text=text,
                    source_citation=(
                        f"{meta.get('filename', 'unknown')} — chunk {meta.get('chunk_index', 0)}"
                    ),
                    distance=float(dist),
                    layer=layer,
                ))
            return hits
        except Exception:
            return []


# ── ChromaDB client factories ─────────────────────────────────────────────────
# Each layer uses a different persistent directory so collections don't collide.

def _base_client() -> Any:
    import chromadb
    base_dir = Path(__file__).parent.parent / "firm_profile" / "knowledge" / "base"
    base_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(base_dir))


def _user_client() -> Any:
    import chromadb
    user_dir = Path(__file__).parent.parent / "firm_profile" / "knowledge" / "user"
    user_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(user_dir))


def _engagement_client(case_id: str) -> Any:
    import chromadb
    from config import CASES_DIR
    eng_dir = CASES_DIR / case_id / "vector_index"
    eng_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(eng_dir))
