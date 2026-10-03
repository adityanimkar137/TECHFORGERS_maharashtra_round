"""Data models used by the replay engine.

Keeping the data structures here makes the rest of the project easier
for other team members to understand and integrate.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Step:
    """One observable step in an agent execution."""

    step_id: int
    name: str
    step_type: str
    input_data: Any
    output: Any
    status: str = "success"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "step_type": self.step_type,
            "input_data": self.input_data,
            "output": self.output,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass
class Checkpoint:
    """Saved execution state used as the starting point for replay."""

    run_id: str
    step_id: int
    steps_before: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "step_id": self.step_id,
            "steps_before": self.steps_before,
        }
