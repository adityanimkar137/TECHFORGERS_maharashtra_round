"""Public entry point for the replay-engine package."""

from typing import Any, Dict, Optional

from app.checkpoint.manager import CheckpointManager
from app.comparison.comparator import TraceComparator
from app.replay.runner import ReplayRunner


class ReplayEngine:
    """Facade that keeps integration simple for the backend team."""

    def __init__(self):
        self.checkpoints = CheckpointManager()
        self.runner = ReplayRunner()
        self.comparator = TraceComparator()

    def create_checkpoint(
        self,
        run: Dict[str, Any],
        start_step: int,
    ) -> Dict[str, Any]:
        checkpoint = self.checkpoints.create(run, start_step)
        return checkpoint.to_dict()

    def replay(
        self,
        run: Dict[str, Any],
        start_step: int,
        modified_outputs: Optional[Dict[int, Any]] = None,
    ) -> Dict[str, Any]:
        return self.runner.replay(
            run=run,
            start_step=start_step,
            modified_outputs=modified_outputs,
        )

    def compare(
        self,
        original: Dict[str, Any],
        replay: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self.comparator.compare(original, replay)
