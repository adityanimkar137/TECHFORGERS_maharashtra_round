export default function StrategySelector({ strategies, value, onChange, params, setParams }) {
  const setP = (k, v) => setParams((p) => ({ ...p, [k]: v }))
  return (
    <div className="card p-4">
      <h2 className="text-sm font-medium mb-3">Alternative strategy</h2>
      <div className="space-y-2">
        {strategies.map((s) => (
          <label key={s.id} className={`flex gap-3 p-3 rounded-md border cursor-pointer ${value === s.id ? 'border-accent bg-raised' : 'border-line hover:bg-raised/60'}`}>
            <input type="radio" name="strategy" className="mt-1 accent-[#7c9cff]" checked={value === s.id} onChange={() => onChange(s.id)} />
            <span><span className="block text-sm font-medium">{s.name}</span><span className="block text-xs text-muted mt-0.5">{s.description}</span></span>
          </label>
        ))}
      </div>
      <h3 className="text-sm font-medium mt-5 mb-3">Parameters</h3>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div><label className="text-xs text-muted block mb-1" htmlFor="mp">Maximum price</label>
          <input id="mp" type="number" className="input w-full" value={params.maxPrice} onChange={(e) => setP('maxPrice', Number(e.target.value))} /></div>
        <div><label className="text-xs text-muted block mb-1" htmlFor="cur">Currency</label>
          <select id="cur" className="input w-full" value={params.currency} onChange={(e) => setP('currency', e.target.value)}><option>INR</option><option>USD</option><option>EUR</option></select></div>
        <div><label className="text-xs text-muted block mb-1" htmlFor="val">Validation</label>
          <select id="val" className="input w-full" value={params.validation ? 'on' : 'off'} onChange={(e) => setP('validation', e.target.value === 'on')}><option value="on">Enabled</option><option value="off">Disabled</option></select></div>
      </div>
    </div>
  )
}
