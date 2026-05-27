import { api, USE_MOCK, setAuthToken } from './api';
import { mock } from './mock';
import { AuthResponse, User } from '@/types';

export async function login(email: string, password: string): Promise<AuthResponse> {
  if (USE_MOCK) {
    const { token, user } = await mock.login(email);
    setAuthToken(token);
    return { access_token: token, token_type: 'bearer', user };
  }
  const res = await api.post<AuthResponse>('/auth/login', { email, password });
  setAuthToken(res.data.access_token);
  return res.data;
}

export async function register(email: string, username: string, password: string): Promise<User> {
  if (USE_MOCK) {
    return {
      id: 2,
      email,
      username,
      role: 'user',
      created_at: new Date().toISOString(),
    };
  }
  const res = await api.post<User>('/auth/register', { email, username, password });
  return res.data;
}

export function logout() {
  setAuthToken(null);
}
