import { api, USE_MOCK } from './api';
import { mock } from './mock';
import { RuleSummary, ScenarioSummary, TopIpReport } from '@/types';

export async function fetchTopIps(): Promise<TopIpReport[]> {
  if (USE_MOCK) return mock.topIps();
  const res = await api.get<TopIpReport[]>('/reports/top-ips');
  return res.data;
}

export async function fetchRulesSummary(): Promise<RuleSummary[]> {
  if (USE_MOCK) return mock.rulesSummary();
  const res = await api.get<RuleSummary[]>('/reports/rules');
  return res.data;
}

export async function fetchScenarioSummary(): Promise<ScenarioSummary[]> {
  if (USE_MOCK) return mock.scenarioSummary();
  const res = await api.get<ScenarioSummary[]>('/reports/scenarios');
  return res.data;
}
