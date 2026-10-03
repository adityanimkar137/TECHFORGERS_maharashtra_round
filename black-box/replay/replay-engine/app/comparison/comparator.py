"""Compare original and replayed execution traces."""

from typing import Any, Dict, List


class TraceComparator:
    """Produces a simple, frontend-friendly comparison."""

    def compare(
        self,
        original: Dict[str, Any],
        replay: Dict[str, Any],
    ) -> Dict[str, Any]:
        original_steps = {
            step["step_id"]: step for step in original.get("steps", [])
        }
        replay_steps = {
            step["step_id"]: step for step in replay.get("steps", [])
        }

        differences: List[Dict[str, Any]] = []

        for step_id in sorted(set(original_steps) | set(replay_steps)):
            old = original_steps.get(step_id)
            new = replay_steps.get(step_id)

            if old is None or new is None:
                differences.append({
                    "step_id": step_id,
                    "type": "step_added_or_removed",
                    "original": old,
                    "replay": new,
                })
                continue

            if old["output"] != new["output"] or old["status"] != new["status"]:
                differences.append({
                    "step_id": step_id,
                    "type": "changed",
                    "original_status": old["status"],
                    "replay_status": new["status"],
                    "original_output": old["output"],
                    "replay_output": new["output"],
                })

        return {
            "original_status": original.get("status", "unknown"),
            "replay_status": replay.get("status", "unknown"),
            "changed_step_count": len(differences),
            "differences": differences,
            "fixed": (
                original.get("status") == "failed"
                and replay.get("status") == "success"
            ),
        }
