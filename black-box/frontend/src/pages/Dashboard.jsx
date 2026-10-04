import { Link } from 'react-router-dom'
import { Activity, CheckCircle2, XCircle, Percent, Stethoscope, FlaskConical, ListChecks, AlertOctagon, RotateCcw, GitCompare } from 'lucide-react'
import useAsync from '../hooks/useAsync.js'
import { getDashboardStats, getRuns } from '../services/runsApi.js'
import { links } from '../services/api.js'
import { Loading, ErrorState, PageHeader } from '../components/layout/PageState.jsx'
import StatCard from '../components/dashboard/StatCard.jsx'
import ExecutionChart from '../components/dashboard/ExecutionChart.jsx'
import FailureDistribution from '../components/dashboard/FailureDistribution.jsx'
import RecentRuns from '../components/dashboard/RecentRuns.jsx'

const actions = [
  { to: '/runs?status=FAILED', label: 'Review failed runs', icon: AlertOctagon },
  { to: links.diagnose, label: 'Diagnose a failed run', icon: ListChecks },
  { to: links.replay, label: 'Replay from checkpoint', icon: RotateCcw },
  { to: links.compare, label: 'View latest comparison', icon: GitCompare },
]

export default function Dashboard() {
  const stats = useAsync(getDashboardStats)
  const runs = useAsync(getRuns)
  if (stats.loading || runs.loading) return <Loading />
  if (stats.error || runs.error) return <ErrorState error={stats.error || runs.error} />
  const s = stats.data
  const rate = s.totalRuns ? ((s.failedRuns / s.totalRuns) * 100).toFixed(1) : '0.0'
  return (
    <>
      <PageHeader title="Dashboard" subtitle="Agent execution health for shopping-assistant" />
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 mb-5">
        <StatCard label="Total runs" value={s.totalRuns.toLocaleString()} icon={Activity} />
        <StatCard label="Successful" value={s.successfulRuns.toLocaleString()} tone="text-ok" icon={CheckCircle2} />
        <StatCard label="Failed" value={s.failedRuns} tone="text-bad" icon={XCircle} />
        <StatCard label="Failure rate" value={`${rate}%`} tone="text-warn" icon={Percent} />
        <StatCard label="Diagnosed failures" value={s.diagnosedFailures ?? '—'} hint={s.diagnosedFailures != null ? `${Math.round((s.diagnosedFailures / s.failedRuns) * 100)}% of failures` : undefined} icon={Stethoscope} />
        <StatCard label="Replay tests" value={s.replayTests ?? '—'} icon={FlaskConical} />
      </div>
      <div className="grid lg:grid-cols-3 gap-4 mb-5">
        <div className="lg:col-span-2"><ExecutionChart data={s.executionSeries} /></div>
        <FailureDistribution data={s.failureDistribution} />
      </div>
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1"><RecentRuns title="Recent executions" runs={runs.data.slice(0, 5)} viewAllTo="/runs" /></div>
        <div className="lg:col-span-1"><RecentRuns title="Recent failures" runs={runs.data.filter((r) => r.status === 'FAILED').slice(0, 5)} viewAllTo="/runs?status=FAILED" /></div>
        <div className="card">
          <div className="px-4 py-3 border-b border-line text-sm font-medium">Quick actions</div>
          <div className="p-3 space-y-2">
            {actions.map(({ to, label, icon: Icon }) => <Link key={label} to={to} className="btn w-full"><Icon size={15} />{label}</Link>)}
          </div>
        </div>
      </div>
    </>
  )
}
