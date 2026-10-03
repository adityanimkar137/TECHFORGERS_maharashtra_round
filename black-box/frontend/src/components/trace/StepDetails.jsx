import JsonViewer from './JsonViewer.jsx'
import { stepMeta } from './ExecutionStep.jsx'
import { fmtDuration } from '../../utils/format.js'

const Meta = ({ k, v }) => (
  <div><div className="text-xs text-muted">{k}</div><div className="text-sm font-mono mt-0.5 break-words">{v}</div></div>
)

export default function StepDetails({ step }) {
  if (!step) return <div className="card p-8 text-sm text-muted text-center">Select a step to inspect its input, output and errors.</div>
  const m = stepMeta[step.status]
  return (
    <div className="card p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Step {step.index}: {step.name}</h2>
        <span className={`text-xs font-medium ${m.color}`}>{m.label || 'OK'}</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Meta k="Tool" v={step.tool} />
        <Meta k="Duration" v={fmtDuration(step.duration)} />
        <Meta k="Timestamp" v={step.timestamp} />
        <Meta k="Checkpoint" v={step.checkpoint} />
      </div>
      <Meta k="Dependencies" v={step.dependencies.length ? step.dependencies.join(', ') : 'None'} />
      {step.error && <div className="border border-bad/40 bg-bad/10 text-bad text-sm rounded-md px-3 py-2"><span className="font-medium">Error: </span>{step.error}</div>}
      <JsonViewer label="Input" data={step.input} />
      <JsonViewer label="Output" data={step.output} tone={step.status === 'suspicious' || step.status === 'failed' ? 'border-warn/50' : undefined} />
      {step.expected && <JsonViewer label="Expected output" data={step.expected} tone="border-ok/40" />}
    </div>
  )
}
