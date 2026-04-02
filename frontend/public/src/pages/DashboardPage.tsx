// src/pages/DashboardPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useProductStats } from '../hooks/useProducts';
import { Spinner, Card } from '../components/ui';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: string;
  accent?: string;
  sub?: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, accent = 'text-violet-400', sub }) => (
  <Card className="p-5">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs text-zinc-500 font-medium uppercase tracking-widest mb-1">{label}</p>
        <p className={`text-3xl font-bold ${accent}`}>{value}</p>
        {sub && <p className="text-xs text-zinc-600 mt-1">{sub}</p>}
      </div>
      <span className="text-2xl">{icon}</span>
    </div>
  </Card>
);

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const { stats, categoryStats, isLoading } = useProductStats();
  const navigate = useNavigate();

  const inventoryValue = stats
    ? `R$ ${stats.total_inventory_value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
    : '—';

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          Olá, {user?.username} 👋
        </h1>
        <p className="text-zinc-500 text-sm mt-1">Bem-vindo ao painel da Geek Store</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-48"><Spinner size="lg" /></div>
      ) : stats ? (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard label="Total de Produtos" value={stats.total_products} icon="📦" />
            <StatCard label="Produtos Ativos" value={stats.active_products} icon="✅" accent="text-emerald-400" />
            <StatCard label="Sem Estoque" value={stats.out_of_stock} icon="⚠️" accent="text-red-400" />
            <StatCard label="Estoque Baixo" value={stats.low_stock} icon="📉" accent="text-amber-400" sub="menos de 10 un." />
            <StatCard label="Inativos" value={stats.inactive_products} icon="🔴" accent="text-zinc-400" />
            <StatCard label="Valor do Estoque" value={inventoryValue} icon="💰" accent="text-violet-400" />
          </div>

          {/* By Category */}
          {categoryStats.length > 0 && (
            <div>
              <h2 className="text-base font-semibold text-zinc-200 mb-4">Produtos por Categoria</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {categoryStats.map((cs) => (
                  <Card
                    key={cs.category_id}
                    className="p-4 flex items-center gap-4"
                    onClick={() => navigate(`/dashboard/products?category_id=${cs.category_id}`)}
                  >
                    <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center text-lg shrink-0">
                      🗂️
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-zinc-100 truncate">{cs.category_name}</p>
                      <p className="text-xs text-zinc-500">{cs.product_count} produtos</p>
                      <p className="text-xs text-violet-400 font-medium">
                        R$ {cs.total_value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </>
      ) : null}
    </div>
  );
};