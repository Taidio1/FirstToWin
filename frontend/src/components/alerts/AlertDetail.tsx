import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Globe, Server, ShieldAlert } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { Badge } from '@/components/ui/Badge';
import { SeverityBadge } from './SeverityBadge';
import { StatusBadge } from './StatusBadge';
import { getOsintForAlert } from '@/services/alerts';
import { AlertItem, AlertStatus } from '@/types';
import { formatDateTime, timeAgo } from '@/lib/utils';

interface Props {
  alert: AlertItem | null;
  onClose: () => void;
  onChangeStatus: (id: number, status: AlertStatus) => void;
  saving?: boolean;
}

export function AlertDetail({ alert, onClose, onChangeStatus, saving }: Props) {
  const open = !!alert;
  const { data: osint, isLoading: osintLoading } = useQuery({
    queryKey: ['osint', alert?.id],
    queryFn: () => getOsintForAlert(alert!.id),
    enabled: open,
  });

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={
        <span className="flex items-center gap-2">
          <ShieldAlert size={16} className="text-severity-critical" />
          Alert #{alert?.id}
        </span>
      }
      description={alert ? `Triggered ${timeAgo(alert.created_at)}` : undefined}
      size="lg"
      footer={
        alert && (
          <>
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
            {alert.status === 'open' && (
              <Button
                variant="secondary"
                loading={saving}
                onClick={() => onChangeStatus(alert.id, 'acknowledged')}
              >
                Acknowledge
              </Button>
            )}
            {alert.status !== 'resolved' && (
              <Button loading={saving} onClick={() => onChangeStatus(alert.id, 'resolved')}>
                Resolve
              </Button>
            )}
          </>
        )
      }
    >
      {!alert ? null : (
        <div className="space-y-5">
          <div className="flex flex-wrap items-center gap-2">
            <SeverityBadge severity={alert.severity} />
            <StatusBadge status={alert.status} />
            <Badge tone="muted">{alert.protocol}</Badge>
            <Badge tone="muted">Rule #{alert.rule_id}</Badge>
          </div>

          <section>
            <h4 className="mb-1 text-sm font-medium text-slate-100">{alert.rule_name}</h4>
            <p className="text-sm text-slate-300">{alert.details}</p>
          </section>

          <section className="grid grid-cols-2 gap-3 rounded-xl border border-ink-700/70 bg-ink-900/60 p-3 font-mono text-xs">
            <Field label="Source IP" value={alert.src_ip} mono accent />
            <Field label="Destination IP" value={alert.dst_ip} mono />
            <Field label="Sensor" value={alert.sensor_id} mono />
            <Field label="Triggered at" value={formatDateTime(alert.created_at)} mono />
          </section>

          <section>
            <div className="mb-2 flex items-center gap-2">
              <Globe size={14} className="text-accent" />
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                OSINT enrichment
              </h4>
            </div>
            <div className="rounded-xl border border-ink-700/70 bg-ink-900/60 p-4 text-sm">
              {osintLoading ? (
                <div className="flex items-center gap-2 text-slate-400">
                  <Spinner size={14} /> Querying AbuseIPDB…
                </div>
              ) : osint ? (
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="col-span-2 flex items-center gap-3">
                    <div
                      className={`h-2 w-full overflow-hidden rounded-full bg-ink-700`}
                      title={`Abuse confidence: ${osint.abuse_confidence}%`}
                    >
                      <div
                        className={
                          osint.abuse_confidence >= 75
                            ? 'h-full bg-severity-critical'
                            : osint.abuse_confidence >= 40
                            ? 'h-full bg-severity-high'
                            : 'h-full bg-emerald-500'
                        }
                        style={{ width: `${osint.abuse_confidence}%` }}
                      />
                    </div>
                    <span className="shrink-0 text-slate-200">
                      {osint.abuse_confidence}% confidence
                    </span>
                  </div>
                  <Field label="Country" value={osint.country ?? '—'} />
                  <Field label="ISP" value={osint.isp ?? '—'} />
                  <Field label="Reports" value={String(osint.reports_count)} />
                  <Field
                    label="Last reported"
                    value={osint.last_reported_at ? formatDateTime(osint.last_reported_at) : '—'}
                  />
                </div>
              ) : (
                <span className="text-slate-400">No external context for this IP yet.</span>
              )}
            </div>
          </section>

          <section className="flex items-center justify-between rounded-xl border border-ink-700/70 bg-ink-900/60 p-3 text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <Server size={14} className="text-slate-400" />
              <span>Suggest blocking</span>
              <code className="rounded bg-ink-800 px-1.5 py-0.5 font-mono text-accent">
                {alert.src_ip}
              </code>
            </div>
            <Button variant="subtle" size="sm">
              Add to blacklist <ArrowRight size={13} />
            </Button>
          </section>
        </div>
      )}
    </Modal>
  );
}

function Field({
  label,
  value,
  mono,
  accent,
}: {
  label: string;
  value: string;
  mono?: boolean;
  accent?: boolean;
}) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wider text-slate-500">{label}</div>
      <div
        className={
          (mono ? 'font-mono ' : '') +
          (accent ? 'text-accent' : 'text-slate-100') +
          ' mt-0.5 text-sm'
        }
      >
        {value}
      </div>
    </div>
  );
}
