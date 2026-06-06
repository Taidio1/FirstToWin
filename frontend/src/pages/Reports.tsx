import { useQuery } from '@tanstack/react-query';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { FullPageSpinner } from '@/components/ui/Spinner';
import { RuleEffectivenessBar } from '@/components/charts/RuleEffectivenessBar';
import { ScenarioBar } from '@/components/charts/ScenarioBar';
import { fetchRulesSummary, fetchScenarioSummary, fetchTopIps } from '@/services/reports';

function riskColor(score: number): string {
  if (score >= 20) return 'text-red-400';
  if (score >= 10) return 'text-orange-400';
  if (score >= 5) return 'text-yellow-400';
  return 'text-slate-300';
}

export default function Reports() {
  const topIps = useQuery({ queryKey: ['reports', 'top-ips'], queryFn: fetchTopIps });
  const rules = useQuery({ queryKey: ['reports', 'rules'], queryFn: fetchRulesSummary });
  const scenarios = useQuery({ queryKey: ['reports', 'scenarios'], queryFn: fetchScenarioSummary });

  if (topIps.isLoading || rules.isLoading || scenarios.isLoading) {
    return <FullPageSpinner label="Loading analytics…" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Analiza danych</div>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">Analityka</h1>
      </div>

      <Card>
        <CardHeader title="Najbardziej podejrzane źródła IP" />
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider text-slate-500">
                  <th className="px-3 py-2">src_ip</th>
                  <th className="px-3 py-2">Risk</th>
                  <th className="px-3 py-2">Alerty</th>
                  <th className="px-3 py-2">Trafienia</th>
                  <th className="px-3 py-2">Critical</th>
                  <th className="px-3 py-2">High</th>
                  <th className="px-3 py-2">Reguły</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-800/70">
                {(topIps.data ?? []).map((r) => (
                  <tr key={r.src_ip} className="text-slate-300">
                    <td className="px-3 py-2 font-mono">{r.src_ip}</td>
                    <td className={`px-3 py-2 font-mono font-semibold ${riskColor(r.risk_score)}`}>
                      {r.risk_score}
                    </td>
                    <td className="px-3 py-2">{r.alerts_count}</td>
                    <td className="px-3 py-2">{r.hits_count}</td>
                    <td className="px-3 py-2">{r.critical_alerts}</td>
                    <td className="px-3 py-2">{r.high_alerts}</td>
                    <td className="px-3 py-2">{r.rules_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Skuteczność reguł (trafienia)" />
          <CardBody>
            <RuleEffectivenessBar data={rules.data ?? []} />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Logi i alerty wg scenariusza" />
          <CardBody>
            <ScenarioBar data={scenarios.data ?? []} />
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
