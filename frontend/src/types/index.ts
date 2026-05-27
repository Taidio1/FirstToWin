export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type AlertStatus = 'open' | 'acknowledged' | 'resolved';
export type SensorStatus = 'online' | 'offline' | 'degraded';
export type RuleType = 'blacklist_ip' | 'connection_threshold' | 'port_scan' | 'protocol_filter';
export type Protocol = 'TCP' | 'UDP' | 'ICMP' | 'OTHER';

export interface User {
  id: number;
  email: string;
  username: string;
  role: 'admin' | 'user';
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: 'bearer';
  user: User;
}

export interface Sensor {
  id: number;
  name: string;
  location: string;
  status: SensorStatus;
  last_seen: string | null;
  packets_seen_24h: number;
  api_key_preview: string;
}

export interface SensorWithSecret extends Sensor {
  api_key: string;
}

export interface Rule {
  id: number;
  name: string;
  type: RuleType;
  enabled: boolean;
  severity: Severity;
  match: {
    src_ip?: string;
    dst_ip?: string;
    dst_port?: number;
    protocol?: Protocol;
    threshold?: number;
    window_seconds?: number;
  };
  description: string;
  created_at: string;
  hit_count: number;
}

export interface NetworkLog {
  id: number;
  sensor_id: string;
  timestamp: string;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  dst_port: number;
  protocol: Protocol;
  flags: string;
  payload_size: number;
  metadata: Record<string, unknown>;
}

export interface OsintReport {
  ip: string;
  abuse_confidence: number;
  is_malicious: boolean;
  country: string | null;
  isp: string | null;
  reports_count: number;
  last_reported_at: string | null;
  source: 'abuseipdb' | 'virustotal' | 'otx';
}

export interface AlertItem {
  id: number;
  rule_id: number;
  rule_name: string;
  severity: Severity;
  status: AlertStatus;
  src_ip: string;
  dst_ip: string;
  protocol: Protocol;
  details: string;
  created_at: string;
  sensor_id: string;
  count: number;
  last_seen: string | null;
  osint?: OsintReport | null;
}

export type LiveAlertEventType = 'alert.created' | 'alert.updated';

export interface LiveAlertEvent {
  type: LiveAlertEventType;
  alert: AlertItem;
}

export interface DashboardStats {
  alerts_24h: number;
  alerts_open: number;
  alerts_critical_open: number;
  sensors_online: number;
  sensors_total: number;
  packets_24h: number;
  by_severity: { severity: Severity; count: number }[];
  alerts_timeline: { hour: string; count: number }[];
  top_sources: { ip: string; count: number; severity: Severity }[];
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
