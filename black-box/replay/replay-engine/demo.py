"""Run this file to see the replay engine working."""

import json
from pathlib import Path

from app.engine import ReplayEngine


def load_sample_run():
    path = Path(__file__).parent / "data" / "sample_run.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    run = load_sample_run()
    engine = ReplayEngine()

    print("=" * 60)
    print("BLACK BOX - REPLAY ENGINE DEMO")
    print("=" * 60)

    print("\n1. Original execution")
    for step in run["steps"]:
        print(f"Step {step['step_id']}: {step['name']} -> {step['status']}")

    print("\n2. Creating checkpoint before Step 3...")
    checkpoint = engine.create_checkpoint(run, start_step=3)
    print(f"Checkpoint created for {checkpoint['run_id']} at Step {checkpoint['step_id']}")

    print("\n3. Replaying from Step 3 with corrected price...")
    replay = engine.replay(
        run=run,
        start_step=3,
        modified_outputs={3: "₹45999"},
    )

    for step in replay["steps"]:
        marker = "(replayed)" if step["step_id"] >= 3 else "(restored)"
        print(
            f"Step {step['step_id']}: {step['name']} -> "
            f"{step['status']} {marker}"
        )

    print(f"\nReplay status: {replay['status']}")

    print("\n4. Comparing original vs replay...")
    comparison = engine.compare(run, replay)

    print(f"Original: {comparison['original_status']}")
    print(f"Replay:   {comparison['replay_status']}")
    print(f"Fixed:    {comparison['fixed']}")

    print("\nChanged steps:")
    for diff in comparison["differences"]:
        print(
            f"- Step {diff['step_id']}: "
            f"{diff.get('original_status')} -> {diff.get('replay_status')}"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
