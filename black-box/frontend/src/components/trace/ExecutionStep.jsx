import { CheckCircle2, XCircle, AlertTriangle, Circle, Loader2 } from 'lucide-react'
import { fmtDuration } from '../../utils/format.js'

export const stepMeta = {
  ok: { icon: CheckCircle2, color: 'text-ok', label: '' },
  suspicious: { icon: AlertTriangle, color: 'text-warn', label: 'SUSPICIOUS' },
  failed: { icon: XCircle, color: 'text-bad', label: 'FAILED' },
  skipped: { icon: Circle, color: 'text-muted', label: 'SKIPPED' },
  running: { icon: Loader2, color: 'text-accent', label: 'RUNNING' },
}

export default function ExecutionStep({ step, selected, last, onClick }) {
  const { icon: Icon, color, label } = stepMeta[step.status]
  return (
    <li className="relative pl-10">
      {!last && <span className="absolute left-[15px] top-8 bottom-[-8px] w-px bg-line" />}
      <Icon size={20} className={`absolute left-1.5 top-3 ${color} ${step.status === 'running' ? 'animate-spin' : ''}`} />
      <button onClick={onClick}
        className={`w-full text-left rounded-md border px-3 py-2.5 mb-2 transition-colors ${selected ? 'border-accent bg-raised' : 'border-line hover:bg-raised/60'}`}>
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs text-muted">Step {step.index}</span>
          <span className="text-xs font-mono text-muted">{fmtDuration(step.duration)}</span>
        </div>
        <div className="text-sm font-medium">{step.name}</div>
        {label && <div className={`text-xs font-medium mt-0.5 ${color}`}>{label}</div>}
      </button>
    </li>
  )
}
