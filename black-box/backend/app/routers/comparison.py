from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Replay, Run, Step
from ..schemas import ComparisonResponse


router = APIRouter(
    prefix="/runs/{run_id}/compare",
    tags=["Comparison"]
)


@router.get("/", response_model=ComparisonResponse)
def compare_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    failed_step = (
        db.query(Step)
        .filter(
            Step.run_id == run_id,
            Step.status == "failed"
        )
        .order_by(Step.step_number)
        .first()
    )

    if failed_step is None:
        raise HTTPException(
            status_code=400,
            detail="No failed step found"
        )

    alternative = (
        db.query(Replay)
        .filter(
            Replay.run_id == run_id,
            Replay.status == "alternative_completed"
        )
        .order_by(Replay.id.desc())
        .first()
    )

    if alternative is None:
        raise HTTPException(
            status_code=404,
            detail="No alternative execution found"
        )

    corrected_output = alternative.result or ""

    marker = "Corrected output: "

    if marker in corrected_output:
        corrected_output = corrected_output.split(
            marker,
            1
        )[1].split(
            "\n",
            1
        )[0]

    explanation = (
        f"Step {failed_step.step_number} "
        f"('{failed_step.name}') changed during "
        f"alternative execution. The original execution "
        f"selected '{failed_step.output_data}', while the "
        f"corrected execution selected "
        f"'{corrected_output}'."
    )

    return ComparisonResponse(
        run_id=run_id,
        original_output=failed_step.output_data or "",
        corrected_output=corrected_output,
        changed_step=failed_step.step_number,
        explanation=explanation
    )