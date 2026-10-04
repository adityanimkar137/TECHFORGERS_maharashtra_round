import api, { USE_MOCK, delay } from './api.js'
import { mockRuns, mockAlternativeRuns, dashboardStats } from '../data/mockRuns.js'

const all = () => [...mockRuns, ...mockAlternativeRuns]

// ---- adapters: backend (snake_case, int ids, text columns) -> UI shape ----
const parse = (v) => {
  if (v == null || v === '') return {}
  try { const j = JSON.parse(v); return typeof j === 'object' && j !== null ? j : { value: j } } catch { return { text: v } }
}
const runStatus = (s = '') => {
  s = s.toLowerCase()
  if (s.includes('fail') || s.includes('error')) return 'FAILED'
  if (s.includes('run') || s.includes('progress') || s.includes('pending')) return 'RUNNING'
  return 'SUCCESS'
}
const stepStatus = (s = '') => {
  s = s.toLowerCase()
  if (s.includes('fail') || s.includes('error')) return 'failed'
  if (s.includes('run') || s.includes('progress')) return 'running'
  return 'ok'
}
export const mapRun = (r) => ({
  id: String(r.id), agent: 'Agent', task: r.task, status: runStatus(r.status), duration: null,
  createdAt: r.created_at || null, steps: [], stepCount: null, failure: r.failure_reason || null, finalOutput: r.final_output || null,
})
export const mapStep = (s) => ({
  id: `step-${s.step_number}`, index: s.step_number, name: s.name, tool: '—', status: stepStatus(s.status), duration: null,
  timestamp: s.created_at ? new Date(s.created_at).toLocaleTimeString('en-IN') : '—',
  checkpoint: `ckpt-${s.step_number}`, dependencies: s.step_number > 1 ? [`step-${s.step_number - 1}`] : [],
  input: parse(s.input_data), output: parse(s.output_data), expected: null, error: s.error_message || null,
})

// The backend has no stats endpoint, so aggregate the run list on the client.
function computeStats(runs) {
  const byDay = {}; const reasons = {}
  runs.forEach((r) => {
    const d = r.createdAt ? new Date(r.createdAt).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : 'All'
    byDay[d] ??= { day: d, success: 0, failed: 0 }
    if (r.status === 'FAILED') { byDay[d].failed++; const k = r.failure || 'Unknown'; reasons[k] = (reasons[k] || 0) + 1 }
    else if (r.status === 'SUCCESS') byDay[d].success++
  })
  const failed = runs.filter((r) => r.status === 'FAILED').length
  return {
    totalRuns: runs.length, successfulRuns: runs.filter((r) => r.status === 'SUCCESS').length, failedRuns: failed,
    diagnosedFailures: null, replayTests: null,
    executionSeries: Object.values(byDay).reverse(),
    failureDistribution: Object.entries(reasons).map(([name, value]) => ({ name, value })),
  }
}

// GET /runs/   (needs the list endpoint added to the backend, see README)
export async function getRuns() {
  if (USE_MOCK) { await delay(); return mockRuns }
  return (await api.get('/runs/')).data.map(mapRun)
}
// GET /runs/{id} + GET /runs/{id}/steps/
export async function getRun(runId) {
  if (USE_MOCK) {
    await delay(250)
    const r = all().find((x) => x.id === runId)
    if (!r) throw new Error(`Run ${runId} not found`)
    return r
  }
  const [run, steps] = await Promise.all([api.get(`/runs/${runId}`), api.get(`/runs/${runId}/steps/`)])
  const mapped = steps.data.map(mapStep)
  return { ...mapRun(run.data), steps: mapped, stepCount: mapped.length }
}
export async function getDashboardStats() {
  if (USE_MOCK) { await delay(); return dashboardStats }
  return computeStats(await getRuns())
}
