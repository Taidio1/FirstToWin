import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useRealtimeAlerts } from '@/hooks/useRealtimeAlerts';
import { useToast } from '@/contexts/ToastContext';

export function Layout() {
  const toast = useToast();
  useRealtimeAlerts((alert) => {
    if (alert.severity === 'critical' || alert.severity === 'high') {
      toast.error(`New ${alert.severity} alert`, alert.rule_name);
    }
  });

  return (
    <div className="flex h-full min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="min-w-0 flex-1 px-6 py-6 lg:px-8">
          <div className="mx-auto w-full max-w-[1400px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
