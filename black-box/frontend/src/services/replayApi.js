import api, { USE_MOCK, delay } from './api.js'
import { mockRuns } from '../data/mockRuns.js'
import { replayProgressSteps } from '../data/mockReplay.js'

const stepNumber = (checkpoint) => Number(String(checkpoint).split('-')[1])

// Real: POST /runs/{id}/replay/   body { start_step_number }
export async function replayFromCheckpoint(runId, checkpoint) {
  if (!USE_MOCK) {
    const r = (await api.post(`/runs/${runId}/replay/`, { start_step_number: stepNumber(checkpoint) })).data
    return { runId, checkpoint, state: { replay_id: r.id, start_step_number: r.start_step_number, status: r.status, replayed: (r.result || '').split('\n') } }
  }
  await delay(700)
  const run = mockRuns.find((r) => r.id === runId)
  const step = run?.steps.find((s) => s.checkpoint === checkpoint) || run?.steps[2]
  return { runId, checkpoint, state: { step: step.name, input: step.input, previous_output: step.output } }
}

// Real: POST /runs/{id}/alternative/   (no body: the backend picks the fix itself; strategy/params are ignored for now)
export async function runAlternative(runId, payload, onProgress) {
  if (!USE_MOCK) {
    onProgress?.(0)
    const r = (await api.post(`/runs/${runId}/alternative/`)).data
    onProgress?.(replayProgressSteps.length)
    return { alternativeRunId: String(r.id), status: r.status === 'alternative_completed' ? 'SUCCESS' : 'FAILED', result: r.result }
  }
  for (let i = 0; i < replayProgressSteps.length; i++) { onProgress?.(i); await delay(650) }
  onProgress?.(replayProgressSteps.length)
  return { alternativeRunId: payload.strategy === 'basic' ? 'RUN-1024' : 'RUN-1031', status: payload.strategy === 'basic' ? 'FAILED' : 'SUCCESS' }
}
