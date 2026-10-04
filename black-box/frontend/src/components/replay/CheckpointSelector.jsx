export default function CheckpointSelector({ run, value, onChange }) {
  return (
    <div className="card p-4">
      <div className="text-xs text-muted">Original run</div>
      <div className="font-mono text-sm mt-0.5">{run.id}</div>
      <label className="text-xs text-muted block mt-4 mb-1.5" htmlFor="ckpt">Checkpoint</label>
      <select id="ckpt" className="input w-full" value={value} onChange={(e) => onChange(e.target.value)}>
        {run.steps.map((s) => <option key={s.id} value={s.checkpoint}>Step {s.index} — {s.name}</option>)}
      </select>
    </div>
  )
}
