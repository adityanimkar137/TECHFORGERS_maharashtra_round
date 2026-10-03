import json
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(__file__))
from features import build_baselines, run_features

HERE = os.path.dirname(__file__)
TRACES = os.path.join(HERE, "..", "dataset", "traces.jsonl")
MODEL_DIR = os.path.join(HERE, "..", "model")


def augment(X):
    """Add |z| and 'low-side' features so a linear model can spot unusual values in either direction."""
    absz = np.abs(X[:, [7, 8, 9, 10, 12]])
    low = np.minimum(X[:, [9, 10]], 0) ** 2
    return np.hstack([X, absz, low])


def fit_logreg(X, y, iters=2000, lr=0.3, l2=1e-3):
    mu, sd = X.mean(0), X.std(0) + 1e-6
    Z = (X - mu) / sd
    w = np.zeros(Z.shape[1])
    b = 0.0
    pos_w = (len(y) - y.sum()) / max(y.sum(), 1)      # balance rare root-cause steps
    sw = np.where(y == 1, pos_w, 1.0)
    sw = sw / sw.mean()
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z @ w + b)))
        g = (p - y) * sw
        w -= lr * (Z.T @ g / len(y) + l2 * w)
        b -= lr * g.mean()
    return {"w": w, "b": b, "mu": mu, "sd": sd}


def score(model, X):
    Z = (augment(X) - model["mu"]) / model["sd"]
    return 1 / (1 + np.exp(-(Z @ model["w"] + model["b"])))

def final_scores(model, row, base, seen_tools):
    """Supervised score + bonus for steps using a tool never seen for that step type."""
    s = score(model, run_features(row, base))
    bonus = np.array([0.0 if (st["type"], st["tool"]) in seen_tools else 1.0
                      for st in row["steps"]])
    return s + bonus

if __name__ == "__main__":
    rows = [json.loads(line) for line in open(TRACES)]
    train_rows = [r for r in rows if r["split"] == "train"]
    print(f"Training runs: {len(train_rows)} "
          f"({sum(not r['success'] for r in train_rows)} failed)")

    base = build_baselines(train_rows)
    seen_tools = {(s["type"], s["tool"]) for r in train_rows if r["success"]
                  for s in r["steps"]}
    with open(os.path.join(MODEL_DIR, "seen_tools.json"), "w") as f:
        os.makedirs(MODEL_DIR, exist_ok=True)
        json.dump(sorted(list(p) for p in seen_tools), f)
    X, y = [], []
    for r in train_rows:
        feats = run_features(r, base)
        for i in range(len(r["steps"])):
            X.append(feats[i])
            y.append(1.0 if (not r["success"] and i == r["root_cause_step"]) else 0.0)
    X, y = np.array(X), np.array(y)
    print(f"Step examples: {len(y)}  (root-cause steps: {int(y.sum())})")

    model = fit_logreg(augment(X), y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    np.savez(os.path.join(MODEL_DIR, "blackbox_model.npz"),
             w=model["w"], b=model["b"], mu=model["mu"], sd=model["sd"])
    with open(os.path.join(MODEL_DIR, "baselines.json"), "w") as f:
        json.dump(base, f)
    print("Saved model to", os.path.abspath(MODEL_DIR))

    def top1(split):
        hits = total = 0
        for r in rows:
            if r["split"] != split or r["success"]:
                continue
            s = final_scores(model, r, base, seen_tools)
            hits += int(np.argmax(s) == r["root_cause_step"])
            total += 1
        return hits, total

    for sp in ["test_seen", "test_unseen"]:
        h, t = top1(sp)
        if t:
            print(f"{sp}: found the root-cause step in {h}/{t} failed runs ({h/t:.0%})")