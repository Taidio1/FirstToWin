import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Pencil, Plus, ShieldCheck, ShieldOff, Trash2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Spinner } from '@/components/ui/Spinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { SeverityBadge } from '@/components/alerts/SeverityBadge';
import { Badge } from '@/components/ui/Badge';
import { RuleForm } from '@/components/rules/RuleForm';
import { listRules, createRule, updateRule, deleteRule } from '@/services/rules';
import { useToast } from '@/contexts/ToastContext';
import { extractError } from '@/services/api';
import { Rule } from '@/types';
import { formatDateTime } from '@/lib/utils';

const TYPE_LABELS: Record<Rule['type'], string> = {
  blacklist_ip: 'Blacklist IP',
  connection_threshold: 'Threshold',
  port_scan: 'Port scan',
  protocol_filter: 'Protocol',
};

export default function Rules() {
  const qc = useQueryClient();
  const toast = useToast();
  const [editing, setEditing] = useState<Rule | null>(null);
  const [creating, setCreating] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<Rule | null>(null);

  const { data: rules, isLoading } = useQuery({ queryKey: ['rules'], queryFn: listRules });

  const create = useMutation({
    mutationFn: createRule,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rules'] });
      setCreating(false);
      toast.success('Rule created');
    },
    onError: (e) => toast.error('Could not create rule', extractError(e)),
  });

  const update = useMutation({
    mutationFn: ({ id, input }: { id: number; input: Partial<Rule> }) => updateRule(id, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rules'] });
      setEditing(null);
      toast.success('Rule saved');
    },
    onError: (e) => toast.error('Could not save rule', extractError(e)),
  });

  const remove = useMutation({
    mutationFn: deleteRule,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rules'] });
      setConfirmDelete(null);
      toast.success('Rule removed');
    },
    onError: (e) => toast.error('Could not delete rule', extractError(e)),
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">Detection rules</h1>
          <p className="text-sm text-slate-400">
            Define what triggers an alert. Rules are evaluated on every incoming log.
          </p>
        </div>
        <Button onClick={() => setCreating(true)}>
          <Plus size={14} /> New rule
        </Button>
      </div>

      <Card>
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : rules && rules.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-ink-700/70 text-left text-[11px] uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3">Rule</th>
                  <th className="px-5 py-3">Type</th>
                  <th className="px-5 py-3">Severity</th>
                  <th className="px-5 py-3">Hits</th>
                  <th className="px-5 py-3">State</th>
                  <th className="px-5 py-3">Created</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-800/70">
                {rules.map((r) => (
                  <tr key={r.id} className="hover:bg-ink-800/40">
                    <td className="px-5 py-3.5">
                      <div className="text-slate-100">{r.name}</div>
                      <div className="mt-0.5 max-w-md truncate text-xs text-slate-500">
                        {r.description}
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-5 py-3.5">
                      <Badge tone="muted">{TYPE_LABELS[r.type]}</Badge>
                    </td>
                    <td className="whitespace-nowrap px-5 py-3.5">
                      <SeverityBadge severity={r.severity} />
                    </td>
                    <td className="whitespace-nowrap px-5 py-3.5 font-mono text-xs text-slate-300">
                      {r.hit_count ?? 0}
                    </td>
                    <td className="whitespace-nowrap px-5 py-3.5">
                      {r.enabled ? (
                        <Badge tone="success">
                          <ShieldCheck size={11} /> enabled
                        </Badge>
                      ) : (
                        <Badge tone="muted">
                          <ShieldOff size={11} /> disabled
                        </Badge>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-5 py-3.5 text-xs text-slate-400">
                      {r.created_at ? formatDateTime(r.created_at) : '—'}
                    </td>
                    <td className="whitespace-nowrap px-5 py-3.5">
                      <div className="flex justify-end gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() =>
                            update.mutate({ id: r.id, input: { enabled: !r.enabled } })
                          }
                          title={r.enabled ? 'Disable' : 'Enable'}
                        >
                          {r.enabled ? <ShieldOff size={14} /> : <ShieldCheck size={14} />}
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setEditing(r)}>
                          <Pencil size={14} />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setConfirmDelete(r)}
                          className="text-severity-critical hover:bg-severity-critical/10"
                        >
                          <Trash2 size={14} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="No detection rules yet"
            description="Add a rule so the engine has something to match against."
            action={<Button onClick={() => setCreating(true)}>Create your first rule</Button>}
          />
        )}
      </Card>

      <Modal
        open={creating}
        onClose={() => setCreating(false)}
        title="Create detection rule"
        description="Match logs against criteria — when matched, an alert is generated."
        size="lg"
      >
        <RuleForm
          onCancel={() => setCreating(false)}
          onSubmit={(d) => create.mutate(d)}
          saving={create.isPending}
        />
      </Modal>

      <Modal
        open={!!editing}
        onClose={() => setEditing(null)}
        title="Edit rule"
        description={editing?.name}
        size="lg"
      >
        {editing && (
          <RuleForm
            initial={editing}
            onCancel={() => setEditing(null)}
            onSubmit={(d) => update.mutate({ id: editing.id, input: d })}
            saving={update.isPending}
          />
        )}
      </Modal>

      <Modal
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        title="Delete rule?"
        description="This action cannot be undone. Existing alerts are preserved."
        footer={
          <>
            <Button variant="ghost" onClick={() => setConfirmDelete(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              loading={remove.isPending}
              onClick={() => confirmDelete && remove.mutate(confirmDelete.id)}
            >
              Delete rule
            </Button>
          </>
        }
      >
        <p className="text-sm text-slate-300">
          Remove rule{' '}
          <span className="font-medium text-slate-100">{confirmDelete?.name}</span>?
        </p>
      </Modal>
    </div>
  );
}
