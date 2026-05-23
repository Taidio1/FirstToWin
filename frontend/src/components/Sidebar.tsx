import { NavLink } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  Cpu,
  FlaskConical,
  LayoutDashboard,
  ScrollText,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { USE_MOCK } from '@/services/api';

const items = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/alerts', label: 'Alerts', icon: AlertTriangle },
  { to: '/rules', label: 'Detection rules', icon: ShieldCheck },
  { to: '/sensors', label: 'Sensors', icon: Cpu },
  { to: '/logs', label: 'Network logs', icon: ScrollText },
  { to: '/attack-lab', label: 'Attack Lab', icon: FlaskConical },
];

export function Sidebar() {
  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-ink-800/80 bg-ink-950/60 px-3 py-5 backdrop-blur-sm">
      <div className="mb-7 flex items-center gap-2.5 px-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent-hover shadow-glow">
          <Activity size={18} className="text-white" />
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight text-slate-100">NDR Console</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-slate-500">First To Win</div>
        </div>
      </div>

      <nav className="flex flex-col gap-1">
        {items.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-accent/10 text-accent'
                  : 'text-slate-400 hover:bg-ink-800/70 hover:text-slate-100'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={16}
                  className={cn(
                    'transition-colors',
                    isActive ? 'text-accent' : 'text-slate-500 group-hover:text-slate-200'
                  )}
                />
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto rounded-xl border border-ink-700/70 bg-ink-900/60 p-3">
        <div className="flex items-center gap-2 text-xs text-slate-300">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-pulse-ring rounded-full bg-emerald-500" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
          </span>
          Detection engine live
        </div>
        <div className="mt-1 text-[11px] text-slate-500">
          v0.1.0 - {USE_MOCK ? 'mock mode' : 'backend mode'}
        </div>
      </div>
    </aside>
  );
}
