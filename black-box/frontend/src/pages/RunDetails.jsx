import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { Stethoscope, RotateCcw } from 'lucide-react'
import useAsync from '../hooks/useAsync.js'
import { getRun } from '../services/runsApi.js'
import { Loading, ErrorState, PageHeader } from '../components/layout/PageState.jsx'
import RunStatusBadge from '../components/runs/RunStatusBadge.jsx'
import ExecutionTimeline from '../components/trace/ExecutionTimeline.jsx'
import StepDetails from '../components/trace/StepDetails.jsx'
import { fmtDuration } from '../utils/format.js'

export default function RunDetails() {
  const { runId } = useParams()
  const [params] = useSearchParams()
  const { data: run, loading, error } = useAsync(() => getRun(runId), [runId])
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    if (!run) return
    const wanted = params.get('step')
    const first = run.steps.find((s) => s.status === 'suspicious') || run.steps.find((s) => s.status === 'failed')
    setSelected(wanted || first?.id || run.steps[0]?.id)
  }, [run]) // eslint-disable-line

  if (loading) return <Loading label="Loading execution trace…" />
  if (error) return <ErrorState error={error} />
  const failed = run.status === 'FAILED'
  return (
    <>
      <PageHeader title={run.id} subtitle={`${run.agent} · ${run.task}`}>
        {failed && <Link to={`/runs/${run.id}/diagnosis`} className="btn btn-primary"><Stethoscope size={14} />View AI diagnosis</Link>}
        {failed && <Link to={`/runs/${run.id}/replay`} className="btn"><RotateCcw size={14} />Replay</Link>}
      </PageHeader>
      <div className="flex gap-6 mb-5 items-center text-sm">
        <RunStatusBadge status={run.status} />
        <span className="text-muted">Duration <span className="text-ink font-mono">{fmtDuration(run.duration)}</span></span>
        <span className="text-muted">Steps <span className="text-ink font-mono">{run.stepCount}</span></span>
        {run.failure && <span className="text-bad">{run.failure}</span>}
      </div>
      <div className="grid lg:grid-cols-5 gap-5">
        <div className="lg:col-span-2"><h2 className="text-sm font-medium mb-3">Execution timeline</h2>
          <ExecutionTimeline steps={run.steps} selectedId={selected} onSelect={setSelected} /></div>
        <div className="lg:col-span-3"><StepDetails step={run.steps.find((s) => s.id === selected)} /></div>
      </div>
    </>
  )
}
