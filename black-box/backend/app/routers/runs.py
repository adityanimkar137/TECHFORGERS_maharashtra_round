from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Run
from ..schemas import RunCreate, RunResponse


router = APIRouter(
    prefix="/runs",
    tags=["Runs"]
)


@router.post("/", response_model=RunResponse)
def create_run(
    run_data: RunCreate,
    db: Session = Depends(get_db)
):
    run = Run(
        task=run_data.task,
        status=run_data.status,
        final_output=run_data.final_output,
        failure_reason=run_data.failure_reason,
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run

@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    return run