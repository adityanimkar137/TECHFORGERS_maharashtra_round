const styles = {
  SUCCESS: 'text-ok bg-ok/10 border-ok/30',
  FAILED: 'text-bad bg-bad/10 border-bad/30',
  RUNNING: 'text-accent bg-accent/10 border-accent/30',
}
export default function RunStatusBadge({ status }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-medium ${styles[status]}`}>
      <span className={`w-1.5 h-1.5 rounded-full bg-current ${status === 'RUNNING' ? 'animate-pulse' : ''}`} />{status}
    </span>
  )
}
