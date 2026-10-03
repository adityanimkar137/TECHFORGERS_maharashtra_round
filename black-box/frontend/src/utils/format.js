export const fmtDuration = (s) => (s == null ? '—' : `${s.toFixed(1)}s`)
export const fmtDate = (iso) =>
  !iso ? '—' : new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
export const pct = (n) => `${Math.round(n * 100)}%`
