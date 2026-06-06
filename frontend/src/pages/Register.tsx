import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { extractError } from '@/services/api';

export default function Register() {
  const { register, isLoading } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await register(email, username, password);
      toast.success('Account created', 'You can now sign in.');
      navigate('/login');
    } catch (err) {
      toast.error('Registration failed', extractError(err));
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-ink-700/70 bg-ink-900/60 p-7 shadow-xl shadow-black/40 backdrop-blur">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">Request access</h2>
          <p className="mt-1 text-sm text-slate-400">
            New accounts get a default <span className="text-slate-200">user</span> role.
          </p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="field-label">Email</label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="field-label">Username</label>
            <Input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div>
            <label className="field-label">Password</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={6}
              required
            />
          </div>

          <Button type="submit" size="lg" className="w-full" loading={isLoading}>
            Create account
          </Button>
        </form>

        <div className="text-center text-xs text-slate-500">
          Already have access?{' '}
          <Link to="/login" className="text-accent hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
