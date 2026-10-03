import json
import os
import sys
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
sys.path.append(os.path.join(HERE, "training"))
from features import run_features
from train import score
from predict import load_model, replay_with_fix, TRACES

TOP_K = 3


def anomaly(row, base, seen):
    f = run_features(row, base)
    a = (np.maximum(0, f[:, 7] - 2) + np.maximum(0, f[:, 8] - 2)
         + np.maximum(0, -f[:, 9] - 2) + np.maximum(0, -f[:, 10] - 2)
         + 3 * f[:, 11])
    bonus = np.array([10.0 if (s["type"], s["tool"]) not in seen else 0.0
                      for s in row["steps"]])
    return a + bonus


def hybrid_order(model, base, seen, row, gate=1.0):
    a = anomaly(row, base, seen)
    sup = score(model, run_features(row, base))
    if a.max() < gate:
        return list(np.argsort(-sup))
    return list(np.argsort(-(a + 0.1 * sup)))


def search_fix(row, model, base, seen):
    """Try fixes at the top-K suspects in order. Returns (attempt that worked or 0, steps re-run)."""
    order = hybrid_order(model, base, seen, row)
    steps_rerun = 0
    for attempt, k in enumerate(order[:TOP_K], start=1):
        steps, ok = replay_with_fix(row, int(k))
        steps_rerun += len(steps)
        if ok:
            return attempt, steps_rerun
    return 0, steps_rerun


if __name__ == "__main__":
    model, base, seen = load_model()
    rows = [json.loads(l) for l in open(TRACES)]
    failed = [r for r in rows if r["split"].startswith("test") and not r["success"]]

    stats = defaultdict(lambda: {"n": 0, "at1": 0, "atK": 0, "rerun": 0, "full": 0})
    for r in failed:
        attempt, rerun = search_fix(r, model, base, seen)
        for key in (r["fault_type"], "ALL"):
            s = stats[key]
            s["n"] += 1
            s["at1"] += attempt == 1
            s["atK"] += attempt > 0
            s["rerun"] += rerun
            s["full"] += len(r["steps"])

    print(f"{'':<22}{'runs':>6}{'fixed@1':>9}{'fixed@3':>9}{'steps re-run vs one full re-run':>34}")
    for key in sorted(stats, key=lambda k: (k == "ALL", k)):
        s = stats[key]
        print(f"{key:<22}{s['n']:>6}{s['at1']/s['n']:>9.0%}{s['atK']/s['n']:>9.0%}"
              f"{s['rerun']/s['full']:>27.0%}")