import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Replay, Run, Step
from ..schemas import ReplayCreate, ReplayResponse


router = APIRouter(
    prefix="/runs/{run_id}/replay",
    tags=["Replay"]
)


@router.post("/", response_model=ReplayResponse)
def replay_run(
    run_id: int,
    replay_data: ReplayCreate,
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
        .filter(
            Step.run_id == run_id,
            Step.step_number >= replay_data.start_step_number
        )
        .order_by(Step.step_number)
        .all()
    )

    if not steps:
        raise HTTPException(
            status_code=404,
            detail="No steps found from the selected step"
        )

    result_lines = []

    for step in steps:
        result_lines.append(
            f"Step {step.step_number}: "
            f"{step.name} -> {step.output_data or 'No output'}"
        )

    result = "\n".join(result_lines)

    replay = Replay(
        run_id=run_id,
        start_step_number=replay_data.start_step_number,
        status="completed",
        result=result
    )

    db.add(replay)
    db.commit()
    db.refresh(replay)

    return replay


@router.get("/", response_model=list[ReplayResponse])
def get_replays(
    run_id: int,
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    replays = (
        db.query(Replay)
        .filter(Replay.run_id == run_id)
        .order_by(Replay.id.desc())
        .all()
    )

    return replays