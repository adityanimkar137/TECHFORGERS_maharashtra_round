from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Checkpoint, Run, Step
from ..schemas import CheckpointCreate, CheckpointResponse


router = APIRouter(
    prefix="/runs/{run_id}/checkpoints",
    tags=["Checkpoints"]
)


@router.post("/", response_model=CheckpointResponse)
def create_checkpoint(
    run_id: int,
    checkpoint_data: CheckpointCreate,
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    step = (
        db.query(Step)
        .filter(
            Step.id == checkpoint_data.step_id,
            Step.run_id == run_id
        )
        .first()
    )

    if step is None:
        raise HTTPException(
            status_code=404,
            detail="Step not found for this run"
        )

    checkpoint = Checkpoint(
        run_id=run_id,
        step_id=step.id,
        step_number=step.step_number,
        state_data=checkpoint_data.state_data
    )

    db.add(checkpoint)
    db.commit()
    db.refresh(checkpoint)

    return checkpoint


@router.get("/", response_model=list[CheckpointResponse])
def get_checkpoints(
    run_id: int,
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    checkpoints = (
        db.query(Checkpoint)
        .filter(Checkpoint.run_id == run_id)
        .order_by(Checkpoint.step_number)
        .all()
    )

    return checkpoints