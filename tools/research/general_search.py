"""General web search via Tavily. Returns ResearchResult with low-trust citations."""

from datetime import datetime, timezone

from tavily import TavilyClient

from config import TAVILY_API_KEY
from schemas.research import Citation, ResearchResult


class GeneralSearch:
    def __init__(self):
        self._client = None

    def _get_client(self) -> TavilyClient:
        if self._client is None:
            self._client = TavilyClient(api_key=TAVILY_API_KEY)
        return self._client

    def search(self, query: str, max_results: int = 5) -> ResearchResult:
        raw = self._get_client().search(query=query, max_results=max_results)
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
