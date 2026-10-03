import { Link, useParams } from 'react-router-dom'
import useAsync from '../hooks/useAsync.js'
import { getDiagnosis } from '../services/diagnosisApi.js'
import { Loading, ErrorState, PageHeader } from '../components/layout/PageState.jsx'
import DiagnosisCard from '../components/diagnosis/DiagnosisCard.jsx'
import ProbabilityChart from '../components/diagnosis/ProbabilityChart.jsx'
import EvidenceList from '../components/diagnosis/EvidenceList.jsx'
import RelatedRuns from '../components/diagnosis/RelatedRuns.jsx'

export default function Diagnosis() {
  const { runId } = useParams()
  const { data: d, loading, error } = useAsync(() => getDiagnosis(runId), [runId])
  if (loading) return <Loading label="Analysing execution trace…" />
  if (error) return <ErrorState error={error} />
  const hasChart = d.probabilities.length > 0
  return (
    <>
      <PageHeader title="AI diagnosis" subtitle={<>Analysis of <Link className="text-accent hover:underline" to={`/runs/${runId}`}>run {runId}</Link></>} />
      <div className={`grid gap-4 mb-4 ${hasChart ? 'lg:grid-cols-2' : ''}`}>
        <DiagnosisCard runId={runId} primary={d.primary} reason={d.reason} />
        {hasChart && <ProbabilityChart data={d.probabilities} />}
      </div>
      <div className="grid lg:grid-cols-3 gap-4">
        <EvidenceList items={d.evidence} />
        {d.relatedSuccessful.length > 0 && <RelatedRuns title="Related successful runs" runs={d.relatedSuccessful} tone="bg-ok" />}
        {d.relatedFailed.length > 0 && <RelatedRuns title="Related failed runs" runs={d.relatedFailed} tone="bg-bad" />}
      </div>
    </>
  )
}
