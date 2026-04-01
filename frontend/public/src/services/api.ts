// src/services/api.ts
// Cliente HTTP centralizado — baseado no Axios com interceptors JWT

import axios, { type AxiosError, type AxiosRequestConfig } from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
});

// ── Injeta Bearer token em toda requisição ──────────────────
api.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    if (!config.headers) {
      config.headers = { Authorization: `Bearer ${token}` };
    } else {
      // AxiosRequestConfig['headers'] pode ser um objeto ou função; tratamos como objeto
      if (typeof config.headers === 'object' && !Array.isArray(config.headers)) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
  }
  return config;
});

// ── Trata 401 globalmente (token expirado) ──────────────────
api.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    if (error.response?.status === 401 && window.location.pathname !== '/login') {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);