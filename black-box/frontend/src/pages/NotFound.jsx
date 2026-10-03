import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="card p-10 text-center max-w-md mx-auto mt-16">
      <div className="font-mono text-3xl text-muted">404</div>
      <p className="text-sm text-muted mt-2">This page doesn't exist. Go back to the dashboard to continue.</p>
      <Link to="/dashboard" className="btn btn-primary mt-4">Back to dashboard</Link>
    </div>
  )
}
