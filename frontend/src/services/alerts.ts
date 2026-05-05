import { api, USE_MOCK } from './api';
import { mock } from './mock';
import { AlertItem, AlertStatus, OsintReport, Paginated, Severity } from '@/types';

export interface AlertQuery {
  page?: number;
  page_size?: number;
  severity?: Severity;
  status?: AlertStatus;
  q?: string;
}

export async function listAlerts(params: AlertQuery): Promise<Paginated<AlertItem>> {
  if (USE_MOCK) return mock.listAlerts(params);
  const res = await api.get<Paginated<AlertItem>>('/alerts', { params });
  return res.data;
}

export async function getAlert(id: number): Promise<AlertItem> {
  if (USE_MOCK) return mock.getAlert(id);
  const res = await api.get<AlertItem>(`/alerts/${id}`);
  return res.data;
}

export async function patchAlertStatus(id: number, status: AlertStatus): Promise<AlertItem> {
  if (USE_MOCK) return mock.patchAlert(id, status);
  const res = await api.patch<AlertItem>(`/alerts/${id}`, { status });
  return res.data;
}

export async function getOsintForAlert(id: number): Promise<OsintReport> {
  if (USE_MOCK) return mock.getOsint(id);
  const res = await api.get<OsintReport>(`/alerts/${id}/osint`);
  return res.data;
}
