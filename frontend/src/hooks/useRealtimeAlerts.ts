import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { USE_MOCK } from '@/services/api';
import { mock } from '@/services/mock';
import { AlertItem } from '@/types';

/**
 * Subscribes to a real-time alert stream and pushes new items into the query cache.
 * In mock mode this synthesizes alerts on a timer so the dashboard feels alive in demos.
 * In production it connects to /api/alerts/stream via SSE — easy to swap to WebSocket later.
 */
export function useRealtimeAlerts(onAlert?: (alert: AlertItem) => void) {
  const qc = useQueryClient();
  const cb = useRef(onAlert);
  cb.current = onAlert;

  useEffect(() => {
    if (USE_MOCK) {
      const handle = window.setInterval(() => {
        const alert = mock.generateLiveAlert();
        qc.invalidateQueries({ queryKey: ['alerts'] });
        qc.invalidateQueries({ queryKey: ['dashboard-stats'] });
        cb.current?.(alert);
      }, 12_000);
      return () => window.clearInterval(handle);
    }

    const url = `${import.meta.env.VITE_API_BASE_URL || '/api'}/alerts/stream`;
    const source = new EventSource(url, { withCredentials: true });
    source.addEventListener('alert', (event) => {
      try {
        const data = JSON.parse((event as MessageEvent).data) as AlertItem;
        qc.invalidateQueries({ queryKey: ['alerts'] });
        qc.invalidateQueries({ queryKey: ['dashboard-stats'] });
        cb.current?.(data);
      } catch {
        /* ignore malformed payload */
      }
    });
    return () => source.close();
  }, [qc]);
}
