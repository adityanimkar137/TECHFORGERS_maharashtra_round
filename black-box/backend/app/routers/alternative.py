import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Replay, Run, Step
from ..schemas import ReplayResponse


router = APIRouter(
    prefix="/runs/{run_id}/alternative",
    tags=["Alternative Execution"]
)


@router.post("/", response_model=ReplayResponse)
def alternative_execution(
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

    input_data = failed_step.input_data or ""

    prices = re.findall(
        r"([A-Za-z]+):\s*₹?(\d+)",
        input_data
    )

    if not prices:
        raise HTTPException(
            status_code=400,
            detail="Could not extract product prices"
        )

    price_data = [
        (name, int(price))
        for name, price in prices
    ]

    cheapest_name, cheapest_price = min(
        price_data,
        key=lambda item: item[1]
    )

    corrected_output = (
        f"{cheapest_name} is the cheapest at "
        f"₹{cheapest_price}"
    )

    result = (
        f"Original output: {failed_step.output_data}\n"
        f"Corrected output: {corrected_output}\n"
        f"Reason: The alternative execution compared "
        f"all extracted prices and selected the minimum."
    )

    replay = Replay(
        run_id=run_id,
        start_step_number=failed_step.step_number,
        status="alternative_completed",
        result=result
    )

    db.add(replay)
    db.commit()
    db.refresh(replay)

    return replay