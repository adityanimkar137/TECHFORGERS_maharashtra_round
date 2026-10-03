from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Run, Step
from ..schemas import DiagnosisResponse


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

    # Find the first failed step
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