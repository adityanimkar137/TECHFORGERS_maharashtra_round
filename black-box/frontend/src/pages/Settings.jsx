import { PageHeader } from '../components/layout/PageState.jsx'
import { API_URL, USE_MOCK } from '../services/api.js'

const Row = ({ k, v }) => <div className="flex justify-between py-3 border-b border-line last:border-0 text-sm"><span className="text-muted">{k}</span><span className="font-mono">{v}</span></div>

export default function Settings() {
  return (
    <>
      <PageHeader title="Settings" subtitle="Connection and project configuration" />
      <div className="card px-4 max-w-2xl">
        <Row k="Project" v="shopping-assistant" />
        <Row k="API URL" v={API_URL} />
        <Row k="Data source" v={USE_MOCK ? 'Mock data' : 'FastAPI backend'} />
        <Row k="Failure threshold" v="50%" />
      </div>
      <p className="text-xs text-muted mt-3 max-w-2xl">Change VITE_API_URL and VITE_USE_MOCK in frontend/.env and restart the dev server to connect the backend.</p>
    </>
  )
}
