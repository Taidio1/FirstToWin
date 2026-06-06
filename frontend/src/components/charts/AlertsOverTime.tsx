import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { format } from 'date-fns';
import { DashboardStats } from '@/types';

export function AlertsOverTime({ data }: { data: DashboardStats['alerts_timeline'] }) {
  const formatted = data.map((d) => ({
    label: format(new Date(d.hour), 'HH:mm'),
    count: d.count,
  }));

  if (data.every((d) => d.count === 0)) {
    return (
      <div className="flex h-[220px] items-center justify-center text-sm text-slate-500">
        No alert data yet — run a simulation to see activity.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={formatted} margin={{ left: -16, right: 12, top: 8, bottom: 0 }}>
        <defs>
          <linearGradient id="alertGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#5b9dff" stopOpacity={0.45} />
            <stop offset="95%" stopColor="#5b9dff" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#1c2540" strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="label"
          stroke="#475569"
          fontSize={11}
          tickLine={false}
          axisLine={false}
          interval={2}
        />
        <YAxis stroke="#475569" fontSize={11} tickLine={false} axisLine={false} width={28} />
        <Tooltip
          contentStyle={{
            background: '#0d1220',
            border: '1px solid #1c2540',
            borderRadius: 12,
            fontSize: 12,
          }}
          labelStyle={{ color: '#94a3b8' }}
          itemStyle={{ color: '#5b9dff' }}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke="#5b9dff"
          strokeWidth={2}
          fill="url(#alertGrad)"
          isAnimationActive
          animationDuration={500}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
