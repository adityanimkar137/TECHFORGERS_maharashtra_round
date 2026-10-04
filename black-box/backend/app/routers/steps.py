from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
import json

from ..models import Run, Step, StepMetric
from ..schemas import StepIngest, StepResponse


router = APIRouter(
    prefix="/runs/{run_id}/steps",
    tags=["Steps"]
)


@router.post("/", response_model=StepResponse)
def create_step(
    run_id: int,
    step_data: StepIngest,
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    step = Step(
        run_id=run_id,
        step_number=step_data.step_number,
        name=step_data.name,
        status=step_data.status,
        input_data=step_data.input_data,
        output_data=step_data.output_data,
        error_message=step_data.error_message,
    )

    db.add(step)
    if step_data.metrics:
        db.add(StepMetric(run_id=run_id, step_number=step_data.step_number,
                          data=json.dumps(step_data.metrics)))
    db.commit()
    db.refresh(step)

    return step


@router.get("/", response_model=list[StepResponse])
def get_steps(
    run_id: int,
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    steps = (
        db.query(Step)
        .filter(Step.run_id == run_id)
        .order_by(Step.step_number)
        .all()
    )

    return steps