import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { authService } from '../services/authService';
import { Button, Input, Card } from '../components/ui';

export const ProfilePage: React.FC = () => {
  const { user, fetchMe } = useAuthStore();
  const [emailForm, setEmailForm] = useState({ email: user?.email ?? '' });
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' });
  const [emailLoading, setEmailLoading] = useState(false);
  const [pwLoading, setPwLoading] = useState(false);
  const [emailMsg, setEmailMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [pwMsg, setPwMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleEmailUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailLoading(true);
    setEmailMsg(null);
    try {
      await authService.updateEmail(emailForm.email);
      await fetchMe();
      setEmailMsg({ type: 'success', text: 'Email atualizado com sucesso!' });
    } catch (err: any) {
      setEmailMsg({ type: 'error', text: err.response?.data?.detail ?? 'Erro ao atualizar email' });
    } finally {
      setEmailLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwMsg(null);
    if (pwForm.newPw !== pwForm.confirm) {
      setPwMsg({ type: 'error', text: 'As novas senhas não conferem' });
      return;
    }
    if (pwForm.newPw.length < 6) {
      setPwMsg({ type: 'error', text: 'A nova senha deve ter pelo menos 6 caracteres' });
      return;
    }
    setPwLoading(true);
    try {
      await authService.changePassword(pwForm.current, pwForm.newPw);
      setPwForm({ current: '', newPw: '', confirm: '' });
      setPwMsg({ type: 'success', text: 'Senha alterada com sucesso!' });
    } catch (err: any) {
      setPwMsg({ type: 'error', text: err.response?.data?.detail ?? 'Erro ao alterar senha' });
    } finally {
      setPwLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Perfil</h1>
        <p className="text-zinc-500 text-sm mt-0.5">Gerencie suas informações de conta</p>
      </div>

      {/* User Info Card */}
      <Card className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-2xl bg-violet-700 flex items-center justify-center text-2xl font-bold text-white shadow-lg shadow-violet-900/40">
            {user?.username?.[0]?.toUpperCase() ?? 'A'}
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">{user?.username}</h2>
            <p className="text-sm text-zinc-400">{user?.email}</p>
            <span className="inline-flex items-center gap-1 mt-1 text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Ativo
            </span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm border-t border-zinc-800 pt-4">
          <div>
            <p className="text-zinc-500 text-xs mb-0.5">Username</p>
            <p className="text-zinc-200 font-mono">{user?.username}</p>
          </div>
          <div>
            <p className="text-zinc-500 text-xs mb-0.5">Membro desde</p>
            <p className="text-zinc-200">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString('pt-BR')
                : '—'}
            </p>
          </div>
        </div>
      </Card>

      {/* Update Email */}
      <Card className="p-6">
        <h3 className="font-semibold text-zinc-100 mb-4 flex items-center gap-2">
          <span>📧</span> Atualizar Email
        </h3>
        <form onSubmit={handleEmailUpdate} className="space-y-4">
          {emailMsg && (
            <div
              className={`border rounded-xl p-3 text-sm ${
                emailMsg.type === 'success'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : 'bg-red-500/10 border-red-500/30 text-red-400'
              }`}
            >
              {emailMsg.text}
            </div>
          )}
          <Input
            label="Novo email"
            type="email"
            value={emailForm.email}
            onChange={(e) => setEmailForm({ email: e.target.value })}
            required
          />
          <Button type="submit" isLoading={emailLoading} variant="secondary">
            Atualizar email
          </Button>
        </form>
      </Card>

      {/* Change Password */}
      <Card className="p-6">
        <h3 className="font-semibold text-zinc-100 mb-4 flex items-center gap-2">
          <span>🔐</span> Alterar Senha
        </h3>
        <form onSubmit={handlePasswordChange} className="space-y-4">
          {pwMsg && (
            <div
              className={`border rounded-xl p-3 text-sm ${
                pwMsg.type === 'success'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : 'bg-red-500/10 border-red-500/30 text-red-400'
              }`}
            >
              {pwMsg.text}
            </div>
          )}
          <Input
            label="Senha atual"
            type="password"
            value={pwForm.current}
            onChange={(e) => setPwForm((f) => ({ ...f, current: e.target.value }))}
            required
            autoComplete="current-password"
          />
          <Input
            label="Nova senha"
            type="password"
            value={pwForm.newPw}
            onChange={(e) => setPwForm((f) => ({ ...f, newPw: e.target.value }))}
            required
            minLength={6}
            autoComplete="new-password"
          />
          <Input
            label="Confirmar nova senha"
            type="password"
            value={pwForm.confirm}
            onChange={(e) => setPwForm((f) => ({ ...f, confirm: e.target.value }))}
            required
            autoComplete="new-password"
          />
          <Button type="submit" isLoading={pwLoading} variant="secondary">
            Alterar senha
          </Button>
        </form>
      </Card>
    </div>
  );
};
