import { Search, Bell, ChevronDown } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Topbar() {
  const nav = useNavigate()
  const onSearch = (e) => {
    e.preventDefault()
    const q = new FormData(e.target).get('q').trim()
    if (q) nav(`/runs?q=${encodeURIComponent(q)}`)
  }
  return (
    <header className="h-14 shrink-0 border-b border-line bg-panel flex items-center gap-3 px-4">
      <button className="btn" title="Switch project">
        <span className="w-2 h-2 rounded-full bg-ok" />shopping-assistant<ChevronDown size={14} className="text-muted" />
      </button>
      <form onSubmit={onSearch} className="flex-1 max-w-md relative">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
        <input name="q" className="input w-full pl-9" placeholder="Search runs, agents, tasks" />
      </form>
      <div className="flex-1" />
      <button className="btn relative" aria-label="Notifications"><Bell size={15} /><span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-bad" /></button>
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-raised border border-line flex items-center justify-center text-xs font-medium">DV</div>
        <div className="hidden md:block leading-tight"><div className="text-sm">Dev User</div><div className="text-[11px] text-muted">Owner</div></div>
      </div>
    </header>
  )
}
