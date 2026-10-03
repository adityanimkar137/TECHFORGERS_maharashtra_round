import { CheckCircle2 } from 'lucide-react'

export default function EvidenceList({ items }) {
  return (
    <div className="card p-4">
      <h2 className="text-sm font-medium mb-3">Evidence</h2>
      <ul className="space-y-2">
        {items.map((e) => <li key={e} className="flex gap-2 text-sm"><CheckCircle2 size={16} className="text-ok mt-0.5 shrink-0" />{e}</li>)}
      </ul>
    </div>
  )
}
