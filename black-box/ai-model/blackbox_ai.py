"""The ONE entry point the backend uses to talk to the AI model.

    from blackbox_ai import diagnose_steps
    result = diagnose_steps(steps)

`steps` is a list of dicts, in execution order, each with:
    type             "plan" | "retrieve" | "tool_call" | "reason" | "verify" | "answer"
    tool             name of the tool/model used (str)
    latency_ms       float
    tokens           int
    confidence       float 0..1
    retrieval_score  float 0..1 (0 if not a retrieval step)
    error            0 or 1
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "training"), os.path.join(HERE, "dataset")):
    if p not in sys.path:
        sys.path.append(p)

from features import run_features          # noqa: E402
from predict import load_model, explain    # noqa: E402
from train import score                    # noqa: E402

REQUIRED = ["type", "tool", "latency_ms", "tokens", "confidence", "retrieval_score", "error"]
_cache = {}


def _model():
    if "m" not in _cache:
        _cache["m"] = load_model()
    return _cache["m"]


def has_metrics(step):
    return all(k in step for k in REQUIRED)


def _anomaly(feats, steps, seen):
    a = (np.maximum(0, feats[:, 7] - 2) + np.maximum(0, feats[:, 8] - 2)
         + np.maximum(0, -feats[:, 9] - 2) + np.maximum(0, -feats[:, 10] - 2)
         + 3 * feats[:, 11])
    bonus = np.array([10.0 if (s["type"], s["tool"]) not in seen else 0.0 for s in steps])
    return a + bonus


def diagnose_steps(steps, gate=1.0):
    model, base, seen = _model()
    steps = [dict(s, idx=i) for i, s in enumerate(steps)]
    row = {"steps": steps}
    feats = run_features(row, base)
    an = _anomaly(feats, steps, seen)
    sup = score(model, feats)
    scores = sup if an.max() < gate else an + 0.1 * sup      # hybrid detector
    order = [int(i) for i in np.argsort(-scores)]
    shares = scores / max(float(scores.sum()), 1e-9)          # relative suspicion, NOT calibrated
    top = float(shares[order[0]])
    return {
        "suspect": order[0],
        "ranking": order[:3],
        "shares": [float(x) for x in shares],
        "confidence": "High" if top > 0.6 else "Medium" if top > 0.35 else "Low",
        "evidence": explain(row, feats, order[0], seen),
    }
