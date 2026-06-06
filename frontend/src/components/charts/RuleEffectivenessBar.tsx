import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { RuleSummary, Severity } from '@/types';

const COLORS: Record<Severity, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#3b82f6',
  info: '#94a3b8',
};

export function RuleEffectivenessBar({ data }: { data: RuleSummary[] }) {
  if (data.length === 0) {
    return (
      <div className="flex h-[180px] items-center justify-center text-sm text-slate-500">
        No rule activity yet.
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 36)}>
      <BarChart data={data} layout="vertical" margin={{ left: 16, right: 28, top: 4, bottom: 4 }}>
        <XAxis type="number" hide />
        <YAxis
          dataKey="rule_name"
          type="category"
          width={130}
          tickLine={false}
          axisLine={false}
          stroke="#94a3b8"
          fontSize={11}
        />
        <Tooltip
          cursor={{ fill: 'rgba(91,157,255,0.06)' }}
          contentStyle={{ background: '#0d1220', border: '1px solid #1c2540', borderRadius: 12, fontSize: 12 }}
        />
        <Bar dataKey="hits_count" radius={[0, 6, 6, 0]} barSize={16} isAnimationActive animationDuration={500}>
          {data.map((d) => (
            <Cell key={d.rule_name} fill={COLORS[d.severity]} />
          ))}
          <LabelList
            dataKey="hits_count"
            position="right"
            style={{ fill: '#cbd5e1', fontSize: 11, fontFamily: 'JetBrains Mono' }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
