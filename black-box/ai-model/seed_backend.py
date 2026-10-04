"""Fill the REAL backend with runs from the simulated agent, so the website shows live data.

    python seed_backend.py                       # 12 runs -> http://localhost:8000
    python seed_backend.py http://localhost:8000 30

Each step is POSTed with its metrics (tool, latency, tokens, confidence...) and a checkpoint.
The true root-cause step is NOT marked as failed: like a real agent, the run only fails at the end
(final answer rejected), and the AI model has to work out which earlier step caused it.
"""
import json
import random
import sys
import urllib.request

sys.path.append("dataset")
from simulator import make_task, run_agent, FAULT_TYPES, VALID_FAULT_STEPS

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12
NAMES = {"plan": "Plan task", "retrieve": "Retrieve context", "tool_call": "Call tool",
         "reason": "Reason", "verify": "Verify", "answer": "Generate answer"}


def post(path, body):
    req = urllib.request.Request(BASE + path, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


rng = random.Random(2026)
for n in range(N):
    task = make_task(900000 + n)
    fault = None
    if n % 2 == 1:                                   # every other run fails
        options = [(f, [i for i, t in enumerate(task["step_types"]) if t in VALID_FAULT_STEPS[f]])
                   for f in FAULT_TYPES]
        options = [(f, v) for f, v in options if v and f != "silent_corruption"]
        f, v = rng.choice(options)
        fault = {"type": f, "step": rng.choice(v)}
    steps, ok = run_agent(task, fault)
    last = len(steps) - 1
    run = post("/runs/", {
        "task": f"Simulated task #{n + 1}",
        "status": "success" if ok else "failed",
        "final_output": str(steps[-1]["output"]),
        "failure_reason": None if ok else "Final answer failed verification"})
    for i, s in enumerate(steps):
        failed_here = (not ok) and i == last
        saved = post(f"/runs/{run['id']}/steps/", {
            "step_number": i + 1, "name": NAMES[s["type"]],
            "status": "failed" if failed_here else "success",
            "input_data": json.dumps(s["checkpoint"]), "output_data": str(s["output"]),
            "error_message": "Final answer failed verification" if failed_here else None,
            "metrics": {k: s[k] for k in ["type", "tool", "latency_ms", "tokens",
                                          "confidence", "retrieval_score", "error"]}})
        post(f"/runs/{run['id']}/checkpoints/", {"step_id": saved["id"],
                                                 "state_data": json.dumps(s["checkpoint"])})
    print(f"run {run['id']}: {'success' if ok else 'FAILED  (hidden cause: ' + fault['type'] + ' at step ' + str(fault['step'] + 1) + ')'}")
