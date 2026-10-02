import asyncio

from ingestion.clinical_trials_client import ClinicalTrialsClient
from ingestion.document_parser import DocumentParser


async def main():
    async with ClinicalTrialsClient() as client:
        raw = await client.fetch_study("NCT04280705")

        print("RAW STUDY:", raw is not None)

        parser = DocumentParser()
        study = parser.parse_study(raw)

        print("PARSED:", study is not None)

        if study:
            print("NCT ID:", study.nct_id)
            print("TITLE:", study.title)
            print("STATUS:", study.status)
            print("CONDITIONS:", study.conditions)
            print("INTERVENTIONS:", study.interventions)
            print("RESULTS POSTED:", study.results_posted)


asyncio.run(main())