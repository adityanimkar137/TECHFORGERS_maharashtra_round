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
Set `frontend/.env`:
```
VITE_API_URL=http://localhost:8000/api
VITE_USE_MOCK=false
```
| Function | Endpoint |
|---|---|
| `getRuns` (runsApi.js) | `GET /runs` |
| `getRun` | `GET /runs/{run_id}` |
| `getDashboardStats` | `GET /stats` (suggested) |
| `getDiagnosis` (diagnosisApi.js) | `GET /runs/{run_id}/diagnosis` |
| `replayFromCheckpoint` (replayApi.js) | `POST /runs/{run_id}/replay` body `{checkpoint}` |
| `runAlternative` | `POST /runs/{run_id}/alternative` body `{checkpoint, strategy, params}` returns `{alternativeRunId, status}` |
| `getComparison` (comparisonApi.js) | `GET /comparison/{original_id}/{alternative_id}` returns `{original, alternative}` |

Response shapes follow the objects in `src/data/`. Run objects use `id, agent, task, status, duration, createdAt, stepCount, failure, steps[]`.
