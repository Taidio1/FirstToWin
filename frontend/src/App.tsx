import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { FullPageSpinner } from '@/components/ui/Spinner';
import Login from '@/pages/Login';
import Register from '@/pages/Register';

const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Alerts = lazy(() => import('@/pages/Alerts'));
const Rules = lazy(() => import('@/pages/Rules'));
const Sensors = lazy(() => import('@/pages/Sensors'));
const Logs = lazy(() => import('@/pages/Logs'));
const AttackLab = lazy(() => import('@/pages/AttackLab'));
const NotFound = lazy(() => import('@/pages/NotFound'));

export default function App() {
  return (
    <Suspense fallback={<FullPageSpinner label="Loading…" />}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/sensors" element={<Sensors />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/attack-lab" element={<AttackLab />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Route>
      </Routes>
    </Suspense>
  );
}
