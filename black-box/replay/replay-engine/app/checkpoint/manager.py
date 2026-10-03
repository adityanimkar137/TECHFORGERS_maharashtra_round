"""Checkpoint creation and loading."""

from copy import deepcopy
from typing import Any, Dict

from app.models import Checkpoint


class CheckpointManager:
    """Creates an immutable-in-practice snapshot before a replay step."""

    def create(self, run: Dict[str, Any], start_step: int) -> Checkpoint:
        steps = run.get("steps", [])
        self._validate_step_exists(steps, start_step)

        # Save only the unaffected steps before the replay point.
        previous_steps = [
            deepcopy(step)
            for step in steps
            if step["step_id"] < start_step
        ]

        return Checkpoint(
            run_id=run["run_id"],
            step_id=start_step,
            steps_before=previous_steps,
        )

    def restore(self, checkpoint: Checkpoint) -> Dict[str, Any]:
        """Return the state represented by a checkpoint."""
        return {
            "run_id": checkpoint.run_id,
            "steps": deepcopy(checkpoint.steps_before),
        }

    @staticmethod
    def _validate_step_exists(steps, step_id: int) -> None:
        if not any(step["step_id"] == step_id for step in steps):
            raise ValueError(f"Step {step_id} does not exist in this run.")
