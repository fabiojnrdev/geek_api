// src/components/products/ProductCard.tsx
// FIX BUG-F1: Caminhos de import corrigidos para a estrutura de pastas atual

import React from 'react';
import { Badge, Button } from '../ui';
import type { Product } from '../../types';

interface ProductCardProps {
  product: Product;
  onEdit?: (p: Product) => void;
  onDelete?: (p: Product) => void;
  onToggleActive?: (p: Product) => void;
}

function stockColor(qty: number): 'red' | 'yellow' | 'green' {
  if (qty === 0) return 'red';
  if (qty < 10) return 'yellow';
  return 'green';
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onEdit,
  onDelete,
  onToggleActive,
}) => {
  const price = typeof product.preco === 'string'
    ? parseFloat(product.preco)
    : product.preco;

  return (
    <div
      className={`
        bg-zinc-900 border rounded-2xl overflow-hidden transition-all duration-200
        hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-900/20 group
        ${product.is_active ? 'border-zinc-800' : 'border-zinc-800/40 opacity-60'}
      `}
    >
      {/* Image */}
      <div className="relative h-44 bg-zinc-800 overflow-hidden">
        <img
          src={product.image_url}
          alt={product.nome}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          onError={(e) => {
            (e.target as HTMLImageElement).src =
              'https://via.placeholder.com/400x300/18181b/6d28d9?text=Geek+Store';
          }}
          loading="lazy"
        />

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-zinc-900/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {!product.is_active && (
          <div className="absolute inset-0 bg-zinc-950/70 flex items-center justify-center">
            <Badge color="zinc">Inativo</Badge>
          </div>
        )}

        <div className="absolute top-2 right-2">
          <Badge color={stockColor(product.quantidade_estoque)}>
            {product.quantidade_estoque === 0
              ? 'Sem estoque'
              : `${product.quantidade_estoque} un.`}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <p className="text-xs text-violet-400 font-semibold mb-0.5 uppercase tracking-wider">
            {product.franquia}
          </p>
          <h3 className="text-sm font-semibold text-zinc-100 line-clamp-2 leading-snug">
            {product.nome}
          </h3>
          {product.category && (
            <Badge color="blue" className="mt-1.5">
              {product.category.name}
            </Badge>
          )}
        </div>

        <p className="text-xs text-zinc-500 line-clamp-2 leading-relaxed">
          {product.descricao}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xl font-bold text-violet-400">
            R${' '}
            {price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </span>
        </div>

        {/* Actions */}
        {(onEdit || onDelete || onToggleActive) && (
          <div className="flex gap-2 pt-2 border-t border-zinc-800">
            {onEdit && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onEdit(product)}
                className="flex-1"
              >
                ✏️ Editar
              </Button>
            )}
            {onToggleActive && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onToggleActive(product)}
                title={product.is_active ? 'Desativar' : 'Ativar'}
              >
                {product.is_active ? '🔴' : '🟢'}
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(product)}
                title="Deletar"
                className="hover:text-red-400 hover:bg-red-500/10"
              >
                🗑️
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
