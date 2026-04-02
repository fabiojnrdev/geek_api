import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const NAV = [
  { to: '/dashboard', icon: '⬡', label: 'Dashboard' },
  { to: '/dashboard/products', icon: '📦', label: 'Produtos' },
  { to: '/dashboard/categories', icon: '🗂️', label: 'Categorias' },
  { to: '/dashboard/profile', icon: '👤', label: 'Perfil' },
];

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
  <aside className="fixed left-0 top-0 h-screen w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col z-40">
    {/* Logo */}
      <div className="p-6 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-violet-600 flex items-center justify-center text-lg">🎮</div>
          <div>
            <p className="font-bold text-white text-sm tracking-wide">GEEK STORE</p>
            <p className="text-zinc-500 text-xs">Admin Panel</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/dashboard'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150
               ${isActive
                ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/20'
                : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100'}`
            }
          >
            <span className="text-base">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="p-4 border-t border-zinc-800">
        <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-zinc-900">
          <div className="w-8 h-8 rounded-full bg-violet-700 flex items-center justify-center text-xs font-bold text-white">
            {user?.username?.[0]?.toUpperCase() ?? 'A'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-zinc-200 truncate">{user?.username}</p>
            <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-zinc-600 hover:text-red-400 transition-colors text-sm"
            title="Sair"
          >
            ⏻
          </button>
        </div>
      </div>
    </aside>
  );
};