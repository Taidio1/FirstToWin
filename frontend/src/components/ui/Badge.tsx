import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

type Tone = 'default' | 'accent' | 'success' | 'warning' | 'danger' | 'muted';

const tones: Record<Tone, string> = {
  default: 'bg-ink-700/70 text-slate-200 border-ink-600',
  accent: 'bg-accent/15 text-accent border-accent/30',
  success: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  warning: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  danger: 'bg-severity-critical/10 text-severity-critical border-severity-critical/30',
  muted: 'bg-ink-800/70 text-slate-400 border-ink-700',
};

export function Badge({
  children,
  tone = 'default',
  className,
}: {
  children: ReactNode;
  tone?: Tone;
  className?: string;
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium tracking-wide',
        tones[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
