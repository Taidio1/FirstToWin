import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { QueryClient } from '@tanstack/react-query';
import { USE_MOCK } from '@/services/api';
import { mock } from '@/services/mock';
import {
  AlertItem,
  DashboardStats,
  LiveAlertEvent,
  Paginated,
  Severity,
} from '@/types';

const LIVE_ALERT_EVENT = 'ndr:live-alert';
const LIVE_STATE_EVENT = 'ndr:live-state';

const severityRank: Record<Severity, number> = {
  info: 0,
  low: 1,
  medium: 2,
  high: 3,
  critical: 4,
};

type LiveState = 'connecting' | 'connected' | 'disconnected';

/**
 * Subscribes to the Docker-proxied alert WebSocket and updates React Query caches immediately.
 */
export function useRealtimeAlerts(onAlert?: (alert: AlertItem) => void) {
  const qc = useQueryClient();
  const cb = useRef(onAlert);
  cb.current = onAlert;

  useEffect(() => {
    if (USE_MOCK) {
      dispatchLiveState('connected');
      const handle = window.setInterval(() => {
        const alert = mock.generateLiveAlert();
        handleLiveEvent(qc, { type: 'alert.created', alert });
        cb.current?.(alert);
      }, 12_000);
      return () => window.clearInterval(handle);
    }

    let closedByEffect = false;
    let reconnectTimer: number | undefined;
    let socket: WebSocket | undefined;

    const connect = () => {
      dispatchLiveState('connecting');
      socket = new WebSocket(buildWebSocketUrl());

      socket.addEventListener('open', () => dispatchLiveState('connected'));
      socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(String(event.data)) as { type?: string; alert?: AlertItem };
          if (data.type !== 'alert.created' && data.type !== 'alert.updated') return;
          const liveEvent = data as LiveAlertEvent;
          handleLiveEvent(qc, liveEvent);
          cb.current?.(liveEvent.alert);
        } catch {
          /* ignore malformed payload */
        }
      });
      socket.addEventListener('close', () => {
        dispatchLiveState('disconnected');
        if (!closedByEffect) {
          reconnectTimer = window.setTimeout(connect, 2500);
        }
      });
      socket.addEventListener('error', () => {
        dispatchLiveState('disconnected');
        socket?.close();
      });
    };

    connect();

    return () => {
      closedByEffect = true;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [qc]);
}

export function useLiveAlertPulse() {
  const [alertId, setAlertId] = useState<number | null>(null);

  useEffect(() => {
    let timer: number | undefined;
    const handle = (event: Event) => {
      const alert = (event as CustomEvent<AlertItem>).detail;
      setAlertId(alert.id);
      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(() => setAlertId(null), 2500);
    };
    window.addEventListener(LIVE_ALERT_EVENT, handle);
    return () => {
      window.removeEventListener(LIVE_ALERT_EVENT, handle);
      if (timer) window.clearTimeout(timer);
    };
  }, []);

  return alertId;
}

export function useLiveConnectionState() {
  const [state, setState] = useState<LiveState>('connecting');

  useEffect(() => {
    const handle = (event: Event) => {
      setState((event as CustomEvent<LiveState>).detail);
    };
    window.addEventListener(LIVE_STATE_EVENT, handle);
    return () => window.removeEventListener(LIVE_STATE_EVENT, handle);
  }, []);

  return state;
}

function buildWebSocketUrl() {
  const base = import.meta.env.VITE_API_BASE_URL || '/api';
  const url = new URL(base, window.location.origin);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  url.pathname = `${url.pathname.replace(/\/$/, '')}/alerts/ws`;
  return url.toString();
}

function handleLiveEvent(qc: QueryClient, event: LiveAlertEvent) {
  updateAlertCaches(qc, event);
  updateDashboardCache(qc, event);
  dispatchLiveAlert(event.alert);
  qc.invalidateQueries({ queryKey: ['alerts'] });
  qc.invalidateQueries({ queryKey: ['dashboard-stats'] });
}

function updateAlertCaches(qc: QueryClient, event: LiveAlertEvent) {
  const queries = qc.getQueryCache().findAll({ queryKey: ['alerts'] });
  for (const query of queries) {
    const params = query.queryKey[1] as Record<string, unknown> | undefined;
    qc.setQueryData<Paginated<AlertItem>>(query.queryKey, (current) => {
      if (!current?.items) return current;

      const index = current.items.findIndex((item) => item.id === event.alert.id);
      if (index >= 0) {
        const items = [...current.items];
        items[index] = event.alert;
        return { ...current, items };
      }

      const page = Number(params?.page ?? 1);
      if (
        event.type !== 'alert.created' ||
        page !== 1 ||
        !alertMatchesParams(event.alert, params)
      ) {
        return current;
      }

      const pageSize = Number(params?.page_size ?? current.page_size ?? 20);
      return {
        ...current,
        total: current.total + 1,
        items: [event.alert, ...current.items].slice(0, pageSize),
      };
    });
  }
}

function alertMatchesParams(alert: AlertItem, params?: Record<string, unknown>) {
  if (!params) return true;
  if (params.severity && params.severity !== alert.severity) return false;
  if (params.status && params.status !== alert.status) return false;
  if (typeof params.q === 'string' && params.q.trim()) {
    const q = params.q.trim().toLowerCase();
    const haystack = [
      alert.rule_name,
      alert.details,
      alert.src_ip,
      alert.dst_ip,
      alert.protocol,
    ]
      .join(' ')
      .toLowerCase();
    return haystack.includes(q);
  }
  return true;
}

function updateDashboardCache(qc: QueryClient, event: LiveAlertEvent) {
  qc.setQueryData<DashboardStats>(['dashboard-stats'], (current) => {
    if (!current || event.type !== 'alert.created') return current;

    const alert = event.alert;
    const bySeverity = current.by_severity.map((item) =>
      item.severity === alert.severity ? { ...item, count: item.count + 1 } : item
    );
    const sourceMap = new Map(
      current.top_sources.map((source) => [source.ip, { ...source }])
    );
    const existing = sourceMap.get(alert.src_ip);
    sourceMap.set(alert.src_ip, {
      ip: alert.src_ip,
      count: (existing?.count ?? 0) + 1,
      severity:
        existing && severityRank[existing.severity] > severityRank[alert.severity]
          ? existing.severity
          : alert.severity,
    });

    return {
      ...current,
      alerts_24h: current.alerts_24h + 1,
      alerts_open: alert.status === 'open' ? current.alerts_open + 1 : current.alerts_open,
      alerts_critical_open:
        alert.status === 'open' && alert.severity === 'critical'
          ? current.alerts_critical_open + 1
          : current.alerts_critical_open,
      by_severity: bySeverity,
      alerts_timeline: current.alerts_timeline.map((point, index, all) =>
        index === all.length - 1 ? { ...point, count: point.count + 1 } : point
      ),
      top_sources: [...sourceMap.values()].sort((a, b) => b.count - a.count).slice(0, 5),
    };
  });
}

function dispatchLiveAlert(alert: AlertItem) {
  window.dispatchEvent(new CustomEvent(LIVE_ALERT_EVENT, { detail: alert }));
}

function dispatchLiveState(state: LiveState) {
  window.dispatchEvent(new CustomEvent(LIVE_STATE_EVENT, { detail: state }));
}
