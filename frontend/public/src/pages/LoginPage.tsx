import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button, Input } from '../components/ui';
import { useAuthStore } from '../store/authStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error, isAuthenticated, clearError } = useAuthStore();
  const [form, setForm] = useState({ username: '', password: '' });

  useEffect(() => { if (isAuthenticated) navigate('/dashboard'); }, [isAuthenticated, navigate]);

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    try {
      await login(form);
      navigate('/dashboard');
    } catch { /* error shown via store */ }
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-violet-600/10 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-sm relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-violet-600 text-3xl mb-4 shadow-lg shadow-violet-600/30">
            🎮
          </div>
          <h1 className="text-2xl font-bold text-white">Geek Store</h1>
          <p className="text-zinc-500 text-sm mt-1">Painel Administrativo</p>
        </div>

        {/* Form */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-zinc-100">Entrar</h2>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Username"
              value={form.username}
              onChange={set('username')}
              placeholder="admin"
              required
              autoComplete="username"
            />
            <Input
              label="Senha"
              type="password"
              value={form.password}
              onChange={set('password')}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
            <Button type="submit" isLoading={isLoading} className="w-full" size="lg">
              Entrar
            </Button>
          </form>

          <p className="text-center text-sm text-zinc-600">
            Não tem conta?{' '}
            <Link to="/register" className="text-violet-400 hover:text-violet-300 transition-colors">
              Registrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};