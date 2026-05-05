import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const schema = z.object({
  name: z.string().min(3, 'Name is too short'),
  location: z.string().min(2, 'Add a short location/description'),
});

export type SensorFormValues = z.infer<typeof schema>;

export function SensorForm({
  onSubmit,
  onCancel,
  saving,
}: {
  onSubmit: (v: SensorFormValues) => void;
  onCancel: () => void;
  saving?: boolean;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SensorFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', location: '' },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="field-label">Name</label>
        <Input
          invalid={!!errors.name}
          placeholder="sensor-edge-03"
          {...register('name')}
        />
        {errors.name && <p className="mt-1 text-xs text-severity-critical">{errors.name.message}</p>}
      </div>
      <div>
        <label className="field-label">Location</label>
        <Input
          invalid={!!errors.location}
          placeholder="Warsaw / DC1 — uplink"
          {...register('location')}
        />
        {errors.location && (
          <p className="mt-1 text-xs text-severity-critical">{errors.location.message}</p>
        )}
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          Register sensor
        </Button>
      </div>
    </form>
  );
}
