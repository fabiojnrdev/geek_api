import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const NAV = [
  { to: '/dashboard', icon: '⬡', label: 'Dashboard', end: true },
  { to: '/dashboard/products', icon: '📦', label: 'Produtos', end: false },
  { to: '/dashboard/categories', icon: '🗂️', label: 'Categorias', end: false },
  { to: '/dashboard/profile', icon: '👤', label: 'Perfil', end: false },
];

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-zinc-950 border-r border-zinc-800/60 flex flex-col z-40">
      {/* Logo */}
      <div className="p-6 border-b border-zinc-800/60">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center text-xl shadow-lg shadow-violet-900/40">
            🎮
          </div>
          <div>
            <p className="font-bold text-white text-sm tracking-widest uppercase">Geek Store</p>
            <p className="text-violet-400/70 text-xs font-medium">Admin Panel</p>
          </div>
        </div>
      </div>

      {/* Decorative accent line */}
      <div className="h-px bg-gradient-to-r from-transparent via-violet-500/30 to-transparent" />

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {NAV.map(({ to, icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150
               ${isActive
                ? 'bg-violet-600/90 text-white shadow-md shadow-violet-600/30 ring-1 ring-violet-500/30'
                : 'text-zinc-400 hover:bg-zinc-800/70 hover:text-zinc-100'}`
            }
          >
            <span className="text-base w-5 text-center">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Version tag */}
      <div className="px-4 pb-2">
        <span className="text-xs text-zinc-700 font-mono">v1.0.0</span>
      </div>

      {/* User */}
      <div className="p-4 border-t border-zinc-800/60">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-zinc-900/80 ring-1 ring-zinc-800/50">
          <div className="w-8 h-8 rounded-full bg-violet-700 flex items-center justify-center text-xs font-bold text-white shrink-0">
            {user?.username?.[0]?.toUpperCase() ?? 'A'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-zinc-200 truncate">{user?.username}</p>
            <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-zinc-600 hover:text-red-400 transition-colors text-sm p-1 rounded hover:bg-red-500/10"
            title="Sair"
          >
            ⏻
          </button>
        </div>
      </div>
    </aside>
  );
};