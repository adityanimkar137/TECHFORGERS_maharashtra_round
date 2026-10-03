import { Play, RotateCcw } from 'lucide-react'
import JsonViewer from '../trace/JsonViewer.jsx'

export default function ReplayPanel({ state, loadingState, onReplay, onRun, running, canRun }) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-medium">Previous state at checkpoint</h2>
        <button className="btn" onClick={onReplay} disabled={loadingState || running}><RotateCcw size={14} className={loadingState ? 'animate-spin' : ''} />Replay from checkpoint</button>
      </div>
      {state ? <JsonViewer data={state} /> : <p className="text-sm text-muted py-6 text-center">Replay from the checkpoint to load the agent state, then choose a strategy.</p>}
      <button className="btn btn-primary mt-4" onClick={onRun} disabled={!canRun || running}><Play size={14} />{running ? 'Running…' : 'Run alternative'}</button>
    </div>
  )
}
