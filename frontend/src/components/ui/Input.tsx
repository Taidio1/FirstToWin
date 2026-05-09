import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
}

export const Input = forwardRef<HTMLInputElement, Props>(
  ({ className, invalid, ...rest }, ref) => (
    <input
      ref={ref}
      className={cn(
        'w-full rounded-lg border bg-ink-900/70 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500',
        'transition-colors focus:outline-none focus:ring-2',
        invalid
          ? 'border-severity-critical/60 focus:border-severity-critical focus:ring-severity-critical/30'
          : 'border-ink-600 focus:border-accent/60 focus:ring-accent/30',
        className
      )}
      {...rest}
    />
  )
);
Input.displayName = 'Input';
