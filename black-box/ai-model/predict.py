import json
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "training"))
sys.path.append(os.path.join(HERE, "dataset"))
from features import run_features, FEATURE_NAMES
from train import score
from simulator import run_agent

F = {n: i for i, n in enumerate(FEATURE_NAMES)}
MODEL_DIR = os.path.join(HERE, "model")
TRACES = os.path.join(HERE, "dataset", "traces.jsonl")


def load_model():
    d = np.load(os.path.join(MODEL_DIR, "blackbox_model.npz"))
    model = {k: d[k] for k in ["w", "b", "mu", "sd"]}
    base = json.load(open(os.path.join(MODEL_DIR, "baselines.json")))
    seen = {tuple(p) for p in json.load(open(os.path.join(MODEL_DIR, "seen_tools.json")))}
    return model, base, seen


def diagnose(row, model, base, seen):
    """Return (ranked step indices, feature matrix, scores)."""
    feats = run_features(row, base)
    bonus = np.array([0.0 if (s["type"], s["tool"]) in seen else 1.0 for s in row["steps"]])
    scores = score(model, feats) + bonus
    return list(np.argsort(-scores)), feats, scores


def explain(row, feats, k, seen):
    s, f = row["steps"][k], feats[k]
    ev = []
    if (s["type"], s["tool"]) not in seen:
        ev.append(f"used tool '{s['tool']}', never seen on '{s['type']}' steps in successful runs")
    if f[F["latency_z"]] > 3:
        ev.append(f"latency {s['latency_ms']:.0f} ms is {f[F['latency_z']]:.1f} std above normal")
    if f[F["confidence_z"]] < -2:
        ev.append(f"confidence {s['confidence']:.2f} is {abs(f[F['confidence_z']]):.1f} std below normal")
    if s["type"] == "retrieve" and f[F["retrieval_z"]] < -2:
        ev.append(f"retrieval score {s['retrieval_score']:.2f} is {abs(f[F['retrieval_z']]):.1f} std below normal")
    if f[F["tokens_z"]] > 3:
        ev.append(f"token count {s['tokens']} is {f[F['tokens_z']]:.1f} std above normal")
    if s["error"]:
        ev.append("step reported an error")
    later = feats[k + 1:, F["confidence_z"]]
    if len(later) and later.mean() < -0.3:
        ev.append("later steps show lower confidence than normal (downstream degradation)")
    if not ev:
        ev.append("no single metric is extreme; flagged on a combination of weak signals "
                  "(typical of silent corruption, low confidence in this diagnosis)")
    return ev


def replay_with_fix(row, k):
    """Resume from step k's checkpoint with step k fixed. Steps before k are NOT re-run.
    If the real fault is at a different step, it still happens, so the run still fails."""
    fault = {"type": row["fault_type"], "step": row["root_cause_step"]}
    if fault["step"] == k:
        fault = None                      # the proposed fix removes the fault
    steps, ok = run_agent(row["task"], fault, start_step=k,
                          checkpoint=row["steps"][k]["checkpoint"])
    return steps, ok


def show(row, model, base, seen):
    order, feats, scores = diagnose(row, model, base, seen)
    k = order[0]
    n = len(row["steps"])
    print(f"\n=== Run {row['run_id']} (failed) ===")
    print(f"Diagnosis: step {k} ({row['steps'][k]['type']}, tool={row['steps'][k]['tool']})"
          f"   [runner-ups: {order[1]}, {order[2]}]")
    print("Evidence:")
    for e in explain(row, feats, k, seen):
        print("  -", e)
    steps, ok = replay_with_fix(row, k)
    print(f"Replay from checkpoint at step {k}: re-ran {len(steps)} of {n} steps "
          f"(skipped {k}), final answer correct: {ok}")
    print(f"Trace comparison, final output: original={row['steps'][-1]['output']}  "
          f"replayed={steps[-1]['output']}  expected={row['task']['expected']}")
    print(f"(Ground truth: step {row['root_cause_step']}, fault={row['fault_type']})")


if __name__ == "__main__":
    model, base, seen = load_model()
    rows = [json.loads(l) for l in open(TRACES)]
    failed = [r for r in rows if r["split"].startswith("test") and not r["success"]]

    if len(sys.argv) > 1:
        picks = [r for r in failed if r["run_id"] == int(sys.argv[1])]
    else:
        picks = []
        for ft in ["bad_retrieval", "silent_corruption", "wrong_tool"]:
            picks += [r for r in failed if r["fault_type"] == ft][:1]
    for r in picks:
        show(r, model, base, seen)

    fixed = saved = total_steps = 0
    for r in failed:
        k = diagnose(r, model, base, seen)[0][0]
        _, ok = replay_with_fix(r, k)
        fixed += ok
        saved += k
        total_steps += len(r["steps"])
    print(f"\nOver {len(failed)} held-out failed runs: fixing the diagnosed step "
          f"recovered {fixed} ({fixed/len(failed):.0%}); "
          f"replay skipped {saved/total_steps:.0%} of steps vs. full re-execution.")