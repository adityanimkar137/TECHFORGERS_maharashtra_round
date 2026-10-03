import random
from math import gcd

STEP_TYPES_MIDDLE = ["retrieve", "tool_call", "reason"]
EXPECTED_TOOLS = {
    "plan": ["planner"],
    "retrieve": ["search", "vector_db"],
    "tool_call": ["calculator", "code_exec"],
    "reason": ["llm"],
    "verify": ["llm"],
    "answer": ["llm"],
}
ALL_TOOLS = ["planner", "search", "vector_db", "calculator", "code_exec", "llm"]
FAULT_TYPES = ["bad_retrieval", "tool_error", "hallucination", "wrong_tool", "silent_corruption"]
VALID_FAULT_STEPS = {
    "bad_retrieval": ["retrieve"],
    "tool_error": ["tool_call"],
    "hallucination": ["plan", "reason"],
    "wrong_tool": ["retrieve", "tool_call"],
    "silent_corruption": ["plan", "retrieve", "tool_call", "reason", "verify"],
}
UNITS = [a for a in range(1, 60) if gcd(a, 1000) == 1]


def clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def make_task(seed):
    """A task = a chain of steps; each step transforms a value (mod 1000)."""
    rng = random.Random(f"task-{seed}")
    n_mid = rng.randint(3, 7)
    step_types = ["plan", "retrieve"] + [rng.choice(STEP_TYPES_MIDDLE) for _ in range(n_mid)] + ["verify", "answer"]
    ops = [(rng.choice(UNITS), rng.randint(0, 999)) for _ in step_types]
    start = rng.randint(0, 999)
    expected = start
    for a, b in ops:
        expected = (expected * a + b) % 1000
    return {"seed": seed, "step_types": step_types, "ops": ops, "start": start, "expected": expected}


def execute_step(task, idx, state, fault):
    """Run ONE step. Deterministic per (task seed, idx), so replays reproduce unaffected steps."""
    rng = random.Random(f"{task['seed']}-step-{idx}")
    stype = task["step_types"][idx]
    a, b = task["ops"][idx]

    tool = rng.choice(EXPECTED_TOOLS[stype])
    latency = rng.lognormvariate(5.0, 0.25)
    if rng.random() < 0.05:                      # benign distractor: latency spike
        latency *= 4
    tokens = max(5, int(rng.gauss(120, 30)))
    confidence = clip(rng.gauss(0.85, 0.07))
    retrieval_score = clip(rng.gauss(0.80, 0.08)) if stype == "retrieve" else 0.0
    error = 1 if rng.random() < 0.02 else 0      # benign distractor: recovered error

    if state["corrupted"]:                       # downstream symptom: mild degradation
        confidence = clip(confidence - abs(rng.gauss(0.05, 0.03)))

    true_out = (state["value"] * a + b) % 1000
    out = true_out
    corrupt_now = False

    if fault is not None and fault["step"] == idx:
        ft = fault["type"]
        corrupt_now = True
        if ft == "bad_retrieval":
            retrieval_score = clip(rng.gauss(0.35, 0.12))
        elif ft == "tool_error":
            error = 1
            latency *= 3
        elif ft == "hallucination":
            confidence = clip(rng.gauss(0.45, 0.12))
            tokens = int(tokens * 2.5)
        elif ft == "wrong_tool":
            tool = rng.choice([t for t in ALL_TOOLS if t not in EXPECTED_TOOLS[stype]])
        elif ft == "silent_corruption":
            confidence = clip(rng.gauss(0.78, 0.07))   # very weak signal
        out = (true_out + rng.randint(1, 999)) % 1000

    record = {
        "idx": idx, "type": stype, "tool": tool,
        "latency_ms": round(latency, 1), "tokens": tokens,
        "confidence": round(confidence, 3),
        "retrieval_score": round(retrieval_score, 3),
        "error": error, "output": out,
        "checkpoint": {"value": state["value"]},  # state BEFORE this step (observable)
    }
    new_state = {"value": out, "corrupted": state["corrupted"] or corrupt_now}
    return record, new_state


def run_agent(task, fault=None, start_step=0, checkpoint=None):
    """Run (or replay) the agent. Pass start_step + checkpoint to resume mid-run.
    Pass fault=None to test a 'fixed' execution."""
    value = task["start"] if checkpoint is None else checkpoint["value"]
    # a resumed run is only 'corrupted' if the fault happened before start_step
    corrupted = bool(fault and fault["step"] < start_step)
    state = {"value": value, "corrupted": corrupted}
    steps = []
    for idx in range(start_step, len(task["step_types"])):
        rec, state = execute_step(task, idx, state, fault)
        steps.append(rec)
    success = state["value"] == task["expected"]
    return steps, success