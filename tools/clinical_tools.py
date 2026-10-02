from typing import Any

from ingestion.clinical_trials_client import ClinicalTrialsClient


class ClinicalTools:
    """Tools for retrieving clinical trial information."""

    async def search_trials(
        self,
        query: str,
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """Search ClinicalTrials.gov for trials."""

        async with ClinicalTrialsClient() as client:
            return await client.search_studies(
                condition=query,
                max_results=page_size,
            )

    async def get_trial(
        self,
        nct_id: str,
    ) -> dict[str, Any] | None:
        """Retrieve a specific clinical trial."""

        async with ClinicalTrialsClient() as client:
            return await client.fetch_study(nct_id)