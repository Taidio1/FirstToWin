import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { getAuthToken } from '@/services/api';
import { login as loginRequest, logout as logoutRequest, register as registerRequest } from '@/services/auth';
import { User } from '@/types';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const USER_KEY = 'ndr.user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  });
  const [isLoading, setLoading] = useState(false);

  useEffect(() => {
    if (!getAuthToken()) {
      setUser(null);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const res = await loginRequest(email, password);
      setUser(res.user);
      localStorage.setItem(USER_KEY, JSON.stringify(res.user));
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, username: string, password: string) => {
    setLoading(true);
    try {
      await registerRequest(email, username, password);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    logoutRequest();
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
