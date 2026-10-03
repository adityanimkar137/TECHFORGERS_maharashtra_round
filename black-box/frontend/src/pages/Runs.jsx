import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import useAsync from '../hooks/useAsync.js'
import { getRuns } from '../services/runsApi.js'
import { Loading, ErrorState, PageHeader } from '../components/layout/PageState.jsx'
import RunFilters from '../components/runs/RunFilters.jsx'
import RunTable from '../components/runs/RunTable.jsx'

export default function Runs() {
  const [params] = useSearchParams()
  const { data, loading, error } = useAsync(getRuns)
  const [filters, setFilters] = useState({ q: params.get('q') || '', status: params.get('status') || '', agent: '', sort: 'createdAt:desc' })

  // Keep filters in sync when the sidebar/topbar navigates with new query params.
  const key = params.toString()
  useMemo(() => setFilters((f) => ({ ...f, q: params.get('q') || '', status: params.get('status') || '' })), [key]) // eslint-disable-line

  const agents = useMemo(() => [...new Set((data || []).map((r) => r.agent))], [data])
  const rows = useMemo(() => {
    if (!data) return []
    const q = filters.q.toLowerCase()
    const [field, dir] = filters.sort.split(':')
    return data
      .filter((r) => (!filters.status || r.status === filters.status) && (!filters.agent || r.agent === filters.agent)
        && (!q || `${r.id} ${r.agent} ${r.task}`.toLowerCase().includes(q)))
      .sort((a, b) => ((a[field] ?? 0) > (b[field] ?? 0) ? 1 : -1) * (dir === 'asc' ? 1 : -1))
  }, [data, filters])

  if (loading) return <Loading />
  if (error) return <ErrorState error={error} />
  return (
    <>
      <PageHeader title="Executions" subtitle={`${rows.length} of ${data.length} runs`} />
      <RunFilters filters={filters} setFilters={setFilters} agents={agents} />
      <RunTable runs={rows} />
    </>
  )
}
