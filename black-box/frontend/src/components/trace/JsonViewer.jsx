const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

function highlight(json) {
  return esc(json).replace(
    /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|(-?\d+\.?\d*(?:[eE][+-]?\d+)?)/g,
    (m, str, colon, lit, num) => {
      if (str) return colon ? `<span class="text-accent">${str}</span>${colon}` : `<span class="text-ok">${str}</span>`
      if (lit) return `<span class="text-warn">${lit}</span>`
      if (num) return `<span class="text-warn">${num}</span>`
      return m
    }
  )
}

export default function JsonViewer({ data, label, tone }) {
  const empty = data == null || (typeof data === 'object' && Object.keys(data).length === 0)
  return (
    <div>
      {label && <div className="text-xs text-muted mb-1.5">{label}</div>}
      <pre className={`font-mono text-xs leading-relaxed bg-base border rounded-md p-3 overflow-x-auto ${tone || 'border-line'}`}>
        {empty ? <span className="text-muted">No data</span> : <code dangerouslySetInnerHTML={{ __html: highlight(JSON.stringify(data, null, 2)) }} />}
      </pre>
    </div>
  )
}
