import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from 'react';
import { CheckCircle2, Info, TriangleAlert, X } from 'lucide-react';
import { cn } from '@/lib/utils';

type ToastKind = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  kind: ToastKind;
  title: string;
  description?: string;
}

interface ToastContextValue {
  show: (kind: ToastKind, title: string, description?: string) => void;
  success: (title: string, description?: string) => void;
  error: (title: string, description?: string) => void;
  info: (title: string, description?: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const seq = useRef(1);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback(
    (kind: ToastKind, title: string, description?: string) => {
      const id = seq.current++;
      setToasts((prev) => [...prev, { id, kind, title, description }]);
      setTimeout(() => dismiss(id), 4500);
    },
    [dismiss]
  );

  const value = useMemo<ToastContextValue>(
    () => ({
      show,
      success: (t, d) => show('success', t, d),
      error: (t, d) => show('error', t, d),
      info: (t, d) => show('info', t, d),
    }),
    [show]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-[22rem] flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              'pointer-events-auto flex animate-fade-in items-start gap-3 rounded-xl border bg-ink-800/95 p-3 shadow-lg shadow-black/40 backdrop-blur',
              t.kind === 'success' && 'border-emerald-500/40',
              t.kind === 'error' && 'border-severity-critical/50',
              t.kind === 'info' && 'border-ink-600'
            )}
          >
            <div
              className={cn(
                'mt-0.5',
                t.kind === 'success' && 'text-emerald-400',
                t.kind === 'error' && 'text-severity-critical',
                t.kind === 'info' && 'text-accent'
              )}
            >
              {t.kind === 'success' ? (
                <CheckCircle2 size={18} />
              ) : t.kind === 'error' ? (
                <TriangleAlert size={18} />
              ) : (
                <Info size={18} />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium text-slate-100">{t.title}</div>
              {t.description && (
                <div className="mt-0.5 text-xs text-slate-400">{t.description}</div>
              )}
            </div>
            <button
              onClick={() => dismiss(t.id)}
              className="rounded-md p-1 text-slate-500 hover:bg-ink-700 hover:text-slate-200"
              aria-label="Dismiss"
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
