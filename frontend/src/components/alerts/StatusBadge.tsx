import { Badge } from '@/components/ui/Badge';
import { AlertStatus } from '@/types';

export function StatusBadge({ status }: { status: AlertStatus }) {
  switch (status) {
    case 'open':
      return <Badge tone="danger">Open</Badge>;
    case 'acknowledged':
      return <Badge tone="warning">Acknowledged</Badge>;
    case 'resolved':
      return <Badge tone="success">Resolved</Badge>;
  }
}
