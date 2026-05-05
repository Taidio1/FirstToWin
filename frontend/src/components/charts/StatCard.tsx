import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface Props {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  icon?: ReactNode;
  tone?: 'default' | 'danger' | 'success' | 'accent';
  trend?: { direction: 'up' | 'down'; value: string };
}

const toneClasses = {
  default: 'text-slate-100',
  danger: 'text-severity-critical',
  success: 'text-emerald-400',
  accent: 'text-accent',
};

export function StatCard({ label, value, hint, icon, tone = 'default', trend }: Props) {
  return (
    <div className="panel-elevated relative overflow-hidden p-5">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
            {label}
          </div>
          <div className={cn('mt-2 text-3xl font-semibold tracking-tight', toneClasses[tone])}>
            {value}
          </div>
          {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
        </div>
        {icon && (
          <div
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-xl border border-ink-700/70 bg-ink-800/70',
              tone === 'danger' && 'border-severity-critical/30 text-severity-critical',
              tone === 'success' && 'border-emerald-500/30 text-emerald-400',
              tone === 'accent' && 'border-accent/30 text-accent'
            )}
          >
            {icon}
          </div>
        )}
      </div>
      {trend && (
        <div
          className={cn(
            'mt-4 inline-flex items-center gap-1 text-xs',
            trend.direction === 'up' ? 'text-emerald-400' : 'text-severity-critical'
          )}
        >
          {trend.direction === 'up' ? '▲' : '▼'} {trend.value}
        </div>
      )}
    </div>
  );
}
