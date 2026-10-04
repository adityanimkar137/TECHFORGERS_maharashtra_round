import { Check, Loader2, Circle } from 'lucide-react'

export default function ReplayProgress({ steps, current }) {
  const done = current >= steps.length
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-medium">{done ? 'Alternative run complete' : 'Running alternative'}</h2>
        <span className="text-xs font-mono text-muted">{Math.min(current, steps.length)}/{steps.length}</span>
      </div>
      <div className="h-1 bg-line rounded mb-4"><div className="h-1 bg-accent rounded transition-all duration-500" style={{ width: `${(Math.min(current, steps.length) / steps.length) * 100}%` }} /></div>
      <ul className="space-y-2">
        {steps.map((s, i) => (
          <li key={s} className={`flex items-center gap-2 text-sm ${i > current ? 'text-muted' : ''}`}>
            {i < current ? <Check size={15} className="text-ok" /> : i === current ? <Loader2 size={15} className="animate-spin text-accent" /> : <Circle size={15} />}{s}
          </li>
        ))}
      </ul>
    </div>
  )
}
