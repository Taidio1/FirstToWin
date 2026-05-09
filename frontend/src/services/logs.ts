import { api, USE_MOCK } from './api';
import { mock } from './mock';
import { NetworkLog, Paginated } from '@/types';

export interface LogQuery {
  page?: number;
  page_size?: number;
  q?: string;
}

export async function listLogs(params: LogQuery): Promise<Paginated<NetworkLog>> {
  if (USE_MOCK) return mock.listLogs(params);
  const res = await api.get<Paginated<NetworkLog>>('/logs', { params });
  return res.data;
}
