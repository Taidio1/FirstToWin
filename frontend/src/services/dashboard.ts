import { api, USE_MOCK } from './api';
import { mock } from './mock';
import { DashboardStats } from '@/types';

export async function fetchDashboardStats(): Promise<DashboardStats> {
  if (USE_MOCK) return mock.stats();
  const res = await api.get<DashboardStats>('/dashboard/stats');
  return res.data;
}
