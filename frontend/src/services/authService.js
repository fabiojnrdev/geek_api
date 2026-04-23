import { api } from './api';

export const authService = {
  async register(data) {
    const res = await api.post('/auth/register', data);
    return res.data;
  },

  async login(data) {
    const res = await api.post('/auth/login-json', data);
    localStorage.setItem('access_token', res.data.access_token);
    return res.data;
  },

  async loginForm(username, password) {
    const form = new URLSearchParams({ username, password });
    const res = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    localStorage.setItem('access_token', res.data.access_token);
    return res.data;
  },

  async me() {
    const res = await api.get('/auth/me');
    return res.data;
  },

  async updateEmail(email) {
    const res = await api.put('/auth/me', null, { params: { email } });
    return res.data;
  },

  async changePassword(currentPassword, newPassword) {
    await api.post('/auth/change-password', null, {
      params: { current_password: currentPassword, new_password: newPassword },
    });
  },

  logout() {
    localStorage.removeItem('access_token');
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },
};
