import { stepMeta } from '../trace/ExecutionStep.jsx'
import { fmtDuration } from '../../utils/format.js'

const Cell = ({ s }) => {
  const m = stepMeta[s.status]; const Icon = m.icon
  return <div className="flex items-center gap-2 text-sm"><Icon size={16} className={m.color} />Step {s.index} <span className="text-muted font-mono text-xs ml-auto">{fmtDuration(s.duration)}</span></div>
}

export default function ComparisonTable({ original, alternative }) {
  return (
    <div className="card overflow-x-auto">
      <table className="w-full min-w-[560px]">
        <thead><tr><th className="th">Step</th><th className="th">Original</th><th className="th">Alternative</th><th className="th">Change</th></tr></thead>
        <tbody>
          {original.steps.map((o, i) => {
            const a = alternative.steps[i]; const changed = o.status !== a.status
            return (
              <tr key={o.id} className="border-b border-line last:border-0">
                <td className="px-4 py-3 text-sm">{o.name}</td>
                <td className="px-4 py-3"><Cell s={o} /></td>
                <td className="px-4 py-3"><Cell s={a} /></td>
                <td className="px-4 py-3 text-xs">{changed ? <span className="text-ok">{o.status} → {a.status}</span> : <span className="text-muted">Unchanged</span>}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
