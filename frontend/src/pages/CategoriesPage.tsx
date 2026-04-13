import React, { useState } from 'react';
import { useCategories } from '../hooks/useCategories';
import { categoryService } from '../services/categoryService';
import { Button, Input, Card, Spinner, EmptyState } from '../components/ui';
import type { Category } from '../types';

interface CategoryFormData {
  name: string;
  description: string;
}

export const CategoriesPage: React.FC = () => {
  const { categories, isLoading, error, refetch } = useCategories();
  const [showForm, setShowForm] = useState(false);
  const [editingCat, setEditingCat] = useState<Category | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Category | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [form, setForm] = useState<CategoryFormData>({ name: '', description: '' });

  const openCreate = () => {
    setEditingCat(null);
    setForm({ name: '', description: '' });
    setFormError(null);
    setShowForm(true);
  };

  const openEdit = (cat: Category) => {
    setEditingCat(cat);
    setForm({ name: cat.name, description: cat.description ?? '' });
    setFormError(null);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    setFormError(null);
    try {
      if (editingCat) {
        await categoryService.update(editingCat.id, {
          name: form.name,
          description: form.description || undefined,
        });
      } else {
        await categoryService.create({
          name: form.name,
          description: form.description || undefined,
        });
      }
      setShowForm(false);
      refetch();
    } catch (err: any) {
      setFormError(err.response?.data?.detail ?? 'Erro ao salvar categoria');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (cat: Category) => {
    try {
      await categoryService.delete(cat.id);
      refetch();
    } catch (err: any) {
      alert(err.response?.data?.detail ?? 'Erro ao deletar categoria');
    } finally {
      setConfirmDelete(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Categorias</h1>
          <p className="text-zinc-500 text-sm mt-0.5">
            {categories.length} categoria{categories.length !== 1 ? 's' : ''} cadastrada{categories.length !== 1 ? 's' : ''}
          </p>
        </div>
        <Button onClick={openCreate} leftIcon={<span>✨</span>}>
          Nova Categoria
        </Button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 text-center">
          <p className="text-red-400">{error}</p>
        </div>
      ) : categories.length === 0 ? (
        <EmptyState
          icon="🗂️"
          title="Nenhuma categoria"
          description="Crie categorias para organizar seus produtos."
          action={<Button onClick={openCreate}>✨ Criar categoria</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((cat) => (
            <Card key={cat.id} className="p-5 space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-violet-600/15 flex items-center justify-center text-xl">
                    🗂️
                  </div>
                  <div>
                    <h3 className="font-semibold text-zinc-100">{cat.name}</h3>
                    <span className="text-xs text-zinc-500 font-mono">/{cat.slug}</span>
                  </div>
                </div>
              </div>

              {cat.description && (
                <p className="text-sm text-zinc-500 leading-relaxed line-clamp-2">
                  {cat.description}
                </p>
              )}

              <div className="flex gap-2 pt-1 border-t border-zinc-800">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => openEdit(cat)}
                  className="flex-1"
                >
                  ✏️ Editar
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setConfirmDelete(cat)}
                  className="hover:text-red-400 hover:bg-red-500/10"
                  title="Deletar"
                >
                  🗑️
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-zinc-950 border border-zinc-800 rounded-2xl w-full max-w-md shadow-2xl">
            <div className="p-6 border-b border-zinc-800 flex items-center justify-between">
              <h2 className="text-lg font-bold text-white">
                {editingCat ? 'Editar Categoria' : 'Nova Categoria'}
              </h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-zinc-500 hover:text-white w-8 h-8 rounded-lg hover:bg-zinc-800 flex items-center justify-center"
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {formError && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">
                  {formError}
                </div>
              )}
              <Input
                label="Nome *"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                required
                minLength={2}
                maxLength={100}
                placeholder="Ex: Animes"
              />
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-zinc-300">Descrição</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                  rows={3}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30 transition-colors resize-none"
                  placeholder="Descrição opcional da categoria..."
                  maxLength={500}
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowForm(false)}
                  className="flex-1"
                  disabled={formLoading}
                >
                  Cancelar
                </Button>
                <Button type="submit" isLoading={formLoading} className="flex-1">
                  {editingCat ? '💾 Salvar' : '✨ Criar'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirm Delete Modal */}
      {confirmDelete && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-zinc-950 border border-zinc-800 rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl">
            <div className="text-center space-y-2">
              <span className="text-4xl">⚠️</span>
              <h3 className="text-lg font-bold text-white">Deletar categoria?</h3>
              <p className="text-sm text-zinc-400">
                Deletar <span className="text-zinc-200 font-medium">{confirmDelete.name}</span>?
                Só é possível se não houver produtos associados.
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary" className="flex-1" onClick={() => setConfirmDelete(null)}>
                Cancelar
              </Button>
              <Button variant="danger" className="flex-1" onClick={() => handleDelete(confirmDelete)}>
                Deletar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};