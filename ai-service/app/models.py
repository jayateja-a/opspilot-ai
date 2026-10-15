from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Analyze(StrictModel):
    incident_id: UUID
    service: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=8000)
    scenario_id: str = Field(default="", max_length=80)

class Execute(StrictModel):
    incident_id: UUID
    approval_id: UUID
    service: str = Field(min_length=1, max_length=80)
    scenario_id: str = Field(max_length=80)
    action: str = Field(max_length=80)

class RunbookInput(StrictModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    service: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1, max_length=16000)

class Hypothesis(StrictModel):
    root_cause: str = Field(min_length=1, max_length=2000)
    reasoning: str = Field(min_length=1, max_length=4000)
    confidence: float = Field(ge=0, le=1)
    evidence_ids: list[str] = Field(min_length=1, max_length=20)
    runbook_ids: list[str] = Field(min_length=1, max_length=10)

class Citation(StrictModel):
    chunk_id: str
    runbook_id: str
    title: str
    content: str
    score: float

class Recommendation(StrictModel):
    action: str
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    executable: bool
    human_approval_required: Literal[True] = True
    explanation: str

class AnalysisResult(StrictModel):
    mode: Literal["demo", "openai"]
    root_cause: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[dict]
    citations: list[Citation]
    recommendation: Recommendation
    tool_calls: list[dict]
    warnings: list[str]
