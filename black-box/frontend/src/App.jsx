import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Runs from './pages/Runs.jsx'
import RunDetails from './pages/RunDetails.jsx'
import Diagnosis from './pages/Diagnosis.jsx'
import Replay from './pages/Replay.jsx'
import Comparison from './pages/Comparison.jsx'
import Settings from './pages/Settings.jsx'
import NotFound from './pages/NotFound.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/runs" element={<Runs />} />
        <Route path="/runs/:runId" element={<RunDetails />} />
        <Route path="/runs/:runId/diagnosis" element={<Diagnosis />} />
        <Route path="/runs/:runId/replay" element={<Replay />} />
        <Route path="/comparison/:originalRunId/:alternativeRunId" element={<Comparison />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
