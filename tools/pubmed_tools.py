from typing import Any

from ingestion.pubmed_client import PubMedClient


class PubMedTools:
    """Tools for retrieving research papers from PubMed."""

    async def search_papers(
        self,
        query: str,
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Search PubMed for papers.

        The current PubMedClient is designed around clinical-trial
        references, so this method searches PubMed using the supplied
        query as an NCT/trial reference.
        """

        async with PubMedClient() as client:
            return await client.fetch_papers_for_trial(
                nct_id=query,
                max_results=max_results,
            )

    async def get_paper(
        self,
        pmid: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve a specific PubMed paper.

        The current PubMedClient does not expose a direct PMID lookup.
        Therefore this method is not directly supported yet.
        """

        raise NotImplementedError(
            "Direct PMID lookup is not implemented in PubMedClient yet."
        )

    async def search_by_nct(
        self,
        nct_id: str,
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """Find PubMed papers referencing a clinical trial."""

        async with PubMedClient() as client:
            return await client.fetch_papers_for_trial(
                nct_id=nct_id,
                max_results=max_results,
            )

    async def search_by_ncts(
        self,
        nct_ids: list[str],
        max_per_trial: int = 20,
    ) -> dict[str, list[dict[str, Any]]]:
        """Find PubMed papers for multiple clinical trials."""

        async with PubMedClient() as client:
            return await client.fetch_papers_for_trials(
                nct_ids=nct_ids,
                max_per_trial=max_per_trial,
            )