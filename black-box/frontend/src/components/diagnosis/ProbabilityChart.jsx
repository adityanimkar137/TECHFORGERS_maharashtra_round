import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, LabelList } from 'recharts'

export default function ProbabilityChart({ data }) {
  const rows = data.map((d) => ({ ...d, value: Math.round(d.probability * 100) }))
  const max = Math.max(...rows.map((r) => r.value))
  return (
    <div className="card p-4">
      <h2 className="text-sm font-medium mb-4">Failure probability by step</h2>
      <div className="h-64">
        <ResponsiveContainer>
          <BarChart data={rows} layout="vertical" margin={{ right: 40 }}>
            <XAxis type="number" domain={[0, 100]} stroke="#8a94a6" fontSize={12} tickFormatter={(v) => `${v}%`} tickLine={false} />
            <YAxis type="category" dataKey="step" stroke="#8a94a6" fontSize={12} width={55} tickLine={false} axisLine={false} />
            <Tooltip formatter={(v) => `${v}%`} labelFormatter={(_, p) => p?.[0]?.payload.name} contentStyle={{ background: '#181d26', border: '1px solid #232a35', borderRadius: 6 }} cursor={{ fill: '#181d26' }} />
            <Bar dataKey="value" radius={[0, 3, 3, 0]}>
              {rows.map((r, i) => <Cell key={i} fill={r.value === max ? '#f0616d' : '#3a4558'} />)}
              <LabelList dataKey="value" position="right" formatter={(v) => `${v}%`} fill="#e6e9ef" fontSize={12} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
