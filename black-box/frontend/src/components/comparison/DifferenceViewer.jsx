import JsonViewer from '../trace/JsonViewer.jsx'

// Shows only steps whose input or output changed between the two runs.
export default function DifferenceViewer({ original, alternative }) {
  const diffs = original.steps
    .map((o, i) => ({ o, a: alternative.steps[i] }))
    .filter(({ o, a }) => JSON.stringify(o.input) !== JSON.stringify(a.input) || JSON.stringify(o.output) !== JSON.stringify(a.output))
  return (
    <div className="space-y-4">
      {diffs.length === 0 && <div className="card p-6 text-sm text-muted text-center">No input or output differences.</div>}
      {diffs.map(({ o, a }) => (
        <div key={o.id} className="card p-4">
          <h3 className="text-sm font-medium mb-3">Step {o.index}: {o.name}</h3>
          <div className="grid md:grid-cols-2 gap-4">
            {JSON.stringify(o.input) !== JSON.stringify(a.input) && <>
              <JsonViewer label="Original input" data={o.input} tone="border-bad/40" />
              <JsonViewer label="Alternative input" data={a.input} tone="border-ok/40" />
            </>}
            <JsonViewer label="Original output" data={o.output} tone="border-bad/40" />
            <JsonViewer label="Alternative output" data={a.output} tone="border-ok/40" />
          </div>
        </div>
      ))}
    </div>
  )
}
