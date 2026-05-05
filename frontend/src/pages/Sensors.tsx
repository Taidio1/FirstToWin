import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Copy, Cpu, Plus, Trash2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Spinner } from '@/components/ui/Spinner';
import { SensorForm } from '@/components/sensors/SensorForm';
import { listSensors, createSensor, deleteSensor } from '@/services/sensors';
import { useToast } from '@/contexts/ToastContext';
import { extractError } from '@/services/api';
import { Sensor, SensorWithSecret } from '@/types';
import { timeAgo } from '@/lib/utils';

function StatusDot({ status }: { status: Sensor['status'] }) {
  const cls =
    status === 'online'
      ? 'bg-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.7)]'
      : status === 'degraded'
      ? 'bg-amber-400'
      : 'bg-slate-500';
  return <span className={`inline-block h-2 w-2 rounded-full ${cls}`} />;
}

export default function Sensors() {
  const qc = useQueryClient();
  const toast = useToast();
  const [creating, setCreating] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<Sensor | null>(null);
  const [secret, setSecret] = useState<SensorWithSecret | null>(null);

  const { data: sensors, isLoading } = useQuery({
    queryKey: ['sensors'],
    queryFn: listSensors,
    refetchInterval: 15_000,
  });

  const create = useMutation({
    mutationFn: ({ name, location }: { name: string; location: string }) =>
      createSensor(name, location),
    onSuccess: (s) => {
      qc.invalidateQueries({ queryKey: ['sensors'] });
      setCreating(false);
      setSecret(s);
    },
    onError: (e) => toast.error('Could not register sensor', extractError(e)),
  });

  const remove = useMutation({
    mutationFn: deleteSensor,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sensors'] });
      setConfirmDelete(null);
      toast.success('Sensor removed');
    },
    onError: (e) => toast.error('Could not remove sensor', extractError(e)),
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">Sensors</h1>
          <p className="text-sm text-slate-400">
            Devices that capture network traffic and ship logs to the backend.
          </p>
        </div>
        <Button onClick={() => setCreating(true)}>
          <Plus size={14} /> Register sensor
        </Button>
      </div>

      {isLoading ? (
        <Card className="flex justify-center py-12">
          <Spinner />
        </Card>
      ) : sensors && sensors.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sensors.map((s) => (
            <Card key={s.id} className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-ink-700 bg-ink-800/70 text-accent">
                    <Cpu size={18} />
                  </div>
                  <div>
                    <div className="font-medium text-slate-100">{s.name}</div>
                    <div className="text-xs text-slate-400">{s.location}</div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-severity-critical hover:bg-severity-critical/10"
                  onClick={() => setConfirmDelete(s)}
                >
                  <Trash2 size={14} />
                </Button>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="mb-1 text-[10px] uppercase tracking-wider text-slate-500">
                    Status
                  </div>
                  <div className="flex items-center gap-2 text-slate-100">
                    <StatusDot status={s.status} />
                    <span className="capitalize">{s.status}</span>
                  </div>
                </div>
                <div>
                  <div className="mb-1 text-[10px] uppercase tracking-wider text-slate-500">
                    Last seen
                  </div>
                  <div className="text-slate-300">
                    {s.last_seen ? timeAgo(s.last_seen) : 'never'}
                  </div>
                </div>
                <div>
                  <div className="mb-1 text-[10px] uppercase tracking-wider text-slate-500">
                    Packets (24h)
                  </div>
                  <div className="font-mono text-slate-300">
                    {new Intl.NumberFormat('en-US').format(s.packets_seen_24h)}
                  </div>
                </div>
                <div>
                  <div className="mb-1 text-[10px] uppercase tracking-wider text-slate-500">
                    API key
                  </div>
                  <div className="font-mono text-slate-300">{s.api_key_preview}</div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<Cpu size={28} />}
            title="No sensors registered"
            description="Register your first sensor to start receiving network logs."
            action={<Button onClick={() => setCreating(true)}>Register sensor</Button>}
          />
        </Card>
      )}

      <Modal
        open={creating}
        onClose={() => setCreating(false)}
        title="Register a new sensor"
        description="An API key will be generated — copy it immediately, it is shown only once."
      >
        <SensorForm
          onCancel={() => setCreating(false)}
          onSubmit={(v) => create.mutate(v)}
          saving={create.isPending}
        />
      </Modal>

      <Modal
        open={!!secret}
        onClose={() => setSecret(null)}
        title="Sensor registered"
        description="Configure the sensor with the API key below — you won't see it again."
        footer={
          <Button onClick={() => setSecret(null)}>Done</Button>
        }
      >
        {secret && (
          <div className="space-y-3">
            <div className="rounded-lg border border-accent/30 bg-accent/10 p-3">
              <div className="text-[11px] uppercase tracking-wider text-accent">API key</div>
              <div className="mt-1 flex items-center gap-2 font-mono text-sm text-slate-100">
                <span className="break-all">{secret.api_key}</span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    navigator.clipboard.writeText(secret.api_key);
                    toast.success('Copied to clipboard');
                  }}
                >
                  <Copy size={13} />
                </Button>
              </div>
            </div>
            <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-3 text-xs text-slate-400">
              Set <code className="text-slate-200">NDR_SENSOR_API_KEY</code> in the sensor service
              and point it at <code className="text-slate-200">/api/logs</code>.
            </div>
            <div className="text-xs text-slate-300">
              Status: <Badge tone="muted">offline</Badge> — will turn online on first heartbeat.
            </div>
          </div>
        )}
      </Modal>

      <Modal
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        title="Remove sensor?"
        description="The sensor will lose its credentials and stop being accepted by the API."
        footer={
          <>
            <Button variant="ghost" onClick={() => setConfirmDelete(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              loading={remove.isPending}
              onClick={() => confirmDelete && remove.mutate(confirmDelete.id)}
            >
              Remove sensor
            </Button>
          </>
        }
      >
        <p className="text-sm text-slate-300">
          Remove sensor{' '}
          <span className="font-medium text-slate-100">{confirmDelete?.name}</span>?
        </p>
      </Modal>
    </div>
  );
}
