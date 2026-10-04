import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts'

export default function ExecutionChart({ data }) {
  return (
    <div className="card p-4">
      <h2 className="text-sm font-medium mb-4">Executions this week</h2>
      <div className="h-64">
        <ResponsiveContainer>
          <BarChart data={data}>
            <CartesianGrid stroke="#232a35" vertical={false} />
            <XAxis dataKey="day" stroke="#8a94a6" fontSize={12} tickLine={false} />
            <YAxis stroke="#8a94a6" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: '#181d26', border: '1px solid #232a35', borderRadius: 6 }} cursor={{ fill: '#181d26' }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="success" name="Successful" stackId="a" fill="#3fb97f" />
            <Bar dataKey="failed" name="Failed" stackId="a" fill="#f0616d" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
