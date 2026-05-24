import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Severity } from '@/types';

const COLORS: Record<Severity, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#3b82f6',
  info: '#94a3b8',
};

export function TopSourcesBar({
  data,
}: {
  data: { ip: string; count: number; severity: Severity }[];
}) {
  if (data.length === 0) {
    return (
      <div className="flex h-[180px] items-center justify-center text-sm text-slate-500">
        No top sources yet.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 32)}>
      <BarChart data={data} layout="vertical" margin={{ left: 16, right: 24, top: 4, bottom: 4 }}>
        <XAxis type="number" hide />
        <YAxis
          dataKey="ip"
          type="category"
          width={110}
          tickLine={false}
          axisLine={false}
          stroke="#94a3b8"
          fontSize={11}
        />
        <Tooltip
          cursor={{ fill: 'rgba(91,157,255,0.06)' }}
          contentStyle={{
            background: '#0d1220',
            border: '1px solid #1c2540',
            borderRadius: 12,
            fontSize: 12,
          }}
        />
        <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={14}>
          {data.map((d) => (
            <Cell key={d.ip} fill={COLORS[d.severity]} />
          ))}
          <LabelList
            dataKey="count"
            position="right"
            style={{ fill: '#cbd5e1', fontSize: 11, fontFamily: 'JetBrains Mono' }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
