from typing import Any

import httpx


class SearchTools:
    """General web search tool."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Perform a web search.

        This is a lightweight search interface that can later
        be connected to a dedicated search provider.
        """
        if not query.strip():
            return []

        # Placeholder until a search provider/API is configured.
        return [
            {
                "title": f"Search query: {query}",
                "url": "",
                "snippet": "Search provider not configured yet.",
            }
        ][:max_results]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()