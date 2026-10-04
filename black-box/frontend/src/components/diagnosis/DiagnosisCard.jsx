import { Link } from 'react-router-dom'
import { Search, RotateCcw } from 'lucide-react'
import { pct } from '../../utils/format.js'

export default function DiagnosisCard({ runId, primary, reason }) {
  return (
    <div className="card p-5 border-l-2 border-l-bad">
      <div className="text-xs text-muted">Primary diagnosis</div>
      <h2 className="text-lg font-semibold mt-1">Step {primary.stepIndex}: {primary.stepName}</h2>
      {reason && <p className="text-sm text-muted mt-2">{reason}</p>}
      {(primary.probability != null || primary.confidence) && (
        <div className="flex gap-8 mt-4">
          {primary.probability != null && <div><div className="text-xs text-muted">Failure probability</div><div className="text-2xl font-mono font-semibold text-bad">{pct(primary.probability)}</div></div>}
          {primary.confidence && <div><div className="text-xs text-muted">Confidence</div><div className="text-2xl font-semibold">{primary.confidence}</div></div>}
        </div>
      )}
      <div className="flex flex-wrap gap-2 mt-5">
        <Link to={`/runs/${runId}?step=step-${primary.stepIndex}`} className="btn"><Search size={14} />Investigate step</Link>
        <Link to={`/runs/${runId}/replay`} className="btn btn-primary"><RotateCcw size={14} />Replay from this step</Link>
      </div>
    </div>
  )
}
