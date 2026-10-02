import re

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_analysis_graph
from api.schemas import AnalysisRequest, AnalysisResponse
from graph.state import AnalysisState
from ingestion.clinical_trials_client import ClinicalTrialsClient
from ingestion.document_parser import DocumentParser


router = APIRouter(prefix="/analysis", tags=["Analysis"])


def extract_nct_id(query: str) -> str | None:
    """
    Extract an NCT ID from the query.

    Example:
    "Analyze clinical trial NCT04280705"
    -> "NCT04280705"
    """

    match = re.search(r"\bNCT\d{8}\b", query, re.IGNORECASE)

    if match:
        return match.group(0).upper()

    return None


@router.post("", response_model=AnalysisResponse)
async def analyze(
    request: AnalysisRequest,
    graph=Depends(get_analysis_graph),
):
    # Start with studies supplied in the request
    studies = list(request.studies)

    # ---------------------------------------------------------
    # If studies were not supplied, try to get an NCT ID
    # from the query and fetch the real clinical trial
    # ---------------------------------------------------------

    if not studies:

        nct_id = extract_nct_id(request.query)

        if not nct_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No study was provided. "
                    "Include an NCT ID such as NCT04280705 "
                    "in the query or provide studies."
                ),
            )

        # Fetch study from ClinicalTrials.gov
        async with ClinicalTrialsClient() as client:
            raw_study = await client.fetch_study(nct_id)

        if raw_study is None:
            raise HTTPException(
                status_code=404,
                detail=f"Clinical trial not found: {nct_id}",
            )

        # Parse the raw ClinicalTrials.gov response
        parser = DocumentParser()

        parsed_study = parser.parse_study(raw_study)

        if parsed_study is None:
            raise HTTPException(
                status_code=422,
                detail=f"Could not parse clinical trial: {nct_id}",
            )

        # IMPORTANT:
        # The graph expects studies to be a LIST.
        studies = [
            parsed_study.model_dump()
        ]

    # ---------------------------------------------------------
    # Build LangGraph state
    # ---------------------------------------------------------

    state: AnalysisState = {
        "query": request.query,
        "studies": studies,
        "papers": list(request.papers),
        "errors": [],
    }

    # ---------------------------------------------------------
    # Run the analysis graph
    # ---------------------------------------------------------

    try:
        result = await graph.ainvoke(state)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        ) from e

    # ---------------------------------------------------------
    # Return analysis response
    # ---------------------------------------------------------

    return AnalysisResponse(
        query=request.query,

        timeline_analysis=result.get(
            "timeline_analysis",
            {},
        ),

        track_record_analysis=result.get(
            "track_record_analysis",
            {},
        ),

        side_effect_analysis=result.get(
            "side_effect_analysis",
            {},
        ),

        missing_results_analysis=result.get(
            "missing_results_analysis",
            {},
        ),

        broken_promises_analysis=result.get(
            "broken_promises_analysis",
            {},
        ),

        pattern_analysis=result.get(
            "pattern_analysis",
            {},
        ),
            final_analysis=result.get(
        "final_analysis",
        {},
    ),
    )