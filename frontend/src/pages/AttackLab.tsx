import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Activity,
  Play,
  SquareTerminal,
  StopCircle,
  Timer,
  Zap,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { FullPageSpinner, Spinner } from '@/components/ui/Spinner';
import {
  getAttackLabStatus,
  runScenario,
  startAutoAttack,
  stopAutoAttack,
  SCENARIOS,
  RunResult,
} from '@/services/attackLab';
import { extractError } from '@/services/api';
import { useToast } from '@/contexts/ToastContext';
import { cn } from '@/lib/utils';

function formatCountdown(seconds: number | null): string {
  if (seconds === null) return '--:--';
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

export default function AttackLab() {
  const [intervalSecs, setIntervalSecs] = useState(30);
  const [localCountdown, setLocalCountdown] = useState<number | null>(null);
  const [runningScenario, setRunningScenario] = useState<string | null>(null);
  const [lastRun, setLastRun] = useState<RunResult | null>(null);

  const toast = useToast();
  const qc = useQueryClient();

  const { data: status, isLoading } = useQuery({
    queryKey: ['attack-lab-status'],
    queryFn: getAttackLabStatus,
    refetchInterval: 3000,
  });

  // Sync countdown from server
  useEffect(() => {
    setLocalCountdown(status?.seconds_remaining ?? null);
  }, [status?.seconds_remaining]);

  // Tick countdown down 1s at a time
  useEffect(() => {
    if (localCountdown == null || localCountdown <= 0) return;
    const id = window.setTimeout(
      () => setLocalCountdown((c) => (c != null && c > 0 ? c - 1 : null)),
      1000
    );
    return () => clearTimeout(id);
  }, [localCountdown]);

  const startMut = useMutation({
    mutationFn: () => startAutoAttack(intervalSecs),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['attack-lab-status'] });
      toast.success('Auto-attack started');
    },
    onError: (e) => toast.error(extractError(e)),
  });

  const stopMut = useMutation({
    mutationFn: stopAutoAttack,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['attack-lab-status'] });
      toast.info('Auto-attack stopped');
    },
    onError: (e) => toast.error(extractError(e)),
  });

  const runMut = useMutation({
    mutationFn: (scenario: string) => {
      setRunningScenario(scenario);
      return runScenario(scenario);
    },
    onSuccess: (data) => {
      setLastRun(data);
      setRunningScenario(null);
      void qc.invalidateQueries({ queryKey: ['attack-lab-status'] });
      toast.success(
        `"${data.scenario}" complete`,
        `${data.payloads_sent} payloads · ${data.alerts_created} alert(s) created`
      );
    },
    onError: (e) => {
      setRunningScenario(null);
      toast.error(extractError(e));
    },
  });

  if (isLoading) return <FullPageSpinner label="Loading Attack Lab…" />;

  const result = lastRun ?? status?.last_result ?? null;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-slate-500">
          <SquareTerminal size={12} className="text-orange-400" />
          Attack Lab · Simulation only — no real network traffic
        </div>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">
          Attack Simulator
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Inject demo payloads through the detection pipeline to generate alerts.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Auto-attack control */}
        <Card>
          <CardHeader
            title="Auto-attack"
            description="Randomly fires port-scan, ssh-bruteforce or blacklist at a fixed interval"
          />
          <CardBody className="space-y-4">
            {/* Live indicator */}
            <div className="flex items-center justify-between rounded-lg border border-ink-700/60 bg-ink-900/60 px-4 py-3">
              <div className="flex items-center gap-2">
                {status?.running ? (
                  <>
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="absolute inline-flex h-full w-full animate-pulse rounded-full bg-orange-500 opacity-75" />
                      <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-orange-400" />
                    </span>
                    <span className="text-sm font-medium text-orange-300">Active</span>
                  </>
                ) : (
                  <>
                    <span className="h-2.5 w-2.5 rounded-full bg-slate-600" />
                    <span className="text-sm font-medium text-slate-400">Idle</span>
                  </>
                )}
              </div>
              {status?.running && (
                <div className="flex items-center gap-1.5 font-mono text-lg font-semibold text-orange-300">
                  <Timer size={16} className="text-orange-400" />
                  {formatCountdown(localCountdown)}
                </div>
              )}
            </div>

            {status?.running && (
              <p className="text-xs text-slate-500">
                Next random attack in{' '}
                <span className="font-mono text-orange-300">{formatCountdown(localCountdown)}</span>
              </p>
            )}

            {/* Interval input */}
            <div className="flex items-center gap-3">
              <label className="w-36 shrink-0 text-sm text-slate-300">Interval (seconds)</label>
              <Input
                type="number"
                min={5}
                max={3600}
                value={intervalSecs}
                onChange={(e) => setIntervalSecs(Number(e.target.value))}
                className="w-28"
                disabled={status?.running}
              />
            </div>

            {/* Start / Stop */}
            {status?.running ? (
              <Button
                variant="danger"
                onClick={() => stopMut.mutate()}
                loading={stopMut.isPending}
                className="w-full"
              >
                <StopCircle size={16} />
                Stop Auto-attack
              </Button>
            ) : (
              <Button
                onClick={() => startMut.mutate()}
                loading={startMut.isPending}
                className="w-full"
              >
                <Play size={16} />
                Start Auto-attack
              </Button>
            )}
          </CardBody>
        </Card>

        {/* Last result */}
        <Card>
          <CardHeader title="Last result" description="Most recent scenario execution" />
          <CardBody>
            {result ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between rounded-lg border border-ink-700/60 bg-ink-900/60 px-4 py-3">
                  <span className="text-xs uppercase tracking-widest text-slate-500">Scenario</span>
                  <span className="rounded-md bg-accent/10 px-2.5 py-0.5 text-sm font-semibold text-accent">
                    {result.scenario}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-lg border border-ink-700/60 bg-ink-900/60 px-4 py-3 text-center">
                    <div className="text-2xl font-bold font-mono text-slate-100">
                      {result.payloads_sent}
                    </div>
                    <div className="mt-1 text-xs text-slate-500">Payloads sent</div>
                  </div>
                  <div className="rounded-lg border border-ink-700/60 bg-ink-900/60 px-4 py-3 text-center">
                    <div
                      className={cn(
                        'text-2xl font-bold font-mono',
                        result.alerts_created > 0 ? 'text-orange-300' : 'text-slate-400'
                      )}
                    >
                      {result.alerts_created}
                    </div>
                    <div className="mt-1 text-xs text-slate-500">Alerts created</div>
                  </div>
                </div>
                {status?.last_scenario && !lastRun && (
                  <p className="text-xs text-slate-500">
                    Via auto-attack · last scenario: {status.last_scenario}
                  </p>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-slate-500">
                <Activity size={32} className="mb-2 opacity-30" />
                <p className="text-sm">No scenarios run yet</p>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Manual scenarios */}
      <Card>
        <CardHeader
          title="Manual scenarios"
          description="Fire a specific attack pattern immediately through the detection pipeline"
        />
        <CardBody>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            {SCENARIOS.map((s) => (
              <button
                key={s.id}
                onClick={() => runMut.mutate(s.id)}
                disabled={runMut.isPending}
                className={cn(
                  'group flex flex-col gap-2 rounded-xl border p-4 text-left transition-all',
                  'border-ink-700/60 bg-ink-900/40 hover:border-accent/40 hover:bg-ink-800/60',
                  'disabled:cursor-not-allowed disabled:opacity-60',
                  runningScenario === s.id && 'border-accent/60 bg-accent/5'
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-slate-200 group-hover:text-white">
                    {s.label}
                  </span>
                  {runningScenario === s.id ? (
                    <Spinner size={14} />
                  ) : (
                    <Zap
                      size={14}
                      className="text-slate-500 transition-colors group-hover:text-accent"
                    />
                  )}
                </div>
                <p className="text-[11px] leading-relaxed text-slate-500">{s.description}</p>
              </button>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
