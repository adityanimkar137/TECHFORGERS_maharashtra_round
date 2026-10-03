import { Link } from 'react-router-dom'
import { Eye } from 'lucide-react'
import RunStatusBadge from './RunStatusBadge.jsx'
import { fmtDate, fmtDuration } from '../../utils/format.js'

export default function RunRow({ run }) {
  return (
    <tr className="border-b border-line last:border-0 hover:bg-raised/50">
      <td className="px-4 py-3 font-mono text-xs"><Link className="text-accent hover:underline" to={`/runs/${run.id}`}>{run.id}</Link></td>
      <td className="px-4 py-3 text-sm">{run.agent}</td>
      <td className="px-4 py-3 text-sm max-w-xs truncate" title={run.task}>{run.task}</td>
      <td className="px-4 py-3"><RunStatusBadge status={run.status} /></td>
      <td className="px-4 py-3 text-sm font-mono">{fmtDuration(run.duration)}</td>
      <td className="px-4 py-3 text-sm font-mono">{run.stepCount}</td>
      <td className="px-4 py-3 text-sm text-muted">{run.failure || '—'}</td>
      <td className="px-4 py-3 text-sm text-muted whitespace-nowrap">{fmtDate(run.createdAt)}</td>
      <td className="px-4 py-3"><Link to={`/runs/${run.id}`} className="btn !py-1"><Eye size={14} />View</Link></td>
    </tr>
  )
}
