"""Regulatory lookup — authoritative sources only, multi-jurisdiction.

Derives include_domains from JURISDICTION_REGISTRY for given jurisdictions.
If no result from authoritative domains: returns explicit "no authoritative source found".
Does NOT infer or fall back to general sources.
"""

from datetime import datetime, timezone

from tavily import TavilyClient

from config import TAVILY_API_KEY, get_jurisdiction_domains
from schemas.research import Citation, ResearchResult

NO_SOURCE_DISCLAIMER = (
    "No authoritative regulatory source found for this query. "
    "Do NOT infer regulatory requirements. Consult primary sources directly."
)


class RegulatoryLookup:
    def __init__(self):
        self._client = None

    def _get_client(self) -> TavilyClient:
        if self._client is None:
            self._client = TavilyClient(api_key=TAVILY_API_KEY)
        return self._client

    def search(
        self,
        query: str,
        jurisdictions: list[str] | None = None,
        max_results: int = 5,
    ) -> ResearchResult:
        """Search authoritative regulatory sources for the given jurisdictions.

        Derives include_domains from JURISDICTION_REGISTRY.
        Defaults to UAE if jurisdictions is None or empty.
        """
        domains = get_jurisdiction_domains(jurisdictions)

        raw = self._get_client().search(
            query=query,
            max_results=max_results,
            include_domains=domains,
        )

        authoritative: list[Citation] = []
        for r in raw.get("results", []):
            url = r.get("url", "")
            if any(domain in url for domain in domains):
                authoritative.append(Citation(
                    source_url=url,
                    source_name=r.get("title", url),
                    source_type="authoritative",
                    retrieved_at=datetime.now(timezone.utc),
                    excerpt=r.get("content", "")[:2000],
                    confidence="high",
                ))

        if not authoritative:
            return ResearchResult(
                query=query,
                results=[],
                authoritative_citations=[],
                disclaimer=NO_SOURCE_DISCLAIMER,
            )

        return ResearchResult(
            query=query,
            results=authoritative,
            authoritative_citations=authoritative,
        )
