import { NavLink } from 'react-router-dom'
import { links } from '../../services/api.js'
import { LayoutDashboard, ListChecks, AlertOctagon, RotateCcw, GitCompare, Settings, PanelLeftClose, PanelLeftOpen, Box } from 'lucide-react'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/runs', label: 'Executions', icon: ListChecks, end: true },
  { to: '/runs?status=FAILED', label: 'Failures', icon: AlertOctagon, match: false },
  { to: links.replay, label: 'Replay', icon: RotateCcw },
  { to: links.compare, label: 'Comparisons', icon: GitCompare },
]

const link = ({ isActive }) =>
  `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${isActive ? 'bg-raised text-ink' : 'text-muted hover:text-ink hover:bg-raised/60'}`

export default function Sidebar({ collapsed, onToggle }) {
  return (
    <aside className={`${collapsed ? 'w-16' : 'w-60'} shrink-0 bg-panel border-r border-line flex flex-col transition-[width] duration-150`}>
      <div className="h-14 flex items-center gap-3 px-4 border-b border-line">
        <div className="w-7 h-7 rounded bg-accent text-base flex items-center justify-center shrink-0"><Box size={16} /></div>
        {!collapsed && <div className="leading-tight"><div className="text-sm font-semibold tracking-wide">BLACK BOX</div><div className="text-[11px] text-muted">AI Agent Debugger</div></div>}
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {nav.map(({ to, label, icon: Icon, end, match }) => (
          <NavLink key={label} to={to} end={end} title={label}
            className={(s) => link(match === false ? { isActive: false } : s)}>
            <Icon size={17} className="shrink-0" />{!collapsed && label}
          </NavLink>
        ))}
      </nav>
      <div className="p-2 border-t border-line space-y-1">
        <NavLink to="/settings" className={link} title="Settings"><Settings size={17} />{!collapsed && 'Settings'}</NavLink>
        <button onClick={onToggle} className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm text-muted hover:text-ink hover:bg-raised/60" aria-label="Toggle sidebar">
          {collapsed ? <PanelLeftOpen size={17} /> : <><PanelLeftClose size={17} />Collapse</>}
        </button>
      </div>
    </aside>
  )
}
