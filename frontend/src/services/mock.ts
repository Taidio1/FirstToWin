import {
  AlertItem,
  DashboardStats,
  NetworkLog,
  OsintReport,
  Paginated,
  Rule,
  Sensor,
  Severity,
  User,
} from '@/types';

const SEVERITIES: Severity[] = ['critical', 'high', 'medium', 'low', 'info'];

let alertSeq = 1024;
let ruleSeq = 8;
let sensorSeq = 4;
let logSeq = 99001;

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomIP() {
  return `${Math.floor(Math.random() * 223 + 1)}.${Math.floor(Math.random() * 256)}.${Math.floor(
    Math.random() * 256
  )}.${Math.floor(Math.random() * 256)}`;
}

const sampleRules: Rule[] = [
  {
    id: 1,
    name: 'Blacklist — TOR exit nodes',
    type: 'blacklist_ip',
    enabled: true,
    severity: 'high',
    match: { src_ip: '185.220.0.0/16' },
    description: 'Block traffic from known TOR exit nodes (curated daily).',
    created_at: '2026-04-12T09:14:22Z',
    hit_count: 142,
  },
  {
    id: 2,
    name: 'Port scan — > 20 SYN/2s',
    type: 'port_scan',
    enabled: true,
    severity: 'critical',
    match: { threshold: 20, window_seconds: 2, protocol: 'TCP' },
    description: 'Detects horizontal port scans (many destination ports in short window).',
    created_at: '2026-04-14T11:02:00Z',
    hit_count: 37,
  },
  {
    id: 3,
    name: 'Anomalous outbound RDP',
    type: 'protocol_filter',
    enabled: true,
    severity: 'medium',
    match: { dst_port: 3389, protocol: 'TCP' },
    description: 'Outbound 3389 from non-admin subnets is suspicious.',
    created_at: '2026-04-15T16:30:00Z',
    hit_count: 9,
  },
  {
    id: 4,
    name: 'Internal SSH brute force',
    type: 'connection_threshold',
    enabled: true,
    severity: 'high',
    match: { dst_port: 22, threshold: 50, window_seconds: 60, protocol: 'TCP' },
    description: '50+ failed SSH attempts to one host within a minute.',
    created_at: '2026-04-18T08:45:11Z',
    hit_count: 4,
  },
  {
    id: 5,
    name: 'DNS exfiltration heuristic',
    type: 'connection_threshold',
    enabled: false,
    severity: 'low',
    match: { dst_port: 53, threshold: 200, window_seconds: 30, protocol: 'UDP' },
    description: 'Burst of DNS queries from a single host — possible tunneling.',
    created_at: '2026-04-22T13:01:55Z',
    hit_count: 0,
  },
  {
    id: 6,
    name: 'ICMP flood',
    type: 'connection_threshold',
    enabled: true,
    severity: 'medium',
    match: { protocol: 'ICMP', threshold: 500, window_seconds: 10 },
    description: 'High ICMP volume — potential probe or DoS.',
    created_at: '2026-04-25T22:12:08Z',
    hit_count: 2,
  },
  {
    id: 7,
    name: 'AbuseIPDB confidence ≥ 80',
    type: 'blacklist_ip',
    enabled: true,
    severity: 'critical',
    match: {},
    description: 'Auto-block IPs flagged by AbuseIPDB with high confidence.',
    created_at: '2026-05-01T07:18:30Z',
    hit_count: 18,
  },
];

const sampleSensors: Sensor[] = [
  {
    id: 1,
    name: 'sensor-edge-01',
    location: 'Warsaw / DC1 — uplink',
    status: 'online',
    last_seen: new Date(Date.now() - 12_000).toISOString(),
    packets_seen_24h: 1_842_119,
    api_key_preview: 'sk_live_••••3a91',
  },
  {
    id: 2,
    name: 'sensor-core-02',
    location: 'Warsaw / DC1 — core switch',
    status: 'online',
    last_seen: new Date(Date.now() - 4_000).toISOString(),
    packets_seen_24h: 5_218_044,
    api_key_preview: 'sk_live_••••be07',
  },
  {
    id: 3,
    name: 'sensor-branch-01',
    location: 'Kraków / branch office',
    status: 'degraded',
    last_seen: new Date(Date.now() - 5 * 60_000).toISOString(),
    packets_seen_24h: 211_904,
    api_key_preview: 'sk_live_••••12cd',
  },
  {
    id: 4,
    name: 'sensor-lab-01',
    location: 'Lab / red-team segment',
    status: 'offline',
    last_seen: new Date(Date.now() - 6 * 3600_000).toISOString(),
    packets_seen_24h: 0,
    api_key_preview: 'sk_live_••••9f44',
  },
];

