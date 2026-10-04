from datetime import datetime

from pydantic import BaseModel


class RunCreate(BaseModel):
    task: str
    status: str
    final_output: str | None = None
    failure_reason: str | None = None


class RunResponse(RunCreate):
    id: int
    created_at: datetime | None = None   # NEW

    class Config:
        from_attributes = True


class StepCreate(BaseModel):
    step_number: int
    name: str
    status: str
    input_data: str | None = None
    output_data: str | None = None
    error_message: str | None = None


class StepIngest(StepCreate):
    """What an agent POSTs. `metrics` is optional but enables the AI diagnosis."""
    metrics: dict | None = None


class StepResponse(StepCreate):
    id: int
    run_id: int
    created_at: datetime | None = None   # NEW

    class Config:
        from_attributes = True


class DiagnosisResponse(BaseModel):
    run_id: int
    failed_step_id: int
    failed_step_number: int
    failed_step_name: str
    reason: str
    evidence: list[str]
    # filled in by the AI model when step metrics exist (frontend already shows them if present)
    probability: float | None = None
    confidence: str | None = None
    probabilities: list[dict] | None = None
    method: str = "rule-based"


class ReplayCreate(BaseModel):
    start_step_number: int


class ReplayResponse(BaseModel):
    id: int
    run_id: int
    start_step_number: int
    status: str
    result: str | None = None

    class Config:
        from_attributes = True


class CheckpointCreate(BaseModel):
    step_id: int
    state_data: str


class CheckpointResponse(BaseModel):
    id: int
    run_id: int
    step_id: int
    step_number: int
    state_data: str

    class Config:
        from_attributes = True


class ComparisonResponse(BaseModel):
    run_id: int
    original_output: str
    corrected_output: str
    changed_step: int
    explanation: str
