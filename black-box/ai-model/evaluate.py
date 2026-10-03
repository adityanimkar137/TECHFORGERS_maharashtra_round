import json
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "training"))
from features import build_baselines, run_features
from train import augment, fit_logreg, score

rows = [json.loads(l) for l in open(os.path.join(HERE, "dataset", "traces.jsonl"))]
FAULTS = sorted({r["fault_type"] for r in rows if r["fault_type"]})


def train_without(held):
    """Train on the train split, leaving out every run whose fault type is `held`."""
    tr = [r for r in rows if r["split"] == "train" and r["fault_type"] != held]
    base = build_baselines(tr)
    seen = {(s["type"], s["tool"]) for r in tr if r["success"] for s in r["steps"]}
    X, y = [], []
    for r in tr:
        f = run_features(r, base)
        for i in range(len(r["steps"])):
            X.append(f[i])
            y.append(1.0 if (not r["success"] and i == r["root_cause_step"]) else 0.0)
    model = fit_logreg(augment(np.array(X)), np.array(y))
    return model, base, seen


def evaluate(model, base, seen, test):
    top1 = top3 = 0
    chance = 0.0
    for r in test:
        bonus = np.array([0.0 if (s["type"], s["tool"]) in seen else 1.0 for s in r["steps"]])
        sc = score(model, run_features(r, base)) + bonus
        order = list(np.argsort(-sc))
        top1 += order[0] == r["root_cause_step"]
        top3 += r["root_cause_step"] in order[:3]
        chance += 1 / len(r["steps"])
    n = len(test)
    return n, top1 / n, top3 / n, chance / n


def line(name, res):
    n, a, b, c = res
    print(f"{name:<28}{n:>5}{a:>9.0%}{b:>9.0%}{c:>9.0%}")


print(f"{'':<28}{'runs':>5}{'top-1':>9}{'top-3':>9}{'chance':>9}")

# 1) Normal split: trained on all fault types except wrong_tool, tested on held-out runs
model, base, seen = train_without("wrong_tool")
seen_test = [r for r in rows if r["split"] == "test_seen" and not r["success"]]
print("-- Previously seen faults (test_seen) --")
for ft in FAULTS:
    t = [r for r in seen_test if r["fault_type"] == ft]
    if t:
        line(ft, evaluate(model, base, seen, t))
line("ALL seen", evaluate(model, base, seen, seen_test))

# 2) Leave-one-fault-out: hide each fault type, retrain, test on it
print("\n-- Leave-one-fault-out (fault type never seen in training) --")
for held in FAULTS:
    model, base, seen = train_without(held)
    t = [r for r in rows if r["fault_type"] == held]
    line(held, evaluate(model, base, seen, t))
def anomaly(row, base, seen):
    """Label-free: how far is each step beyond normal (learned from successful runs only)?"""
    f = run_features(row, base)
    a = (np.maximum(0, f[:, 7] - 2)       # slow
         + np.maximum(0, f[:, 8] - 2)     # too many tokens
         + np.maximum(0, -f[:, 9] - 2)    # low confidence
         + np.maximum(0, -f[:, 10] - 2)   # low retrieval score
         + 3 * f[:, 11])                  # reported an error
    bonus = np.array([10.0 if (s["type"], s["tool"]) not in seen else 0.0
                      for s in row["steps"]])
    return a + bonus


print("\n-- Label-free detector (successful runs only, zero fault labels) --")
tr = [r for r in rows if r["split"] == "train"]
base_lf = build_baselines(tr)
seen_lf = {(s["type"], s["tool"]) for r in tr if r["success"] for s in r["steps"]}
for ft in FAULTS:
    t = [r for r in rows if r["fault_type"] == ft]
    top1 = top3 = chance = 0
    for r in t:
        order = list(np.argsort(-anomaly(r, base_lf, seen_lf)))
        top1 += order[0] == r["root_cause_step"]
        top3 += r["root_cause_step"] in order[:3]
        chance += 1 / len(r["steps"])
    n = len(t)
    print(f"{ft:<28}{n:>5}{top1/n:>9.0%}{top3/n:>9.0%}{chance/n:>9.0%}")
def hybrid_order(model, base, seen, r, gate=1.0):
    a = anomaly(r, base, seen)
    sup = score(model, run_features(r, base))
    if a.max() < gate:                       # nothing looks abnormal -> trust the learned model
        return list(np.argsort(-sup))
    return list(np.argsort(-(a + 0.1 * sup)))  # otherwise rank by anomaly, supervised as tiebreak


def eval_hybrid(model, base, seen, test):
    top1 = top3 = chance = 0
    for r in test:
        order = hybrid_order(model, base, seen, r)
        top1 += order[0] == r["root_cause_step"]
        top3 += r["root_cause_step"] in order[:3]
        chance += 1 / len(r["steps"])
    n = len(test)
    return n, top1 / n, top3 / n, chance / n


print("\n-- Hybrid: anomaly detector first, supervised model as fallback --")
print("Previously seen faults:")
model, base, seen = train_without("wrong_tool")
for ft in FAULTS:
    t = [r for r in seen_test if r["fault_type"] == ft]
    if t:
        line(ft, eval_hybrid(model, base, seen, t))
line("ALL seen", eval_hybrid(model, base, seen, seen_test))

print("Leave-one-fault-out:")
for held in FAULTS:
    model, base, seen = train_without(held)
    t = [r for r in rows if r["fault_type"] == held]
    line(held, eval_hybrid(model, base, seen, t))