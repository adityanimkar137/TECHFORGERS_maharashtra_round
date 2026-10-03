import { Loader2, AlertTriangle } from 'lucide-react'

export function Loading({ label = 'Loading…' }) {
  return <div className="flex items-center gap-2 text-muted text-sm py-16 justify-center"><Loader2 className="animate-spin" size={16} />{label}</div>
}
export function ErrorState({ error }) {
  return (
    <div className="card p-6 flex items-center gap-3 text-sm">
      <AlertTriangle className="text-bad" size={18} />
      <span>{error?.message || 'Something went wrong. Check the run ID and try again.'}</span>
    </div>
  )
}
export function PageHeader({ title, subtitle, children }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
      <div><h1 className="text-lg font-semibold">{title}</h1>{subtitle && <p className="text-sm text-muted mt-0.5">{subtitle}</p>}</div>
      <div className="flex gap-2 flex-wrap">{children}</div>
    </div>
  )
}
