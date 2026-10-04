import { Link, useParams } from 'react-router-dom'
import { ArrowDown, ArrowUp } from 'lucide-react'
import useAsync from '../hooks/useAsync.js'
import { getComparison } from '../services/comparisonApi.js'
import { Loading, ErrorState, PageHeader } from '../components/layout/PageState.jsx'
import ComparisonCard from '../components/comparison/ComparisonCard.jsx'
import ComparisonTable from '../components/comparison/ComparisonTable.jsx'
import DifferenceViewer from '../components/comparison/DifferenceViewer.jsx'
import JsonViewer from '../components/trace/JsonViewer.jsx'

export default function Comparison() {
  const { originalRunId, alternativeRunId } = useParams()
  const { data, loading, error } = useAsync(() => getComparison(originalRunId, alternativeRunId), [originalRunId, alternativeRunId])
  if (loading) return <Loading label="Comparing runs…" />
  if (error) return <ErrorState error={error} />
  const { original: o, alternative: a } = data
  const diff = a.duration - o.duration
  const last = (r) => (r.finalOutput != null ? { result: r.finalOutput } : r.steps[r.steps.length - 1].output)
  const changedStatus = `${o.status} → ${a.status}`
  const fixedSteps = o.steps.filter((s, i) => s.status !== a.steps[i].status).length
  return (
    <>
      <PageHeader title="Comparison" subtitle={<><Link className="text-accent hover:underline" to={`/runs/${o.id}`}>{o.id}</Link> vs <Link className="text-accent hover:underline" to={`/runs/${a.id}`}>{a.id}</Link></>} />
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <ComparisonCard label="Original" run={o} summary={o.failure || o.finalOutput || 'Original run'} />
        <ComparisonCard label="Alternative" run={a} summary={a.finalOutput || (a.status === 'SUCCESS' ? 'Correct product prices' : a.failure)} />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        {[['Status changed', changedStatus], ['Steps changed', fixedSteps], ['Duration difference', `${diff >= 0 ? '+' : ''}${diff.toFixed(1)}s`], ['Final result', a.status === 'SUCCESS' ? 'Correct' : 'Still incorrect']].map(([k, v]) => (
          <div key={k} className="card p-3"><div className="text-xs text-muted">{k}</div><div className="font-mono text-sm mt-1 flex items-center gap-1">{k === 'Duration difference' && (diff >= 0 ? <ArrowUp size={14} className="text-warn" /> : <ArrowDown size={14} className="text-ok" />)}{v}</div></div>
        ))}
      </div>
      {data.explanation && <div className="card p-4 mb-4 text-sm">{data.explanation}</div>}
      <h2 className="text-sm font-medium mb-2">Step-by-step differences</h2>
      <div className="mb-5"><ComparisonTable original={o} alternative={a} /></div>
      <h2 className="text-sm font-medium mb-2">Changed inputs and outputs</h2>
      <div className="mb-5"><DifferenceViewer original={o} alternative={a} /></div>
      <h2 className="text-sm font-medium mb-2">Final result</h2>
      <div className="grid md:grid-cols-2 gap-4">
        <JsonViewer label="Original" data={last(o)} tone="border-bad/40" />
        <JsonViewer label="Alternative" data={last(a)} tone="border-ok/40" />
      </div>
    </>
  )
}
