import { ReactNode, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  description?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

const sizes = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
};

export function Modal({ open, onClose, title, description, children, footer, size = 'md' }: Props) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-ink-950/70 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />
      <div
        className={cn(
          'relative w-full animate-fade-in rounded-2xl border border-ink-700 bg-ink-900 shadow-2xl shadow-black/50',
          sizes[size]
        )}
        role="dialog"
        aria-modal
      >
        <div className="flex items-start justify-between gap-4 border-b border-ink-700/70 px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-slate-100">{title}</h2>
            {description && <p className="mt-1 text-xs text-slate-400">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-slate-400 hover:bg-ink-700 hover:text-slate-100"
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>
        <div className="px-5 py-5">{children}</div>
        {footer && <div className="flex justify-end gap-2 border-t border-ink-700/70 px-5 py-3">{footer}</div>}
      </div>
    </div>,
    document.body
  );
}
