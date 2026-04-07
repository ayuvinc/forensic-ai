"""Company lookup — official registries, multi-jurisdiction.

Preferred sources: government registries, Zawya, official filings.
Results not from official registries are flagged as 'unverified'.

When RESEARCH_MODE=knowledge_only (default), returns a stub immediately — no network call.
Set RESEARCH_MODE=live in .env to enable Tavily.
"""

from datetime import datetime, timezone

from config import RESEARCH_MODE, TAVILY_API_KEY, get_jurisdiction_company_domains
from schemas.research import Citation, ResearchResult

ZAWYA_DOMAIN = "zawya.com"

_KNOWLEDGE_ONLY_DISCLAIMER = (
    "Research mode: knowledge_only. Company registry lookup disabled. "
    "Verify ownership independently."
)


class CompanyLookup:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from tavily import TavilyClient
            self._client = TavilyClient(api_key=TAVILY_API_KEY)
        return self._client

    def lookup(
        self,
        company_name: str,
        jurisdictions: list[str] | None = None,
        max_results: int = 5,
    ) -> ResearchResult:
        """Look up company registration and ownership for the given jurisdictions.

        Derives official domains from JURISDICTION_REGISTRY.
        Defaults to UAE if jurisdictions is None or empty.
        """
        if RESEARCH_MODE != "live":
            return ResearchResult(
                query=f"{company_name} company registration ownership",
                results=[],
                authoritative_citations=[],
                disclaimer=_KNOWLEDGE_ONLY_DISCLAIMER,
            )

        j_list = jurisdictions or ["UAE"]
        official_domains = get_jurisdiction_company_domains(j_list)
        all_trusted = list(official_domains) + [ZAWYA_DOMAIN]

        query = f"{company_name} company registration ownership {' '.join(j_list)}"
        try:
            raw = self._get_client().search(query=query, max_results=max_results)
        except Exception as e:
            return ResearchResult(
                query=query,
                results=[],
                authoritative_citations=[],
                disclaimer=f"Company lookup unavailable ({e}). Proceed without registry data.",
            )

        results: list[Citation] = []
        authoritative: list[Citation] = []

        for r in raw.get("results", []):
            url = r.get("url", "")
            is_official = any(d in url for d in all_trusted)
            citation = Citation(
                source_url=url,
                source_name=r.get("title", url),
                source_type="authoritative" if is_official else "unverified",
                retrieved_at=datetime.now(timezone.utc),
                excerpt=r.get("content", "")[:2000],
                confidence="high" if is_official else "low",
            )
            results.append(citation)
            if is_official:
                authoritative.append(citation)

        disclaimer = None if authoritative else (
            f"No results from official registries for {', '.join(j_list)}. "
            "All sources are unverified — do not rely on this data for legal conclusions."
        )

        return ResearchResult(
            query=query,
            results=results,
            authoritative_citations=authoritative,
            disclaimer=disclaimer,
        )
