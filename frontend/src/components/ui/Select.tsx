import { SelectHTMLAttributes, forwardRef } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props extends SelectHTMLAttributes<HTMLSelectElement> {}

export const Select = forwardRef<HTMLSelectElement, Props>(
  ({ className, children, ...rest }, ref) => (
    <div className="relative">
      <select
        ref={ref}
        className={cn(
          'w-full appearance-none rounded-lg border border-ink-600 bg-ink-900/70 py-2 pl-3 pr-9 text-sm text-slate-100',
          'transition-colors focus:border-accent/60 focus:outline-none focus:ring-2 focus:ring-accent/30',
          className
        )}
        {...rest}
      >
        {children}
      </select>
      <ChevronDown
        size={14}
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"
      />
    </div>
  )
);
Select.displayName = 'Select';
