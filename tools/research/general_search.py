"""General web search via Tavily. Returns ResearchResult with low-trust citations.

When RESEARCH_MODE=knowledge_only (default), returns a stub immediately — no network call.
Set RESEARCH_MODE=live in .env to enable Tavily.
"""

from datetime import datetime, timezone

from config import RESEARCH_MODE, TAVILY_API_KEY
from schemas.research import Citation, ResearchResult

_KNOWLEDGE_ONLY_DISCLAIMER = (
    "Research mode: knowledge_only. Web search disabled. "
    "Proceeding on model knowledge."
)


class GeneralSearch:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from tavily import TavilyClient
            self._client = TavilyClient(api_key=TAVILY_API_KEY)
        return self._client

    def search(self, query: str, max_results: int = 5) -> ResearchResult:
        if RESEARCH_MODE != "live":
            return ResearchResult(
                query=query,
                results=[],
                authoritative_citations=[],
                disclaimer=_KNOWLEDGE_ONLY_DISCLAIMER,
            )

        try:
            raw = self._get_client().search(query=query, max_results=max_results)
        except Exception as e:
            return ResearchResult(
                query=query,
                results=[],
                authoritative_citations=[],
                disclaimer=f"Web search unavailable ({e}). Proceeding on model knowledge.",
            )

        citations = []
        for r in raw.get("results", []):
            citations.append(Citation(
                source_url=r.get("url", ""),
                source_name=r.get("title", r.get("url", "")),
                source_type="general",
                retrieved_at=datetime.now(timezone.utc),
                excerpt=r.get("content", "")[:2000],
                confidence="low",
            ))

        return ResearchResult(
            query=query,
            results=citations,
            authoritative_citations=[],
            disclaimer="Results from general web search. Not verified as authoritative sources.",
        )
