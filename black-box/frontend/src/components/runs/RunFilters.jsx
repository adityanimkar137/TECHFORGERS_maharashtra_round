import { Search } from 'lucide-react'

export default function RunFilters({ filters, setFilters, agents }) {
  const set = (k) => (e) => setFilters((f) => ({ ...f, [k]: e.target.value }))
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      <div className="relative flex-1 min-w-[220px]">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
        <input className="input w-full pl-9" placeholder="Search by run ID, agent or task" value={filters.q} onChange={set('q')} />
      </div>
      <select className="input" value={filters.status} onChange={set('status')} aria-label="Status filter">
        <option value="">All statuses</option><option>SUCCESS</option><option>FAILED</option><option>RUNNING</option>
      </select>
      <select className="input" value={filters.agent} onChange={set('agent')} aria-label="Agent filter">
        <option value="">All agents</option>{agents.map((a) => <option key={a}>{a}</option>)}
      </select>
      <select className="input" value={filters.sort} onChange={set('sort')} aria-label="Sort">
        <option value="createdAt:desc">Newest first</option><option value="createdAt:asc">Oldest first</option>
        <option value="duration:desc">Longest duration</option><option value="duration:asc">Shortest duration</option>
        <option value="stepCount:desc">Most steps</option>
      </select>
    </div>
  )
}
