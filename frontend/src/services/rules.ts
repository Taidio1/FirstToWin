import { api, USE_MOCK } from './api';
import { mock } from './mock';
import { Rule } from '@/types';

export type RuleInput = Omit<Rule, 'id' | 'created_at' | 'hit_count'>;

export async function listRules(): Promise<Rule[]> {
  if (USE_MOCK) return mock.listRules();
  const res = await api.get<Rule[]>('/rules');
  return res.data;
}

export async function createRule(input: RuleInput): Promise<Rule> {
  if (USE_MOCK) return mock.createRule(input);
  const res = await api.post<Rule>('/rules', input);
  return res.data;
}

export async function updateRule(id: number, input: Partial<RuleInput>): Promise<Rule> {
  if (USE_MOCK) return mock.updateRule(id, input);
  const res = await api.put<Rule>(`/rules/${id}`, input);
  return res.data;
}

export async function deleteRule(id: number): Promise<void> {
  if (USE_MOCK) return mock.deleteRule(id);
  await api.delete(`/rules/${id}`);
}
