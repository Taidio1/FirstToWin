import { useState } from 'react';
import { LogOut, Search, ShieldAlert, User as UserIcon } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Input } from './ui/Input';
import { useNavigate } from 'react-router-dom';

export function Topbar() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-ink-800/80 bg-ink-950/60 px-6 backdrop-blur-md lg:px-8">
      <div className="flex max-w-md flex-1 items-center gap-3">
        <Search size={16} className="text-slate-500" />
        <Input
          placeholder="Search alerts, IPs, rules…"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              const value = (e.target as HTMLInputElement).value;
              navigate(`/alerts?q=${encodeURIComponent(value)}`);
            }
          }}
          className="border-transparent bg-ink-900/50 focus:border-ink-600"
        />
        <span className="kbd hidden md:inline-flex">/</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/alerts?status=open&severity=critical')}
          className="group flex items-center gap-2 rounded-lg border border-severity-critical/30 bg-severity-critical/10 px-3 py-1.5 text-xs font-medium text-severity-critical transition-colors hover:bg-severity-critical/20"
          title="Open critical alerts"
        >
          <ShieldAlert size={14} />
          Active threats
        </button>

        <div className="relative">
          <button
            onClick={() => setOpen((o) => !o)}
            className="flex items-center gap-2 rounded-lg border border-ink-700 bg-ink-800/60 px-2.5 py-1.5 hover:bg-ink-700/80"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-accent/15 text-accent">
              <UserIcon size={14} />
            </div>
            <div className="text-left">
              <div className="text-xs font-medium leading-tight text-slate-100">
                {user?.username ?? 'guest'}
              </div>
              <div className="text-[10px] uppercase tracking-wide text-slate-500">
                {user?.role ?? 'user'}
              </div>
            </div>
          </button>
          {open && (
            <div
              className="absolute right-0 mt-2 w-44 animate-fade-in overflow-hidden rounded-xl border border-ink-700 bg-ink-900 shadow-xl shadow-black/50"
              onMouseLeave={() => setOpen(false)}
            >
              <div className="px-3 py-2 text-[11px] uppercase tracking-wider text-slate-500">
                Signed in as
              </div>
              <div className="border-b border-ink-700/70 px-3 pb-2 text-xs text-slate-200">
                {user?.email}
              </div>
              <button
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                className="flex w-full items-center gap-2 px-3 py-2 text-xs text-slate-300 hover:bg-ink-700"
              >
                <LogOut size={13} />
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
