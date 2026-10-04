import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { GitCompare } from 'lucide-react'
import useAsync from '../hooks/useAsync.js'
import { getRun } from '../services/runsApi.js'
import { replayFromCheckpoint, runAlternative } from '../services/replayApi.js'
import { strategies, defaultParams, replayProgressSteps } from '../data/mockReplay.js'
import { Loading, ErrorState, PageHeader } from '../components/layout/PageState.jsx'
import CheckpointSelector from '../components/replay/CheckpointSelector.jsx'
import StrategySelector from '../components/replay/StrategySelector.jsx'
import ReplayPanel from '../components/replay/ReplayPanel.jsx'
import ReplayProgress from '../components/replay/ReplayProgress.jsx'
import RunStatusBadge from '../components/runs/RunStatusBadge.jsx'

export default function Replay() {
  const { runId } = useParams()
  const { data: run, loading, error } = useAsync(() => getRun(runId), [runId])
  const [checkpoint, setCheckpoint] = useState('')
  const [strategy, setStrategy] = useState('validated')
  const [params, setParams] = useState(defaultParams)
  const [state, setState] = useState(null)
  const [loadingState, setLoadingState] = useState(false)
  const [progress, setProgress] = useState(null) // null = idle
  const [result, setResult] = useState(null)

  useEffect(() => {
    if (!run) return
    const bad = run.steps.find((s) => s.status === 'suspicious') || run.steps.find((s) => s.status === 'failed') || run.steps[0]
    setCheckpoint(bad.checkpoint)
  }, [run])

  const onReplay = async () => {
    setLoadingState(true); setResult(null)
    try { setState((await replayFromCheckpoint(runId, checkpoint)).state) } finally { setLoadingState(false) }
  }
  const onRun = async () => {
    setProgress(0); setResult(null)
    try { setResult(await runAlternative(runId, { checkpoint, strategy, params }, setProgress)) } finally { /* keep progress visible */ }
  }

  if (loading) return <Loading />
  if (error) return <ErrorState error={error} />
  const running = progress !== null && progress < replayProgressSteps.length
  const ckptStep = run.steps.find((s) => s.checkpoint === checkpoint)
  return (
    <>
      <PageHeader title="Replay" subtitle={`Re-run ${run.id} from a checkpoint with a different strategy`}>
        <RunStatusBadge status={run.status} />
      </PageHeader>
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="space-y-4">
          <CheckpointSelector run={run} value={checkpoint} onChange={(c) => { setCheckpoint(c); setState(null) }} />
          <ReplayPanel state={state} loadingState={loadingState} onReplay={onReplay} onRun={onRun} running={running} canRun={!!state} />
        </div>
        <div className="space-y-4">
          <StrategySelector strategies={strategies} value={strategy} onChange={setStrategy} params={params} setParams={setParams} />
          {progress !== null && <ReplayProgress steps={replayProgressSteps} current={progress} />}
          {result && (
            <div className={`card p-4 border-l-2 ${result.status === 'SUCCESS' ? 'border-l-ok' : 'border-l-bad'}`}>
              <div className="flex items-center gap-3"><RunStatusBadge status={result.status} /><span className="font-mono text-sm">{result.alternativeRunId}</span></div>
              <p className="text-sm text-muted mt-2">
                {result.status === 'SUCCESS' ? `Step ${ckptStep?.index ?? 3} now produces correct prices and the final answer is correct.` : 'This strategy reproduced the original failure.'}
              </p>
              <Link to={`/comparison/${runId}/${result.alternativeRunId}`} className="btn btn-primary mt-3"><GitCompare size={14} />Compare original vs alternative</Link>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
