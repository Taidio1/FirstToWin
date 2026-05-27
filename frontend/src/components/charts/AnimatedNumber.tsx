import { useEffect, useMemo, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface Props {
  value: number;
  durationMs?: number;
  className?: string;
}

export function AnimatedNumber({ value, durationMs = 700, className }: Props) {
  const formatter = useMemo(() => new Intl.NumberFormat('en-US'), []);
  const [displayValue, setDisplayValue] = useState(value);
  const displayRef = useRef(value);

  useEffect(() => {
    const from = displayRef.current;
    const to = value;

    if (from === to || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      displayRef.current = to;
      setDisplayValue(to);
      return;
    }

    let frame = 0;
    const startedAt = performance.now();

    const tick = (now: number) => {
      const progress = Math.min((now - startedAt) / durationMs, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const next = Math.round(from + (to - from) * eased);

      displayRef.current = next;
      setDisplayValue(next);

      if (progress < 1) {
        frame = window.requestAnimationFrame(tick);
      }
    };

    frame = window.requestAnimationFrame(tick);

    return () => window.cancelAnimationFrame(frame);
  }, [durationMs, value]);

  return <span className={cn('tabular-nums', className)}>{formatter.format(displayValue)}</span>;
}
