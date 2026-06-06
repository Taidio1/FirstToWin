import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Filter, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Card, CardBody } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { SeverityBadge } from '@/components/alerts/SeverityBadge';
import { StatusBadge } from '@/components/alerts/StatusBadge';
import { AlertDetail } from '@/components/alerts/AlertDetail';
import { listAlerts, patchAlertStatus } from '@/services/alerts';
import { createRule } from '@/services/rules';
import { extractError } from '@/services/api';
import { useToast } from '@/contexts/ToastContext';
import { AlertItem, AlertStatus, Severity } from '@/types';
import { timeAgo } from '@/lib/utils';
import { useAutoRefresh } from '@/hooks/useAutoRefresh';
import { useLiveAlertPulse } from '@/hooks/useRealtimeAlerts';

const PAGE_SIZE = 20;

export default function Alerts() {
  const [params, setParams] = useSearchParams();
  const [page, setPage] = useState(1);
  const [q, setQ] = useState(params.get('q') ?? '');
  const [severity, setSeverity] = useState<Severity | ''>(
    (params.get('severity') as Severity) || ''
  );
  const [status, setStatus] = useState<AlertStatus | ''>(
    (params.get('status') as AlertStatus) || ''
  );
  const [active, setActive] = useState<AlertItem | null>(null);
  const freshAlertId = useLiveAlertPulse();

  const focusId = params.get('focus');
  const qc = useQueryClient();
  const toast = useToast();

  const filters = useMemo(
    () => ({
      page,
      page_size: PAGE_SIZE,
      severity: severity || undefined,
      status: status || undefined,
      q: q || undefined,
    }),
    [page, severity, status, q]
  );

  const { data, isFetching, refetch } = useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => listAlerts(filters),
  });

  useAutoRefresh(() => {
    void refetch();
  }, 5000);

  useEffect(() => {
    if (focusId && data) {
      const found = data.items.find((a) => a.id === Number(focusId));
      if (found) setActive(found);
    }
  }, [focusId, data]);

  const blacklistMutation = useMutation({
    mutationFn: (srcIp: string) =>
      createRule({
        name: `Block ${srcIp}`,
        type: 'blacklist_ip',
        enabled: true,
        severity: 'critical',
        match: { src_ip: srcIp, protocol: 'TCP' },
        description: `Auto-generated blacklist rule for ${srcIp}.`,
      }),
    onSuccess: (rule) => {
      qc.invalidateQueries({ queryKey: ['rules'] });
      toast.success('Rule created', `${rule.name} added to blacklist.`);
    },
    onError: (err) => toast.error('Could not create rule', extractError(err)),
  });

  const patchMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: AlertStatus }) =>
      patchAlertStatus(id, status),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ['alerts'] });
      qc.invalidateQueries({ queryKey: ['dashboard-stats'] });
      setActive((prev) => (prev?.id === updated.id ? updated : prev));
      toast.success('Alert updated', `Status set to ${updated.status}.`);
    },
    onError: (err) => toast.error('Could not update alert', extractError(err)),
  });

  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / PAGE_SIZE));

  function applyFilters() {
    const next = new URLSearchParams(params);
    q ? next.set('q', q) : next.delete('q');
    severity ? next.set('severity', severity) : next.delete('severity');
    status ? next.set('status', status) : next.delete('status');
    next.delete('focus');
    setParams(next, { replace: true });
    setPage(1);
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">Alerts</h1>
          <p className="text-sm text-slate-400">
            Triage detection events. Acknowledge or resolve as you investigate.
          </p>
        </div>
        <Button variant="secondary" onClick={() => refetch()}>
          <RefreshCw size={14} /> Refresh
        </Button>
      </div>

      <Card>
        <CardBody className="space-y-3">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_180px_180px_auto]">
            <Input
              placeholder="Search by IP, rule or detail…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
            />
            <Select
              value={severity}
              onChange={(e) => setSeverity(e.target.value as Severity | '')}
            >
              <option value="">All severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="info">Info</option>
            </Select>
            <Select value={status} onChange={(e) => setStatus(e.target.value as AlertStatus | '')}>
              <option value="">All statuses</option>
              <option value="open">Open</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </Select>
            <Button onClick={applyFilters}>
              <Filter size={14} /> Apply
            </Button>
          </div>
        </CardBody>
      </Card>

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-ink-700/70 text-left text-[11px] uppercase tracking-wider text-slate-500">
                <th className="px-5 py-3">Severity</th>
                <th className="px-5 py-3">Rule</th>
                <th className="px-5 py-3">Source → Destination</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Triggered</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-800/70">
              {isFetching && !data && (
                <tr>
                  <td colSpan={5} className="px-5 py-12 text-center">
                    <Spinner />
                  </td>
                </tr>
              )}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={5}>
                    <EmptyState
                      title="No alerts match your filters"
                      description="Try clearing the search or selecting a broader severity."
                    />
                  </td>
                </tr>
              )}
              {data?.items.map((a) => (
                <tr
                  key={a.id}
                  className={
                    'cursor-pointer transition-colors hover:bg-ink-800/40 ' +
                    (freshAlertId === a.id ? 'live-row-pulse' : '')
                  }
                  onClick={() => setActive(a)}
                >
                  <td className="whitespace-nowrap px-5 py-3.5">
                    <SeverityBadge severity={a.severity} />
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="text-slate-100">{a.rule_name}</div>
                    <div className="mt-0.5 text-xs text-slate-500">{a.details}</div>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-xs">
                    <span className="text-accent">{a.src_ip}</span>
                    <span className="mx-1 text-slate-500">→</span>
                    <span className="text-slate-200">{a.dst_ip}</span>
                    <span className="ml-2 text-slate-500">{a.protocol}</span>
                  </td>
                  <td
                    className="whitespace-nowrap px-5 py-3.5"
                    title="Click to advance status"
                    onClick={(e) => {
                      e.stopPropagation();
                      const next: Record<string, AlertStatus> = {
                        open: 'acknowledged',
                        acknowledged: 'resolved',
                        resolved: 'open',
                      };
                      patchMutation.mutate({ id: a.id, status: next[a.status] as AlertStatus });
                    }}
                  >
                    <span className="cursor-pointer rounded hover:opacity-75 transition-opacity">
                      <StatusBadge status={a.status} />
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-5 py-3.5 text-xs text-slate-400">
                    {timeAgo(a.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between border-t border-ink-700/70 px-5 py-3 text-xs text-slate-400">
          <span>
            Page <span className="text-slate-200">{page}</span> of{' '}
            <span className="text-slate-200">{totalPages}</span> ·{' '}
            <span className="text-slate-200">{data?.total ?? 0}</span> alerts
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft size={14} /> Prev
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next <ChevronRight size={14} />
            </Button>
          </div>
        </div>
      </Card>

      <AlertDetail
        alert={active}
        onClose={() => setActive(null)}
        onChangeStatus={(id, status) => patchMutation.mutate({ id, status })}
        onAddToBlacklist={(srcIp) => blacklistMutation.mutate(srcIp)}
        saving={patchMutation.isPending}
        blacklisting={blacklistMutation.isPending}
      />
    </div>
  );
}
