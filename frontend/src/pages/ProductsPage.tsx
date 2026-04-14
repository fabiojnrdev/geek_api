import React, { useState, useCallback } from 'react';
import { useProducts } from '../hooks/useProducts';
import { useCategories } from '../hooks/useCategories';
import { productService } from '../services/productService';
import { ProductCard } from '../components/products/ProductCard';
import { ProductForm } from '../components/products/ProductForm';
import { Button, Input, Spinner, EmptyState } from '../components/ui';
import type { Product } from '../types';

export const ProductsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Product | null>(null);
  const [searchValue, setSearchValue] = useState('');

  const { data, isLoading, error, filters, setFilters, refetch } = useProducts({
    limit: 20,
    is_active: undefined,
  });
  const { categories } = useCategories();

  const handleSearch = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setSearchValue(val);
      setFilters((f) => ({ ...f, search: val || undefined, skip: 0 }));
    },
    [setFilters]
  );

  const handleDelete = async (p: Product) => {
    try {
      await productService.delete(p.id);
      refetch();
    } catch {
      alert('Erro ao deletar produto');
    } finally {
      setConfirmDelete(null);
    }
  };

  const handleToggle = async (p: Product) => {
    await productService.toggleActive(p.id);
    refetch();
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingProduct(null);
    refetch();
  };

  const products = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Produtos</h1>
          <p className="text-zinc-500 text-sm mt-0.5">
            {total > 0 ? `${total} produto${total !== 1 ? 's' : ''} encontrado${total !== 1 ? 's' : ''}` : 'Nenhum produto'}
          </p>
        </div>
        <Button
          onClick={() => { setEditingProduct(null); setShowForm(true); }}
          leftIcon={<span>✨</span>}
        >
          Novo Produto
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <Input
            placeholder="🔍 Buscar por nome, franquia..."
            value={searchValue}
            onChange={handleSearch}
          />
          <select
            value={filters.category_id ?? ''}
            onChange={(e) =>
              setFilters((f) => ({
                ...f,
                category_id: e.target.value ? Number(e.target.value) : undefined,
                skip: 0,
              }))
            }
            className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30"
          >
            <option value="">Todas as categorias</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <select
            value={`${filters.order_by ?? 'created_at'}_${filters.order_direction ?? 'desc'}`}
            onChange={(e) => {
              const [ob, od] = e.target.value.split('_');
              setFilters((f) => ({ ...f, order_by: ob as any, order_direction: od as any }));
            }}
            className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30"
          >
            <option value="created_at_desc">Mais recentes</option>
            <option value="created_at_asc">Mais antigos</option>
            <option value="preco_asc">Menor preço</option>
            <option value="preco_desc">Maior preço</option>
            <option value="nome_asc">Nome A-Z</option>
            <option value="nome_desc">Nome Z-A</option>
          </select>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-zinc-500">Status:</span>
          {[
            { label: 'Todos', value: undefined },
            { label: 'Ativos', value: true },
            { label: 'Inativos', value: false },
          ].map(({ label, value }) => (
            <button
              key={label}
              onClick={() => setFilters((f) => ({ ...f, is_active: value, skip: 0 }))}
              className={`text-xs px-3 py-1 rounded-full transition-colors ${
                filters.is_active === value
                  ? 'bg-violet-600 text-white'
                  : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
              }`}
            >
              {label}
            </button>
          ))}
          {(filters.search || filters.category_id || filters.is_active !== undefined) && (
            <button
              onClick={() => {
                setSearchValue('');
                setFilters({ limit: 20 });
              }}
              className="text-xs text-red-400 hover:text-red-300 ml-auto"
            >
              Limpar filtros ✕
            </button>
          )}
        </div>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-8 text-center">
          <p className="text-red-400">{error}</p>
          <Button variant="outline" onClick={refetch} className="mt-4">Tentar novamente</Button>
        </div>
      ) : products.length === 0 ? (
        <EmptyState
          icon="📦"
          title="Nenhum produto encontrado"
          description="Tente ajustar os filtros ou cadastre um novo produto."
          action={
            <Button onClick={() => setShowForm(true)}>✨ Criar primeiro produto</Button>
          }
        />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {products.map((p) => (
              <ProductCard
                key={p.id}
                product={p}
                onEdit={(prod) => { setEditingProduct(prod); setShowForm(true); }}
                onDelete={setConfirmDelete}
                onToggleActive={handleToggle}
              />
            ))}
          </div>

          {/* Pagination */}
          {data && data.pages > 1 && (
            <div className="flex items-center justify-center gap-3 pt-4">
              <Button
                variant="secondary"
                size="sm"
                disabled={(filters.skip ?? 0) === 0}
                onClick={() => setFilters((f) => ({ ...f, skip: Math.max(0, (f.skip ?? 0) - (f.limit ?? 20)) }))}
              >
                ← Anterior
              </Button>
              <span className="text-sm text-zinc-400">
                Página {data.page} de {data.pages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={data.page >= data.pages}
                onClick={() => setFilters((f) => ({ ...f, skip: (f.skip ?? 0) + (f.limit ?? 20) }))}
              >
                Próxima →
              </Button>
            </div>
          )}
        </>
      )}

      {/* Form Modal */}
      {showForm && (
        <ProductForm
          product={editingProduct}
          onSuccess={handleFormSuccess}
          onCancel={() => { setShowForm(false); setEditingProduct(null); }}
        />
      )}

      {/* Confirm Delete Modal */}
      {confirmDelete && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-zinc-950 border border-zinc-800 rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl">
            <div className="text-center space-y-2">
              <span className="text-4xl">🗑️</span>
              <h3 className="text-lg font-bold text-white">Deletar produto?</h3>
              <p className="text-sm text-zinc-400">
                Tem certeza que deseja deletar{' '}
                <span className="text-zinc-200 font-medium">{confirmDelete.nome}</span>?
                Esta ação não pode ser desfeita.
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                className="flex-1"
                onClick={() => setConfirmDelete(null)}
              >
                Cancelar
              </Button>
              <Button
                variant="danger"
                className="flex-1"
                onClick={() => handleDelete(confirmDelete)}
              >
                Deletar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
