import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'

const colors = ['#f0616d', '#e3a008', '#7c9cff', '#a78bfa', '#8a94a6']

export default function FailureDistribution({ data }) {
  return (
    <div className="card p-4">
      <h2 className="text-sm font-medium mb-4">Failure distribution</h2>
      <div className="h-64">
        <ResponsiveContainer>
          <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
            <XAxis type="number" stroke="#8a94a6" fontSize={12} tickLine={false} />
            <YAxis type="category" dataKey="name" stroke="#8a94a6" fontSize={12} width={110} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: '#181d26', border: '1px solid #232a35', borderRadius: 6 }} cursor={{ fill: '#181d26' }} />
            <Bar dataKey="value" name="Failures" radius={[0, 3, 3, 0]}>{data.map((_, i) => <Cell key={i} fill={colors[i % colors.length]} />)}</Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
