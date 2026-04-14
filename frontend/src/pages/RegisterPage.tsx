import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button, Input } from '../components/ui';
import { useAuthStore } from '../store/authStore';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' });
  const [localError, setLocalError] = useState<string | null>(null);

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);

    if (form.password !== form.confirm) {
      setLocalError('As senhas não conferem');
      return;
    }
    if (form.password.length < 6) {
      setLocalError('A senha deve ter pelo menos 6 caracteres');
      return;
    }

    try {
      await register({ username: form.username, email: form.email, password: form.password });
      navigate('/login');
    } catch {
      /* error shown via store */
    }
  };

  const displayError = localError ?? error;

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-violet-600/8 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-sm relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-violet-600 text-3xl mb-4 shadow-lg shadow-violet-600/30">
            🎮
          </div>
          <h1 className="text-2xl font-bold text-white">Geek Store</h1>
          <p className="text-zinc-500 text-sm mt-1">Criar nova conta admin</p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-zinc-100">Registrar</h2>

          {displayError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">
              {displayError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Username"
              value={form.username}
              onChange={set('username')}
              placeholder="seunome"
              required
              minLength={3}
              autoComplete="username"
            />
            <Input
              label="Email"
              type="email"
              value={form.email}
              onChange={set('email')}
              placeholder="email@exemplo.com"
              required
              autoComplete="email"
            />
            <Input
              label="Senha"
              type="password"
              value={form.password}
              onChange={set('password')}
              placeholder="••••••••"
              required
              minLength={6}
              autoComplete="new-password"
            />
            <Input
              label="Confirmar senha"
              type="password"
              value={form.confirm}
              onChange={set('confirm')}
              placeholder="••••••••"
              required
              autoComplete="new-password"
            />
            <Button type="submit" isLoading={isLoading} className="w-full" size="lg">
              Criar conta
            </Button>
          </form>

          <p className="text-center text-sm text-zinc-600">
            Já tem conta?{' '}
            <Link to="/login" className="text-violet-400 hover:text-violet-300 transition-colors">
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
