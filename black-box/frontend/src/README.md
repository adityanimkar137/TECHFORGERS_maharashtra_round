# Black Box Frontend

React + Vite dashboard for diagnosing and replaying failed AI-agent runs. It runs on mock data and is ready to be pointed at the FastAPI backend.

## 1. Installation
```bash
cd frontend
npm install
```

## 2. Running
```bash
npm run dev      # http://localhost:5173
npm run build    # production build
```

## 3. Folder structure
- `src/pages/` route pages (Dashboard, Runs, RunDetails, Diagnosis, Replay, Comparison, Settings, NotFound)
- `src/components/` grouped by feature: layout, dashboard, runs, trace, diagnosis, replay, comparison
- `src/services/` API layer. UI components never import mock data directly
- `src/data/` mock runs, diagnosis and replay options
- `src/hooks/useAsync.js` loading/error helper; `src/utils/format.js` formatters

## 4. Mock data
`src/data/mockRuns.js` has 10 runs (5 success, 4 failed, 1 running). `RUN-1024` fails at **Step 3 — Extract Product Prices** (87% in `mockDiagnosis.js`). Running a *Validated* or *Strict* strategy from the Replay page produces `RUN-1031`, which succeeds. Demo path:
Dashboard → Executions → RUN-1024 → Diagnosis → Replay from this step → Replay from checkpoint → Run alternative → Compare.

## 5. Backend integration
`.env`:
```
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=false   # true = demo data, no backend needed
```
Real endpoints used (note the trailing slashes):

| UI action | Backend call |
|---|---|
| Run list | `GET /runs/` (must be added, see below) |
| Run + trace | `GET /runs/{id}` and `GET /runs/{id}/steps/` |
| Diagnosis | `POST /runs/{id}/diagnose/` |
| Replay from checkpoint | `POST /runs/{id}/replay/` `{start_step_number}` |
| Run alternative | `POST /runs/{id}/alternative/` |
| Comparison | `GET /runs/{id}/compare/` |

Backend changes needed: add CORS in `app/main.py`, add `GET /runs/` in `routers/runs.py`, and add `created_at` to `RunResponse`.
Not provided by the backend yet (UI hides or shows a dash): failure probabilities, confidence, related runs, durations, agent name, strategy/params for alternatives.

Seed demo data into the real backend: `python scripts/seed_demo.py`
