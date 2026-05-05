import { cn } from '@/lib/utils';
import { Severity } from '@/types';

const styles: Record<Severity, string> = {
  critical:
    'bg-severity-critical/10 text-severity-critical border-severity-critical/40 shadow-glow-danger',
  high: 'bg-severity-high/10 text-severity-high border-severity-high/40',
  medium: 'bg-severity-medium/10 text-severity-medium border-severity-medium/40',
  low: 'bg-severity-low/10 text-severity-low border-severity-low/40',
  info: 'bg-severity-info/10 text-severity-info border-severity-info/40',
};

export function SeverityBadge({ severity, className }: { severity: Severity; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider',
        styles[severity],
        className
      )}
    >
      <span
        className={cn(
          'h-1.5 w-1.5 rounded-full',
          severity === 'critical' && 'bg-severity-critical animate-pulse',
          severity === 'high' && 'bg-severity-high',
          severity === 'medium' && 'bg-severity-medium',
          severity === 'low' && 'bg-severity-low',
          severity === 'info' && 'bg-severity-info'
        )}
      />
      {severity}
    </span>
  );
}
