from typing import Any

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    query: str = Field(..., min_length=1)
    nct_id: str | None = None
    studies: list[dict[str, Any]] = Field(default_factory=list)
    papers: list[dict[str, Any]] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    query: str
    timeline_analysis: dict[str, Any] = Field(default_factory=dict)
    track_record_analysis: dict[str, Any] = Field(default_factory=dict)
    side_effect_analysis: dict[str, Any] = Field(default_factory=dict)
    missing_results_analysis: dict[str, Any] = Field(default_factory=dict)
    broken_promises_analysis: dict[str, Any] = Field(default_factory=dict)
    pattern_analysis: dict[str, Any] = Field(default_factory=dict)
    final_analysis: dict[str, Any] = Field(default_factory=dict)


class ReviewRequest(BaseModel):
    analysis: dict[str, Any]
    approved: bool = False
    feedback: str = ""


class ReviewResponse(BaseModel):
    approved: bool
    feedback: str
    analysis: dict[str, Any]
    status: str