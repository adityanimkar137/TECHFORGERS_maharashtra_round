import api, { USE_MOCK } from './api.js'
import { getRun } from './runsApi.js'

// Real: GET /runs/{id}/compare/  -> { original_output, corrected_output, changed_step, explanation }
// The backend only recomputes the failed step, so the alternative run is built from the original:
// steps before the change stay as-is, the changed step becomes ok, later steps are marked skipped.
export async function getComparison(originalId, alternativeId) {
  if (USE_MOCK) {
    const [original, alternative] = await Promise.all([getRun(originalId), getRun(alternativeId)])
    return { original, alternative }
  }
  const [original, c] = await Promise.all([getRun(originalId), api.get(`/runs/${originalId}/compare/`).then((r) => r.data)])
  const steps = original.steps.map((s) => {
    if (s.index < c.changed_step) return s
    if (s.index === c.changed_step) return { ...s, status: 'ok', error: null, output: { result: c.corrected_output } }
    return { ...s, status: 'skipped', error: null }
  })
  const alternative = { ...original, id: `ALT-${alternativeId}`, status: 'SUCCESS', failure: null, steps, finalOutput: c.corrected_output }
  return { original: { ...original, finalOutput: c.original_output }, alternative, explanation: c.explanation }
}
