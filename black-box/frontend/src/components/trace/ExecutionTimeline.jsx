import ExecutionStep from './ExecutionStep.jsx'

export default function ExecutionTimeline({ steps, selectedId, onSelect }) {
  return (
    <ol>
      {steps.map((s, i) => (
        <ExecutionStep key={s.id} step={s} last={i === steps.length - 1} selected={s.id === selectedId} onClick={() => onSelect(s.id)} />
      ))}
    </ol>
  )
}
