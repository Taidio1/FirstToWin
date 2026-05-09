import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Rule, RuleType, Severity, Protocol } from '@/types';
import { isValidIPv4, isValidPort } from '@/lib/utils';

const schema = z
  .object({
    name: z.string().min(2, 'Name is too short'),
    type: z.enum(['blacklist_ip', 'connection_threshold', 'port_scan', 'protocol_filter']),
    severity: z.enum(['critical', 'high', 'medium', 'low', 'info']),
    enabled: z.boolean(),
    description: z.string().min(4, 'Add a short description'),
    src_ip: z.string().optional(),
    dst_ip: z.string().optional(),
    dst_port: z.string().optional(),
    protocol: z.enum(['TCP', 'UDP', 'ICMP', 'OTHER']).optional(),
    threshold: z.string().optional(),
    window_seconds: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if (data.src_ip && !isValidIPv4(data.src_ip.split('/')[0])) {
      ctx.addIssue({ code: 'custom', path: ['src_ip'], message: 'Not a valid IPv4 / CIDR' });
    }
    if (data.dst_ip && !isValidIPv4(data.dst_ip.split('/')[0])) {
      ctx.addIssue({ code: 'custom', path: ['dst_ip'], message: 'Not a valid IPv4 / CIDR' });
    }
    if (data.dst_port && !isValidPort(Number(data.dst_port))) {
      ctx.addIssue({ code: 'custom', path: ['dst_port'], message: 'Port must be 0–65535' });
    }
  });

type FormValues = z.infer<typeof schema>;

interface Props {
  initial?: Rule;
  onSubmit: (data: Omit<Rule, 'id' | 'created_at' | 'hit_count'>) => void;
  onCancel: () => void;
  saving?: boolean;
}

export function RuleForm({ initial, onSubmit, onCancel, saving }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? '',
      type: initial?.type ?? 'blacklist_ip',
      severity: initial?.severity ?? 'medium',
      enabled: initial?.enabled ?? true,
      description: initial?.description ?? '',
      src_ip: initial?.match.src_ip ?? '',
      dst_ip: initial?.match.dst_ip ?? '',
      dst_port: initial?.match.dst_port?.toString() ?? '',
      protocol: initial?.match.protocol ?? undefined,
      threshold: initial?.match.threshold?.toString() ?? '',
      window_seconds: initial?.match.window_seconds?.toString() ?? '',
    },
  });

  const submit = handleSubmit((v) => {
    onSubmit({
      name: v.name,
      type: v.type as RuleType,
      severity: v.severity as Severity,
      enabled: v.enabled,
      description: v.description,
      match: {
        src_ip: v.src_ip || undefined,
        dst_ip: v.dst_ip || undefined,
        dst_port: v.dst_port ? Number(v.dst_port) : undefined,
        protocol: (v.protocol as Protocol) || undefined,
        threshold: v.threshold ? Number(v.threshold) : undefined,
        window_seconds: v.window_seconds ? Number(v.window_seconds) : undefined,
      },
    });
  });

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2">
          <label className="field-label">Rule name</label>
          <Input invalid={!!errors.name} placeholder="e.g. Block known TOR exit nodes" {...register('name')} />
          {errors.name && <p className="mt-1 text-xs text-severity-critical">{errors.name.message}</p>}
        </div>

        <div>
          <label className="field-label">Type</label>
          <Select {...register('type')}>
            <option value="blacklist_ip">Blacklist IP</option>
            <option value="connection_threshold">Connection threshold</option>
            <option value="port_scan">Port scan</option>
            <option value="protocol_filter">Protocol filter</option>
          </Select>
        </div>
        <div>
          <label className="field-label">Severity</label>
          <Select {...register('severity')}>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="info">Info</option>
          </Select>
        </div>

        <div>
          <label className="field-label">Source IP / CIDR</label>
          <Input invalid={!!errors.src_ip} placeholder="185.220.0.0/16" {...register('src_ip')} />
          {errors.src_ip && (
            <p className="mt-1 text-xs text-severity-critical">{errors.src_ip.message}</p>
          )}
        </div>
        <div>
          <label className="field-label">Destination IP</label>
          <Input invalid={!!errors.dst_ip} placeholder="10.0.0.0/24" {...register('dst_ip')} />
          {errors.dst_ip && (
            <p className="mt-1 text-xs text-severity-critical">{errors.dst_ip.message}</p>
          )}
        </div>

        <div>
          <label className="field-label">Destination port</label>
          <Input
            invalid={!!errors.dst_port}
            type="number"
            placeholder="443"
            {...register('dst_port')}
          />
          {errors.dst_port && (
            <p className="mt-1 text-xs text-severity-critical">{errors.dst_port.message}</p>
          )}
        </div>
        <div>
          <label className="field-label">Protocol</label>
          <Select {...register('protocol')}>
            <option value="">Any</option>
            <option value="TCP">TCP</option>
            <option value="UDP">UDP</option>
            <option value="ICMP">ICMP</option>
            <option value="OTHER">Other</option>
          </Select>
        </div>

        <div>
          <label className="field-label">Threshold</label>
          <Input type="number" placeholder="20" {...register('threshold')} />
        </div>
        <div>
          <label className="field-label">Window (seconds)</label>
          <Input type="number" placeholder="2" {...register('window_seconds')} />
        </div>

        <div className="col-span-2">
          <label className="field-label">Description</label>
          <Input
            invalid={!!errors.description}
            placeholder="Why this rule exists, what it catches"
            {...register('description')}
          />
          {errors.description && (
            <p className="mt-1 text-xs text-severity-critical">{errors.description.message}</p>
          )}
        </div>

        <label className="col-span-2 inline-flex items-center gap-2 text-xs text-slate-300">
          <input type="checkbox" className="accent-accent" {...register('enabled')} />
          Enabled
        </label>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {initial ? 'Save changes' : 'Create rule'}
        </Button>
      </div>
    </form>
  );
}
