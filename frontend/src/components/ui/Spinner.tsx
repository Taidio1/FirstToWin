import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Spinner({ size = 18, className }: { size?: number; className?: string }) {
  return <Loader2 size={size} className={cn('animate-spin text-accent', className)} />;
}

export function FullPageSpinner({ label }: { label?: string }) {
  return (
    <div className="flex h-full min-h-[60vh] flex-col items-center justify-center gap-3 text-slate-400">
      <Spinner size={28} />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}
