# Black Box - Replay Engine

This module is responsible for checkpointed replay and comparison of AI-agent executions.

## What it does

1. Loads an execution trace.
2. Creates a checkpoint at a selected step.
3. Replays only from that step onward.
4. Allows a step's output to be modified.
5. Runs the remaining steps using a simple demo executor.
6. Compares the original run with the replay.
7. Returns JSON-friendly results for the backend/frontend.

## Project structure

```text
replay-engine/
├── app/
│   ├── __init__.py
│   ├── engine.py
│   ├── models.py
│   ├── checkpoint/
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── replay/
│   │   ├── __init__.py
│   │   └── runner.py
│   └── comparison/
│       ├── __init__.py
│       └── comparator.py
├── data/
│   └── sample_run.json
├── tests/
│   └── test_replay_engine.py
├── demo.py
├── requirements.txt
└── README.md
```

## Run the demo

```bash
python demo.py
```

The demo:
- loads a failed run
- creates a checkpoint before Step 3
- changes Step 3's output
- replays Steps 3 onward
- compares original and replayed executions

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Integration idea

The backend team can import:

```python
from app.engine import ReplayEngine
```

Example:

```python
engine = ReplayEngine()

result = engine.replay(
    run=run_data,
    start_step=3,
    modified_outputs={3: "45999"}
)

comparison = engine.compare(run_data, result)
```

The engine returns normal Python dictionaries, so they can be directly converted to JSON in FastAPI/Flask/Node integration.

## Important design rule

The replay engine does NOT contain UI code, database code, or AI diagnosis code.

That separation is intentional:

- Frontend team -> UI
- Backend team -> API/database
- AI team -> failure diagnosis
- Replay team -> checkpoint/replay/comparison

This reduces Git merge conflicts.