function randomAlert(): AlertItem {
  const severity = pick<Severity>(['critical', 'high', 'high', 'medium', 'medium', 'low', 'info']);
  const rule = pick(sampleRules);
  const src = randomIP();
  return {
    id: alertSeq++,
    rule_id: rule.id,
    rule_name: rule.name,
    severity,
    status: pick(['open', 'open', 'open', 'acknowledged', 'resolved']),
    src_ip: src,
    dst_ip: `10.0.${Math.floor(Math.random() * 8)}.${Math.floor(Math.random() * 255)}`,
    protocol: pick(['TCP', 'TCP', 'UDP', 'ICMP']),
    details:
      severity === 'critical'
        ? `${15 + Math.floor(Math.random() * 30)} SYN packets to different ports from ${src} in 2s`
        : severity === 'high'
        ? `Suspicious outbound from ${src} matching rule "${rule.name}"`
        : `Threshold exceeded for rule "${rule.name}" — see details`,
    created_at: new Date(Date.now() - Math.floor(Math.random() * 24 * 3600_000)).toISOString(),
    sensor_id: `sensor-${Math.ceil(Math.random() * 4).toString().padStart(2, '0')}`,
    osint:
      Math.random() < 0.4
        ? {
            ip: src,
            abuse_confidence: Math.floor(Math.random() * 100),
            is_malicious: Math.random() < 0.5,
            country: pick(['RU', 'CN', 'US', 'DE', 'BR', 'IN', 'NL']),
            isp: pick(['Hetzner', 'OVH', 'DigitalOcean', 'Cloudflare', 'Tencent', 'Unknown']),
            reports_count: Math.floor(Math.random() * 200),
            last_reported_at: new Date(Date.now() - Math.random() * 90 * 86_400_000).toISOString(),
            source: 'abuseipdb',
          }
        : null,
  };
}

