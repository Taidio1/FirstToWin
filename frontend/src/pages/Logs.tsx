import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { Card, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Spinner } from '@/components/ui/Spinner';
import { listLogs } from '@/services/logs';
import { formatDateTime } from '@/lib/utils';
import { useAutoRefresh } from '@/hooks/useAutoRefresh';

const PAGE_SIZE = 50;

export default function Logs() {
  const [q, setQ] = useState('');
  const [committed, setCommitted] = useState('');
  const [page, setPage] = useState(1);
  const { data, isFetching, refetch } = useQuery({
    queryKey: ['logs', { page, page_size: PAGE_SIZE, q: committed }],
    queryFn: () => listLogs({ page, page_size: PAGE_SIZE, q: committed || undefined }),
  });

  useAutoRefresh(() => {
    void refetch();
  }, 5000);

  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / PAGE_SIZE));

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">Network logs</h1>
          <p className="text-sm text-slate-400">
            Raw, normalized packet metadata as it arrives from your sensors.
          </p>
        </div>
        <div className="flex gap-2">
          <Input
            placeholder="Filter by IP or sensor…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                setCommitted(q);
                setPage(1);
              }
            }}
            className="w-72"
          />
          <Button variant="secondary" onClick={() => refetch()}>
            <RefreshCw size={14} /> Refresh
          </Button>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-ink-700/70 text-left text-[11px] uppercase tracking-wider text-slate-500">
                <th className="px-5 py-3">Timestamp</th>
                <th className="px-5 py-3">Sensor</th>
                <th className="px-5 py-3">Source</th>
                <th className="px-5 py-3">Destination</th>
                <th className="px-5 py-3">Proto</th>
                <th className="px-5 py-3">Flags</th>
                <th className="px-5 py-3">Bytes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-800/70 font-mono text-xs">
              {isFetching && !data && (
                <tr>
                  <td colSpan={7}>
                    <CardBody className="flex justify-center">
                      <Spinner />
                    </CardBody>
                  </td>
                </tr>
              )}
              {data?.items.length === 0 && (
                <tr>
                  <td colSpan={7}>
                    <EmptyState
                      title="No logs match your filter"
                      description="Try a different IP / sensor or clear the filter."
                    />
                  </td>
                </tr>
              )}
              {data?.items.map((l) => (
                <tr key={l.id} className="hover:bg-ink-800/40">
                  <td className="whitespace-nowrap px-5 py-2.5 text-slate-400">
                    {formatDateTime(l.timestamp)}
                  </td>
                  <td className="whitespace-nowrap px-5 py-2.5 text-slate-300">{l.sensor_id}</td>
                  <td className="whitespace-nowrap px-5 py-2.5">
                    <span className="text-accent">{l.src_ip}</span>
                    <span className="text-slate-500">:{l.src_port}</span>
                  </td>
                  <td className="whitespace-nowrap px-5 py-2.5">
                    <span className="text-slate-200">{l.dst_ip}</span>
                    <span className="text-slate-500">:{l.dst_port}</span>
                  </td>
                  <td className="whitespace-nowrap px-5 py-2.5">
                    <Badge tone="muted">{l.protocol}</Badge>
                  </td>
                  <td className="whitespace-nowrap px-5 py-2.5 text-slate-300">{l.flags || '—'}</td>
                  <td className="whitespace-nowrap px-5 py-2.5 text-slate-300">{l.payload_size}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between border-t border-ink-700/70 px-5 py-3 text-xs text-slate-400">
          <span>
            Page <span className="text-slate-200">{page}</span> of{' '}
            <span className="text-slate-200">{totalPages}</span> ·{' '}
            <span className="text-slate-200">{data?.total ?? 0}</span> records
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
    </div>
  );
}
