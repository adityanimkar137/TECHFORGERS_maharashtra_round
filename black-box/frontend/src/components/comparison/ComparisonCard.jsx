import RunStatusBadge from '../runs/RunStatusBadge.jsx'
import { fmtDuration } from '../../utils/format.js'

export default function ComparisonCard({ label, run, summary }) {
  return (
    <div className={`card p-4 border-t-2 ${run.status === 'SUCCESS' ? 'border-t-ok' : 'border-t-bad'}`}>
      <div className="flex items-center justify-between"><span className="text-xs text-muted">{label}</span><RunStatusBadge status={run.status} /></div>
      <div className="font-mono text-sm mt-2">{run.id}</div>
      <div className="text-sm mt-1">{summary}</div>
      <div className="text-xs text-muted mt-2 font-mono">{fmtDuration(run.duration)} · {run.stepCount} steps</div>
    </div>
  )
}
