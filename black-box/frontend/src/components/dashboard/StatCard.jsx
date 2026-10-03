export default function StatCard({ label, value, hint, tone = 'text-ink', icon: Icon }) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between text-muted text-xs">{label}{Icon && <Icon size={15} />}</div>
      <div className={`mt-2 text-2xl font-semibold font-mono ${tone}`}>{value}</div>
      {hint && <div className="text-xs text-muted mt-1">{hint}</div>}
    </div>
  )
}