const sampleAlerts: AlertItem[] = Array.from({ length: 64 }, () => randomAlert()).sort(
  (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
);

function delay<T>(value: T, ms = 220): Promise<T> {
  return new Promise((res) => setTimeout(() => res(value), ms));
}

export const mock = {
  async login(email: string): Promise<{ token: string; user: User }> {
    return delay({
      token: 'mock.jwt.token',
      user: {
        id: 1,
        email,
        username: email.split('@')[0],
        role: 'admin',
        created_at: '2026-04-09T18:00:00Z',
      },
    });
  },

  async stats(): Promise<DashboardStats> {
    const open = sampleAlerts.filter((a) => a.status === 'open');
    const critical = open.filter((a) => a.severity === 'critical');
    const bySev = SEVERITIES.map((s) => ({
      severity: s,
      count: sampleAlerts.filter((a) => a.severity === s).length,
    }));
    const now = new Date();
    const timeline = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date(now.getTime() - (23 - i) * 3600_000);
      return {
        hour: hour.toISOString(),
        count: Math.max(0, Math.floor(8 + Math.sin(i / 2) * 5 + Math.random() * 6)),
      };
    });
    const topSourcesMap = new Map<string, { count: number; severity: Severity }>();
    for (const a of sampleAlerts) {
      const cur = topSourcesMap.get(a.src_ip) ?? { count: 0, severity: a.severity };
      cur.count += 1;
      topSourcesMap.set(a.src_ip, cur);
    }
    const top = Array.from(topSourcesMap.entries())
      .map(([ip, v]) => ({ ip, ...v }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6);
    return delay({
      alerts_24h: sampleAlerts.length,
      alerts_open: open.length,
      alerts_critical_open: critical.length,
      sensors_online: sampleSensors.filter((s) => s.status === 'online').length,
      sensors_total: sampleSensors.length,
      packets_24h: sampleSensors.reduce((sum, s) => sum + s.packets_seen_24h, 0),
      by_severity: bySev,
      alerts_timeline: timeline,
      top_sources: top,
    });
  },

  async listAlerts(params: {
    page?: number;
    page_size?: number;
    severity?: Severity;
    status?: AlertItem['status'];
    q?: string;
  }): Promise<Paginated<AlertItem>> {
    const page = params.page ?? 1;
    const pageSize = params.page_size ?? 20;
    let filtered = sampleAlerts;
    if (params.severity) filtered = filtered.filter((a) => a.severity === params.severity);
    if (params.status) filtered = filtered.filter((a) => a.status === params.status);
    if (params.q) {
      const q = params.q.toLowerCase();
      filtered = filtered.filter(
        (a) =>
          a.src_ip.includes(q) ||
          a.dst_ip.includes(q) ||
          a.rule_name.toLowerCase().includes(q) ||
          a.details.toLowerCase().includes(q)
      );
    }
    const start = (page - 1) * pageSize;
    return delay({
      items: filtered.slice(start, start + pageSize),
      total: filtered.length,
      page,
      page_size: pageSize,
    });
  },

  async getAlert(id: number): Promise<AlertItem> {
    const found = sampleAlerts.find((a) => a.id === id);
    if (!found) throw new Error('Alert not found');
    return delay(found);
  },

  async patchAlert(id: number, status: AlertItem['status']): Promise<AlertItem> {
    const found = sampleAlerts.find((a) => a.id === id);
    if (!found) throw new Error('Alert not found');
    found.status = status;
    return delay(found);
  },

  async getOsint(id: number): Promise<OsintReport> {
    const found = sampleAlerts.find((a) => a.id === id);
    if (!found) throw new Error('Alert not found');
    if (found.osint) return delay(found.osint);
    const fresh: OsintReport = {
      ip: found.src_ip,
      abuse_confidence: Math.floor(Math.random() * 100),
      is_malicious: Math.random() < 0.4,
      country: pick(['RU', 'CN', 'US', 'DE', 'NL']),
      isp: pick(['OVH', 'Hetzner', 'DigitalOcean', 'Unknown']),
      reports_count: Math.floor(Math.random() * 100),
      last_reported_at: new Date(Date.now() - Math.random() * 30 * 86_400_000).toISOString(),
      source: 'abuseipdb',
    };
    found.osint = fresh;
    return delay(fresh);
  },

  async listRules(): Promise<Rule[]> {
    return delay([...sampleRules]);
  },
  async createRule(input: Omit<Rule, 'id' | 'created_at' | 'hit_count'>): Promise<Rule> {
    const r: Rule = {
      ...input,
      id: ++ruleSeq,
      created_at: new Date().toISOString(),
      hit_count: 0,
    };
    sampleRules.unshift(r);
    return delay(r);
  },
  async updateRule(id: number, input: Partial<Rule>): Promise<Rule> {
    const idx = sampleRules.findIndex((r) => r.id === id);
    if (idx === -1) throw new Error('Rule not found');
    sampleRules[idx] = { ...sampleRules[idx], ...input };
    return delay(sampleRules[idx]);
  },
  async deleteRule(id: number): Promise<void> {
    const idx = sampleRules.findIndex((r) => r.id === id);
    if (idx === -1) throw new Error('Rule not found');
    sampleRules.splice(idx, 1);
    return delay(undefined);
  },

  async listSensors(): Promise<Sensor[]> {
    return delay([...sampleSensors]);
  },
  async createSensor(name: string, location: string) {
    const apiKey = `sk_live_${Math.random().toString(36).slice(2, 10)}${Math.random()
      .toString(36)
      .slice(2, 10)}`;
    const s: Sensor = {
      id: ++sensorSeq,
      name,
      location,
      status: 'offline',
      last_seen: null,
      packets_seen_24h: 0,
      api_key_preview: `sk_live_••••${apiKey.slice(-4)}`,
    };
    sampleSensors.push(s);
    return delay({ ...s, api_key: apiKey });
  },
  async deleteSensor(id: number) {
    const idx = sampleSensors.findIndex((s) => s.id === id);
    if (idx === -1) throw new Error('Sensor not found');
    sampleSensors.splice(idx, 1);
    return delay(undefined);
  },

  async listLogs(params: { page?: number; page_size?: number; q?: string }): Promise<
    Paginated<NetworkLog>
  > {
    const page = params.page ?? 1;
    const pageSize = params.page_size ?? 50;
    const total = 240;
    const start = (page - 1) * pageSize;
    const items = Array.from({ length: Math.min(pageSize, total - start) }, (_, i) => {
      const proto = pick(['TCP', 'TCP', 'UDP', 'ICMP']);
      return {
        id: logSeq + start + i,
        sensor_id: `sensor-0${(i % 3) + 1}`,
        timestamp: new Date(Date.now() - (start + i) * 1500).toISOString(),
        src_ip: randomIP(),
        dst_ip: `10.0.${i % 8}.${(i * 7) % 254}`,
        src_port: 1024 + Math.floor(Math.random() * 60_000),
        dst_port: pick([22, 53, 80, 443, 3389, 8080]),
        protocol: proto,
        flags: proto === 'TCP' ? pick(['SYN', 'SYN,ACK', 'ACK', 'FIN,ACK', 'RST']) : '',
        payload_size: Math.floor(Math.random() * 1500),
        metadata: { interface: pick(['eth0', 'eth1', 'wlan0']) },
      } as NetworkLog;
    });
    const filtered = params.q
      ? items.filter(
          (l) =>
            l.src_ip.includes(params.q!) ||
            l.dst_ip.includes(params.q!) ||
            l.sensor_id.includes(params.q!)
        )
      : items;
    return delay({ items: filtered, total, page, page_size: pageSize });
  },

  // Streaming-like helper used by useRealtimeAlerts.
  generateLiveAlert(): AlertItem {
    const a = randomAlert();
    a.created_at = new Date().toISOString();
    a.status = 'open';
    sampleAlerts.unshift(a);
    return a;
  },
};
