import { Link } from 'react-router-dom'
import RunStatusBadge from '../runs/RunStatusBadge.jsx'
import { fmtDate } from '../../utils/format.js'

export default function RecentRuns({ title, runs, viewAllTo }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between px-4 py-3 border-b border-line">
        <h2 className="text-sm font-medium">{title}</h2>
        <Link to={viewAllTo} className="text-xs text-accent hover:underline">View all</Link>
      </div>
      <ul>
        {runs.map((r) => (
          <li key={r.id} className="border-b border-line last:border-0">
            <Link to={`/runs/${r.id}`} className="flex items-center gap-3 px-4 py-2.5 hover:bg-raised/50">
              <span className="font-mono text-xs text-accent w-20">{r.id}</span>
              <span className="flex-1 min-w-0"><span className="block text-sm truncate">{r.task}</span><span className="block text-xs text-muted">{r.agent} · {fmtDate(r.createdAt)}</span></span>
              <RunStatusBadge status={r.status} />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
