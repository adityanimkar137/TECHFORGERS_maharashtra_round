import json
import os
import random
from collections import Counter
from simulator import make_task, run_agent, FAULT_TYPES, VALID_FAULT_STEPS

N_RUNS = 4000
FAIL_RATE = 0.45
HOLDOUT_FAULT = "wrong_tool"   # never seen in training -> tests generalization

rng = random.Random(42)
out_path = os.path.join(os.path.dirname(__file__), "traces.jsonl")
counts = Counter()

with open(out_path, "w") as f:
    for run_id in range(N_RUNS):
        task = make_task(run_id)
        fault = None
        if rng.random() < FAIL_RATE:
            candidates = []
            for ft_name in FAULT_TYPES:
                valid_steps = [i for i, t in enumerate(task["step_types"])
                               if t in VALID_FAULT_STEPS[ft_name]]
                if valid_steps:
                    candidates.append((ft_name, valid_steps))
            ft, valid = rng.choice(candidates)
            fault = {"type": ft, "step": rng.choice(valid)}

        steps, success = run_agent(task, fault)

        if fault and fault["type"] == HOLDOUT_FAULT:
            split = "test_unseen"
        else:
            split = rng.choices(["train", "test_seen", "test_unseen"],
                                weights=[0.70, 0.15, 0.15])[0] if fault is None \
                    else rng.choices(["train", "test_seen"], weights=[0.8, 0.2])[0]

        row = {
            "run_id": run_id, "task": task, "steps": steps, "success": success,
            "root_cause_step": fault["step"] if fault else -1,
            "fault_type": fault["type"] if fault else None,
            "split": split,
        }
        f.write(json.dumps(row) + "\n")
        counts[(split, "fail" if fault else "ok")] += 1

print(f"Wrote {N_RUNS} runs to {out_path}")
for k, v in sorted(counts.items()):
    print(k, v)