import { api } from './api';

export interface AttackLabStatus {
  running: boolean;
  interval_seconds: number;
  next_run_at: string | null;
  seconds_remaining: number | null;
  last_scenario: string | null;
  last_result: RunResult | null;
}

export interface RunResult {
  scenario: string;
  payloads_sent: number;
  alerts_created: number;
}

export const SCENARIOS = [
  { id: 'normal', label: 'Normal Traffic', description: 'Simulates benign network activity' },
  { id: 'port-scan', label: 'Port Scan', description: 'Scans multiple destination ports' },
  { id: 'ssh-bruteforce', label: 'SSH Brute Force', description: 'Repeated SSH connection attempts' },
  { id: 'blacklist', label: 'Blacklist IP', description: 'Traffic from a known blacklisted IP' },
  { id: 'full-demo', label: 'Full Demo', description: 'All attack scenarios in sequence' },
] as const;

export async function getAttackLabStatus(): Promise<AttackLabStatus> {
  const res = await api.get<AttackLabStatus>('/attack-lab/status');
  return res.data;
}

export async function runScenario(scenario: string): Promise<RunResult> {
  const res = await api.post<RunResult>('/attack-lab/run', { scenario });
  return res.data;
}

export async function startAutoAttack(interval_seconds: number): Promise<AttackLabStatus> {
  const res = await api.post<AttackLabStatus>('/attack-lab/auto/start', { interval_seconds });
  return res.data;
}

export async function stopAutoAttack(): Promise<AttackLabStatus> {
  const res = await api.post<AttackLabStatus>('/attack-lab/auto/stop');
  return res.data;
}
