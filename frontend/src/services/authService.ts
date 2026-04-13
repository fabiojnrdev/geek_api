// src/services/authService.ts
import { api } from './api';
import type { Token, User, UserCreate, UserLogin } from '../types';

export const authService = {
  async register(data: UserCreate): Promise<User> {
    const res = await api.post<User>('/auth/register', data);
    return res.data;
  },

  async login(data: UserLogin): Promise<Token> {
    const res = await api.post<Token>('/auth/login-json', data);
    localStorage.setItem('access_token', res.data.access_token);
    return res.data;
  },

  // OAuth2 form-data login (para compatibilidade com Swagger)
  async loginForm(username: string, password: string): Promise<Token> {
    const form = new URLSearchParams({ username, password });
    const res = await api.post<Token>('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    localStorage.setItem('access_token', res.data.access_token);
    return res.data;
  },

  async me(): Promise<User> {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },

  async updateEmail(email: string): Promise<User> {
    const res = await api.put<User>('/auth/me', null, { params: { email } });
    return res.data;
  },

  async changePassword(currentPassword: string, newPassword: string) {
    await api.post('/auth/change-password', null, {
      params: { current_password: currentPassword, new_password: newPassword },
    });
  },

  logout() {
    localStorage.removeItem('access_token');
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};