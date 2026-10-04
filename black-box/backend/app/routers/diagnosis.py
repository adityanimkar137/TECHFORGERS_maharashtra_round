from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
import json
import os
import sys

from ..models import Run, Step, StepMetric
from ..schemas import DiagnosisResponse

# The AI model lives in black-box/ai-model. Import it lazily so the backend
# still starts (and falls back to rule-based diagnosis) if it is unavailable.
AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ai-model"))


def _ai_diagnose(db, run_id, steps):
    """Return a DiagnosisResponse from the AI model, or None if it can't be used."""
    rows = db.query(StepMetric).filter(StepMetric.run_id == run_id).all()
    by_num = {r.step_number: json.loads(r.data) for r in rows}
    if not steps or any(s.step_number not in by_num for s in steps):
        return None                      # this run has no metrics -> use the rule-based fallback
    try:
        if AI_DIR not in sys.path:
            sys.path.append(AI_DIR)
        from blackbox_ai import diagnose_steps, has_metrics
        ai_steps = [by_num[s.step_number] for s in steps]
        if not all(has_metrics(m) for m in ai_steps):
            return None
        out = diagnose_steps(ai_steps)
    except Exception as e:               # never take the API down because of the model
        print("AI diagnosis unavailable, using fallback:", e)
        return None
    k = out["suspect"]
    s = steps[k]
    return DiagnosisResponse(
        run_id=run_id,
        failed_step_id=s.id,
        failed_step_number=s.step_number,
        failed_step_name=s.name,
        reason=(f"Step {s.step_number} ('{s.name}') is the most likely root cause. The learned model "
                f"ranks it highest after comparing every step against normal successful runs."),
        evidence=out["evidence"],
        probability=out["shares"][k],
        confidence=out["confidence"],
        probabilities=[{"step": f"Step {st.step_number}", "name": st.name,
                        "probability": out["shares"][i]} for i, st in enumerate(steps)],
        method="ai-model",
    )


router = APIRouter(
    prefix="/runs/{run_id}/diagnose",
    tags=["Diagnosis"]
)


@router.post("/", response_model=DiagnosisResponse)
def diagnose_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    # Check that the run exists
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    # Get all steps for this run
    steps = (
        db.query(Step)
        .filter(Step.run_id == run_id)
        .order_by(Step.step_number)
        .all()
    )

    if not steps:
        raise HTTPException(
            status_code=404,
            detail="No steps found for this run"
        )

    ai = _ai_diagnose(db, run_id, steps)
    if ai is not None:
        return ai

    # Fallback: find the first failed step
    failed_step = None

    for step in steps:
        if step.status.lower() == "failed":
            failed_step = step
            break

    if failed_step is None:
        raise HTTPException(
            status_code=400,
            detail="No failed step found"
        )

    evidence = []

    if failed_step.error_message:
        evidence.append(
            f"Step reported error: {failed_step.error_message}"
        )

    if failed_step.input_data:
        evidence.append(
            f"Input: {failed_step.input_data}"
        )

    if failed_step.output_data:
        evidence.append(
            f"Output: {failed_step.output_data}"
        )

    reason = (
        f"Step {failed_step.step_number} "
        f"('{failed_step.name}') is the most likely "
        f"failure point because it is marked as failed "
        f"and produced the recorded error."
    )

    return DiagnosisResponse(
        run_id=run_id,
        failed_step_id=failed_step.id,
        failed_step_number=failed_step.step_number,
        failed_step_name=failed_step.name,
        reason=reason,
        evidence=evidence
    )