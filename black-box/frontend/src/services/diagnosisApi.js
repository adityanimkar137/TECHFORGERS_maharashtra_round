import api, { USE_MOCK, delay } from './api.js'
import { mockDiagnosis } from '../data/mockDiagnosis.js'
import { mockRuns } from '../data/mockRuns.js'

// Real: POST /runs/{id}/diagnose/
// probability, confidence, probabilities[], related_* are optional: the UI shows them as soon as the backend sends them.
export async function getDiagnosis(runId) {
  if (!USE_MOCK) {
    const d = (await api.post(`/runs/${runId}/diagnose/`)).data
    return {
      runId,
      primary: { stepIndex: d.failed_step_number, stepName: d.failed_step_name, probability: d.probability ?? null, confidence: d.confidence ?? null },
      reason: d.reason,
      probabilities: d.probabilities ?? [],
      evidence: d.evidence ?? [],
      relatedSuccessful: d.related_successful ?? [],
      relatedFailed: d.related_failed ?? [],
    }
  }
  await delay(600)
  if (runId === mockDiagnosis.runId) return mockDiagnosis
  const run = mockRuns.find((r) => r.id === runId)
  if (!run) throw new Error(`Run ${runId} not found`)
  const bad = run.steps.findIndex((s) => s.status === 'failed' || s.status === 'suspicious')
  const idx = bad === -1 ? 0 : bad
  return {
    runId,
    primary: { stepIndex: idx + 1, stepName: run.steps[idx].name, probability: 0.71, confidence: 'Medium' },
    probabilities: run.steps.map((s, i) => ({ step: `Step ${i + 1}`, name: s.name, probability: i === idx ? 0.71 : 0.06 + (i % 3) * 0.05 })),
    evidence: ['Step ended with an error', 'Output differs from successful runs'],
    relatedSuccessful: [{ id: 'RUN-1023', note: 'Same agent, completed successfully' }],
    relatedFailed: [{ id: 'RUN-1022', note: 'Similar failure pattern' }],
  }
}
