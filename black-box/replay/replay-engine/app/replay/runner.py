"""Replay logic.

The demo executor below is deliberately simple. In the real project,
the backend team can replace _execute_step() with the actual agent/tool
execution logic without changing the checkpoint or comparison modules.
"""

from copy import deepcopy
from typing import Any, Dict, Optional


class ReplayRunner:
    """Runs an execution from a selected step."""

    def replay(
        self,
        run: Dict[str, Any],
        start_step: int,
        modified_outputs: Optional[Dict[int, Any]] = None,
    ) -> Dict[str, Any]:
        modified_outputs = modified_outputs or {}

        original_steps = run.get("steps", [])
        if not original_steps:
            raise ValueError("The run contains no steps.")

        if not any(s["step_id"] == start_step for s in original_steps):
            raise ValueError(f"Step {start_step} does not exist.")

        replay_steps = deepcopy(original_steps)

        for step in replay_steps:
            if step["step_id"] < start_step:
                # Unaffected steps are restored, not executed again.
                continue

            if step["step_id"] in modified_outputs:
                step["output"] = modified_outputs[step["step_id"]]
                step["metadata"]["modified_for_replay"] = True

            self._execute_step(step, replay_steps)

        final_status = (
            "success"
            if all(step["status"] == "success" for step in replay_steps)
            else "failed"
        )

        return {
            "run_id": run["run_id"],
            "replay_from_step": start_step,
            "status": final_status,
            "steps": replay_steps,
        }

    @staticmethod
    def _execute_step(step: Dict[str, Any], all_steps) -> None:
        """Demo execution rule.

        A real implementation can call an agent/tool here.
        For the demo, Step 4 succeeds when Step 3 contains a valid
        numeric price below 100000.
        """

        step_id = step["step_id"]

        if step_id == 3:
            try:
                price = float(str(step["output"]).replace("₹", "").replace(",", ""))
                step["status"] = "success" if 0 < price < 100000 else "failed"
            except ValueError:
                step["status"] = "failed"
            return

        if step_id == 4:
            step3 = next(s for s in all_steps if s["step_id"] == 3)
            if step3["status"] == "success":
                step["output"] = "Correct calculation"
                step["status"] = "success"
            else:
                step["output"] = "Calculation failed because Step 3 failed"
                step["status"] = "failed"
            return

        if step_id == 5:
            step4 = next(s for s in all_steps if s["step_id"] == 4)
            if step4["status"] == "success":
                step["output"] = "Final answer generated successfully"
                step["status"] = "success"
            else:
                step["output"] = "Final answer could not be generated"
                step["status"] = "failed"
            return

        # Generic demo rule for other steps.
        step["status"] = "success"
