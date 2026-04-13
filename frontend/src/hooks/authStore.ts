import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '../services/authService';
import type { User, UserLogin, UserCreate } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (data: UserLogin) => Promise<void>;
  register: (data: UserCreate) => Promise<void>;
  fetchMe: () => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: authService.isAuthenticated(),
      isLoading: false,
      error: null,

      login: async (data) => {
        set({ isLoading: true, error: null });
        try {
          await authService.login(data);
          const user = await authService.me();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (err: any) {
          set({
            error: err.response?.data?.detail ?? 'Erro ao fazer login',
            isLoading: false,
          });
          throw err;
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          await authService.register(data);
          set({ isLoading: false });
        } catch (err: any) {
          set({
            error: err.response?.data?.detail ?? 'Erro ao registrar',
            isLoading: false,
          });
          throw err;
        }
      },

      fetchMe: async () => {
        try {
          const user = await authService.me();
          set({ user, isAuthenticated: true });
        } catch {
          set({ user: null, isAuthenticated: false });
        }
      },

      logout: () => {
        authService.logout();
        set({ user: null, isAuthenticated: false });
      },

      clearError: () => set({ error: null }),
    }),
    { name: 'auth-store', partialize: (s) => ({ user: s.user, isAuthenticated: s.isAuthenticated }) }
  )
);