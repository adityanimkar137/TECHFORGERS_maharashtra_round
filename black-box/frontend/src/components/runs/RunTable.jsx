import RunRow from './RunRow.jsx'

const heads = ['Run ID', 'Agent', 'Task', 'Status', 'Duration', 'Steps', 'Failure', 'Created At', 'Action']

export default function RunTable({ runs }) {
  return (
    <div className="card overflow-x-auto">
      <table className="w-full min-w-[900px]">
        <thead><tr>{heads.map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
        <tbody>
          {runs.map((r) => <RunRow key={r.id} run={r} />)}
          {runs.length === 0 && <tr><td colSpan={9} className="px-4 py-10 text-center text-sm text-muted">No runs match these filters. Clear the search or change the status.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
