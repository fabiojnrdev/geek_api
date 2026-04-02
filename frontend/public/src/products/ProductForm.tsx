// src/components/products/ProductForm.tsx
import React, { useEffect, useState } from 'react';
import { Button, Input } from '../ui';
import { categoryService } from '../../services/categoryService';
import { productService } from '../../services/productService';
import type { Product, ProductCreate, ProductUpdate, Category } from '../../types';

interface ProductFormProps {
  product?: Product | null;
  onSuccess: () => void;
  onCancel: () => void;
}

export const ProductForm: React.FC<ProductFormProps> = ({ product, onSuccess, onCancel }) => {
  const isEditing = !!product;
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    nome: product?.nome ?? '',
    descricao: product?.descricao ?? '',
    preco: product?.preco?.toString() ?? '',
    quantidade_estoque: product?.quantidade_estoque?.toString() ?? '0',
    image_url: product?.image_url ?? '',
    category_id: product?.category?.id?.toString() ?? '',
    franquia: product?.franquia ?? '',
  });

  useEffect(() => {
    categoryService.listAll().then(setCategories);
  }, []);

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const payload = {
        nome: form.nome,
        descricao: form.descricao,
        preco: parseFloat(form.preco),
        quantidade_estoque: parseInt(form.quantidade_estoque),
        image_url: form.image_url,
        category_id: parseInt(form.category_id),
        franquia: form.franquia,
      };
      if (isEditing) {
        await productService.update(product!.id, payload as ProductUpdate);
      } else {
        await productService.create(payload as ProductCreate);
      }
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Erro ao salvar produto');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-950 border border-zinc-800 rounded-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-zinc-950 border-b border-zinc-800 p-6 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">{isEditing ? 'Editar Produto' : 'Novo Produto'}</h2>
          <button onClick={onCancel} className="text-zinc-500 hover:text-white transition-colors text-xl">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">{error}</div>
          )}

          <Input label="Nome *" value={form.nome} onChange={set('nome')} required minLength={2} maxLength={200} />
          
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-300">Descrição *</label>
            <textarea
              value={form.descricao}
              onChange={set('descricao')}
              required
              rows={3}
              className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-violet-500 resize-none"
              placeholder="Descrição do produto..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input label="Preço (R$) *" type="number" step="0.01" min="0.01" value={form.preco} onChange={set('preco')} required />
            <Input label="Estoque *" type="number" min="0" value={form.quantidade_estoque} onChange={set('quantidade_estoque')} required />
          </div>

          <Input label="URL da Imagem *" type="url" value={form.image_url} onChange={set('image_url')} required placeholder="https://..." />

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-zinc-300">Categoria *</label>
              <select
                value={form.category_id}
                onChange={set('category_id')}
                required
                className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
              >
                <option value="">Selecione...</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <Input label="Franquia *" value={form.franquia} onChange={set('franquia')} required placeholder="Ex: Naruto" />
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={onCancel} className="flex-1">Cancelar</Button>
            <Button type="submit" isLoading={isLoading} className="flex-1">
              {isEditing ? 'Salvar Alterações' : 'Criar Produto'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};