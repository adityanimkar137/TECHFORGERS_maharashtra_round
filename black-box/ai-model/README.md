# Black Box: AI model for failure diagnosis

Finds the step that caused an agent run to fail, explains why, and tests fixes
by replaying from a checkpoint instead of re-running everything.

## How it works
1. **Execution data** (`dataset/`): a simulated agent records every step (tool, latency,
   tokens, confidence, retrieval score, errors, a state checkpoint). Faults are injected
   at a known step and propagate downstream as mild degradation.
2. **Diagnosis** (`training/`, `model/`): two detectors are combined.
   - Supervised model: logistic regression that scores each step as "root cause".
   - Label-free anomaly detector: scores how far each step deviates from successful runs.
   - Hybrid: anomaly first, supervised model as fallback.
3. **Explanation** (`predict.py`): evidence list per diagnosis (metrics vs. normal).
4. **Checkpointed replay and alternative execution** (`predict.py`, `search_fix.py`):
   resume from the suspect step's checkpoint with a fix applied; try the top 3 suspects.
5. **Evaluation** (`evaluate.py`): top-1 / top-3 localization vs. chance, including
   leave-one-fault-out for unseen fault types.
6. **Report** (`generate_report.py`): writes `report.html` with results and example runs.

## Run
```
pip install -r requirements.txt
python dataset/generate_traces.py
python training/train.py
python evaluate.py
python search_fix.py
python generate_report.py
```

## Results (simulated agent, held-out runs)
Localization, fault type never seen in training:

| Fault | Supervised | Label-free | Hybrid | Chance |
|---|---|---|---|---|
| bad_retrieval | 21% | 91% | 90% | 11% |
| hallucination | 22% | 99% | 99% | 11% |
| tool_error | 6% | 97% | 97% | 11% |
| wrong_tool | 100% | 100% | 100% | 12% |
| silent_corruption | 14% | 13% | 13% | 12% |

Search-and-replay (fix top-3 suspects in order):

| Fault | Fixed 1st try | Fixed within 3 | Steps re-run vs 1 full re-run |
|---|---|---|---|
| bad_retrieval | 92% | 100% | 81% |
| hallucination | 100% | 100% | 73% |
| tool_error | 100% | 100% | 57% |
| wrong_tool | 100% | 100% | 64% |
| silent_corruption | 20% | 59% | 142% |
| equal-weighted average | 82% | 92% | 83% |

## Limitations
- Data is simulated. Detector features were designed around the signals the simulator
  injects, so results show the method works when faults leave observable traces,
  not that it reaches these numbers on a real agent.
- `silent_corruption` (a faulty step that looks normal) is not detectable from step
  metrics. Fixes would need intermediate-output checks.
- A "fix" here removes the injected fault, and success is checked against a known
  answer. A real system needs a fix generator and a verifier.
- The supervised model alone does not generalize to unseen fault types, which is why
  the label-free detector exists.