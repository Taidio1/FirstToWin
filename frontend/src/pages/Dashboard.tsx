import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  Cpu,
  Network,
  Radio,
  ShieldAlert,
} from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { StatCard } from '@/components/charts/StatCard';
import { AlertsOverTime } from '@/components/charts/AlertsOverTime';
import { SeverityPie } from '@/components/charts/SeverityPie';
import { TopSourcesBar } from '@/components/charts/TopSourcesBar';
import { SeverityBadge } from '@/components/alerts/SeverityBadge';
import { FullPageSpinner } from '@/components/ui/Spinner';
import { fetchDashboardStats } from '@/services/dashboard';
import { listAlerts } from '@/services/alerts';
import { timeAgo } from '@/lib/utils';
import { useAutoRefresh } from '@/hooks/useAutoRefresh';

function formatNumber(n: number) {
  return new Intl.NumberFormat('en-US').format(n);
}

export default function Dashboard() {
  const navigate = useNavigate();
  const stats = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchDashboardStats,
  });
  const recent = useQuery({
    queryKey: ['alerts', { page: 1, page_size: 6 }],
    queryFn: () => listAlerts({ page: 1, page_size: 6 }),
  });

  useAutoRefresh(() => {
    void stats.refetch();
    void recent.refetch();
  }, 5000);

  if (stats.isLoading || !stats.data) return <FullPageSpinner label="Loading SOC dashboard…" />;
  const s = stats.data;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-slate-500">
            <Radio size={12} className="text-emerald-400 animate-pulse" />
            Live · last 24h
          </div>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">
            Network detection overview
          </h1>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => navigate('/alerts')}>
            All alerts
          </Button>
          <Button onClick={() => navigate('/rules')}>Manage rules</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Open critical alerts"
          value={formatNumber(s.alerts_critical_open)}
          icon={<ShieldAlert size={18} />}
          tone="danger"
          hint={`${s.alerts_open} open total`}
        />
        <StatCard
          label="Alerts (24h)"
          value={formatNumber(s.alerts_24h)}
          icon={<AlertTriangle size={18} />}
          hint="Across all sensors"
          trend={{ direction: 'up', value: '+12% vs. yesterday' }}
        />
        <StatCard
          label="Sensors online"
          value={`${s.sensors_online} / ${s.sensors_total}`}
          icon={<Cpu size={18} />}
          tone={s.sensors_online === s.sensors_total ? 'success' : 'accent'}
          hint={s.sensors_online < s.sensors_total ? 'Check sensor health' : 'All systems nominal'}
        />
        <StatCard
          label="Packets analyzed"
          value={formatNumber(s.packets_24h)}
          icon={<Network size={18} />}
          tone="accent"
          hint="ingested in the last 24h"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader
            title="Alerts over time"
            description="Hourly volume across all severities"
            actions={
              <div className="flex gap-1 rounded-lg bg-ink-800/60 p-1 text-[11px] text-slate-400">
                {['24h', '7d', '30d'].map((p, i) => (
                  <button
                    key={p}
                    className={
                      'rounded-md px-2 py-0.5 ' +
                      (i === 0 ? 'bg-ink-700 text-slate-100' : 'hover:text-slate-200')
                    }
                  >
                    {p}
                  </button>
                ))}
              </div>
            }
          />
          <CardBody>
            <AlertsOverTime data={s.alerts_timeline} />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="By severity" description="Distribution in the last 24h" />
          <CardBody>
            <SeverityPie data={s.by_severity} />
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card>
          <CardHeader title="Top noisy sources" description="By alert count" />
          <CardBody>
            <TopSourcesBar data={s.top_sources} />
          </CardBody>
        </Card>

        <Card className="xl:col-span-2">
          <CardHeader
            title="Recent alerts"
            description="Latest activity from the detection engine"
            actions={
              <Button variant="ghost" size="sm" onClick={() => navigate('/alerts')}>
                View all →
              </Button>
            }
          />
          <CardBody className="p-0">
            <ul className="divide-y divide-ink-800/70">
              {recent.data?.items.map((a) => (
                <li
                  key={a.id}
                  className="group flex cursor-pointer items-center justify-between gap-3 px-5 py-3 transition-colors hover:bg-ink-800/40"
                  onClick={() => navigate(`/alerts?focus=${a.id}`)}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <SeverityBadge severity={a.severity} />
                    <div className="min-w-0">
                      <div className="truncate text-sm text-slate-100">{a.rule_name}</div>
                      <div className="truncate text-xs text-slate-500 font-mono">
                        {a.src_ip} <span className="text-slate-600">→</span> {a.dst_ip}{' '}
                        <span className="text-slate-600">·</span> {a.protocol}
                      </div>
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2 text-xs text-slate-500">
                    <Activity size={12} />
                    {timeAgo(a.created_at)}
                  </div>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
