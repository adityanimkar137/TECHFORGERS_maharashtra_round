import { Link } from 'react-router-dom'

export default function RelatedRuns({ title, runs, tone }) {
  return (
    <div className="card p-4">
      <h2 className="text-sm font-medium mb-3">{title}</h2>
      <ul className="space-y-2.5">
        {runs.map((r) => (
          <li key={r.id} className="flex items-start gap-3">
            <span className={`w-1.5 h-1.5 rounded-full mt-2 ${tone}`} />
            <div><Link to={`/runs/${r.id}`} className="font-mono text-xs text-accent hover:underline">{r.id}</Link><div className="text-sm text-muted">{r.note}</div></div>
          </li>
        ))}
      </ul>
    </div>
  )
}
