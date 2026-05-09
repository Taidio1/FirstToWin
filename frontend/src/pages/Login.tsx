import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { extractError, USE_MOCK } from '@/services/api';

export default function Login() {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const [email, setEmail] = useState(USE_MOCK ? 'analyst@firsttowin.io' : '');
  const [password, setPassword] = useState(USE_MOCK ? 'demo' : '');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await login(email, password);
      const from = (location.state as { from?: string } | null)?.from ?? '/';
      navigate(from, { replace: true });
    } catch (err) {
      toast.error('Login failed', extractError(err));
    }
  }

  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[1fr_minmax(0,560px)]">
      <div className="relative hidden overflow-hidden border-r border-ink-800/80 lg:block">
        <div className="absolute inset-0 bg-gradient-to-br from-ink-900 via-ink-950 to-black" />
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              'radial-gradient(circle at 20% 20%, rgba(91,157,255,0.35), transparent 35%), radial-gradient(circle at 80% 70%, rgba(239,68,68,0.25), transparent 40%)',
          }}
        />
        <div className="relative z-10 flex h-full flex-col justify-between p-12">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent shadow-glow">
              <Activity size={20} className="text-white" />
            </div>
            <div>
              <div className="text-base font-semibold text-slate-100">NDR Console</div>
              <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                First To Win
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <h1 className="max-w-md text-3xl font-semibold leading-tight text-slate-50">
                Watch your network. Catch what shouldn't be there.
              </h1>
              <p className="mt-3 max-w-md text-sm text-slate-400">
                Real-time detection, OSINT-enriched alerts and one-click response — built for SOC
                analysts and network admins who want signal, not noise.
              </p>
            </div>

            <ul className="space-y-2 text-sm text-slate-300">
              {[
                'Sensor → API in <50ms with API-key auth',
                'Detection engine with port-scan + threshold rules',
                'AbuseIPDB enrichment on every external IP',
                'Real-time updates over SSE — no polling',
              ].map((b) => (
                <li key={b} className="flex items-center gap-2">
                  <ShieldCheck size={14} className="text-accent" /> {b}
                </li>
              ))}
            </ul>
          </div>

          <div className="text-xs text-slate-500">
            v0.1.0 · MVP · Sprint 1 · NDR — Network Detection &amp; Response
          </div>
        </div>
      </div>

      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-slate-100">Sign in</h2>
            <p className="mt-1 text-sm text-slate-400">
              Welcome back. Use your analyst account to access the console.
            </p>
          </div>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="field-label">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@firsttowin.io"
                autoComplete="email"
                required
              />
            </div>
            <div>
              <label className="field-label">Password</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>

            <Button type="submit" size="lg" className="w-full" loading={isLoading}>
              Sign in
            </Button>
          </form>

          {USE_MOCK && (
            <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-3 text-xs text-slate-400">
              <span className="text-slate-300">Mock mode:</span> any email + password will work.
            </div>
          )}

          <div className="text-center text-xs text-slate-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-accent hover:underline">
              Request access
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
