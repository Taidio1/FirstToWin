import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { Severity } from '@/types';

const COLORS: Record<Severity, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#3b82f6',
  info: '#94a3b8',
};

export function SeverityPie({ data }: { data: { severity: Severity; count: number }[] }) {
  const filtered = data.filter((d) => d.count > 0);
  const total = filtered.reduce((s, d) => s + d.count, 0) || 1;

  if (filtered.length === 0) {
    return (
      <div className="flex h-[150px] items-center justify-center text-sm text-slate-500">
        No alerts to display.
      </div>
    );
  }

  return (
    <div className="flex items-center gap-5">
      <ResponsiveContainer width={150} height={150}>
        <PieChart>
          <Pie
            data={filtered}
            dataKey="count"
            nameKey="severity"
            innerRadius={45}
            outerRadius={68}
            paddingAngle={2}
            stroke="none"
            isAnimationActive
            animationDuration={500}
          >
            {filtered.map((entry) => (
              <Cell key={entry.severity} fill={COLORS[entry.severity]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: '#0d1220',
              border: '1px solid #1c2540',
              borderRadius: 12,
              fontSize: 12,
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <ul className="space-y-1.5 text-xs">
        {filtered.map((d) => {
          const pct = Math.round((d.count / total) * 100);
          return (
            <li key={d.severity} className="flex items-center gap-2">
              <span
                className="h-2 w-2 rounded-full"
                style={{ background: COLORS[d.severity] }}
                aria-hidden
              />
              <span className="w-16 capitalize text-slate-300">{d.severity}</span>
              <span className="font-mono text-slate-100">{d.count}</span>
              <span className="text-slate-500">· {pct}%</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
