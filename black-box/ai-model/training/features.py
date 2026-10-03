import math
import numpy as np

TYPES = ["plan", "retrieve", "tool_call", "reason", "verify", "answer"]
EXPECTED_TOOLS = {
    "plan": ["planner"],
    "retrieve": ["search", "vector_db"],
    "tool_call": ["calculator", "code_exec"],
    "reason": ["llm"],
    "verify": ["llm"],
    "answer": ["llm"],
}
FEATURE_NAMES = (
    [f"is_{t}" for t in TYPES]
    + ["tool_mismatch", "latency_z", "tokens_z", "confidence_z",
       "retrieval_z", "error", "conf_change", "prev_conf_z", "position"]
)


def build_baselines(rows):
    """Learn what a 'normal' step looks like, per step type, from successful runs."""
    vals = {t: {"lat": [], "tok": [], "conf": [], "ret": []} for t in TYPES}
    for r in rows:
        if not r["success"]:
            continue
        for s in r["steps"]:
            v = vals[s["type"]]
            v["lat"].append(math.log(s["latency_ms"]))
            v["tok"].append(s["tokens"])
            v["conf"].append(s["confidence"])
            if s["type"] == "retrieve":
                v["ret"].append(s["retrieval_score"])
    base = {}
    for t, v in vals.items():
        base[t] = {k: (float(np.mean(x)) if x else 0.0, max(float(np.std(x)), 1e-3) if x else 1.0)
                   for k, x in v.items()}
    return base


def _z(x, ms):
    return (x - ms[0]) / ms[1]


def run_features(row, base):
    """Return a (n_steps, n_features) matrix for one run."""
    steps = row["steps"]
    n = len(steps)
    X = []
    prev_conf_z = 0.0
    prev_conf = None
    for s in steps:
        b = base[s["type"]]
        conf_z = _z(s["confidence"], b["conf"])
        f = [1.0 if s["type"] == t else 0.0 for t in TYPES]
        f.append(0.0 if s["tool"] in EXPECTED_TOOLS[s["type"]] else 1.0)
        f.append(_z(math.log(s["latency_ms"]), b["lat"]))
        f.append(_z(s["tokens"], b["tok"]))
        f.append(conf_z)
        f.append(_z(s["retrieval_score"], b["ret"]) if s["type"] == "retrieve" else 0.0)
        f.append(float(s["error"]))
        f.append(0.0 if prev_conf is None else s["confidence"] - prev_conf)
        f.append(prev_conf_z)
        f.append(s["idx"] / max(n - 1, 1))
        X.append(f)
        prev_conf_z = conf_z
        prev_conf = s["confidence"]
    return np.array(X, dtype=float)