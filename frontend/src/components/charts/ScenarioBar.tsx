import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { ScenarioSummary } from '@/types';

export function ScenarioBar({ data }: { data: ScenarioSummary[] }) {
  if (data.length === 0) {
    return (
      <div className="flex h-[220px] items-center justify-center text-sm text-slate-500">
        No scenario data yet.
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ left: 8, right: 16, top: 8, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1c2540" vertical={false} />
        <XAxis dataKey="scenario" tickLine={false} axisLine={false} stroke="#94a3b8" fontSize={11} />
        <YAxis tickLine={false} axisLine={false} stroke="#94a3b8" fontSize={11} />
        <Tooltip
          cursor={{ fill: 'rgba(91,157,255,0.06)' }}
          contentStyle={{ background: '#0d1220', border: '1px solid #1c2540', borderRadius: 12, fontSize: 12 }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="logs_count" name="Logi" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={22} />
        <Bar dataKey="alerts_count" name="Alerty" fill="#ef4444" radius={[6, 6, 0, 0]} barSize={22} />
      </BarChart>
    </ResponsiveContainer>
  );
}
