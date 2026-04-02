import { useState, useEffect, useCallback } from 'react';
import { productService } from '../services/productService';
import type { Product, ProductFilters, PaginatedResponse, ProductStats, CategoryStats } from '../types';

export function useProducts(initialFilters: ProductFilters = {}) {
  const [data, setData] = useState<PaginatedResponse<Product> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ProductFilters>(initialFilters);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await productService.list(filters);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Erro ao carregar produtos');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => { fetch(); }, [fetch]);

  return { data, isLoading, error, filters, setFilters, refetch: fetch };
}

export function useProduct(id: number) {
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    productService.get(id)
      .then(setProduct)
      .catch((err) => setError(err.response?.data?.detail ?? 'Produto não encontrado'))
      .finally(() => setIsLoading(false));
  }, [id]);

  return { product, isLoading, error };
}

export function useProductStats() {
  const [stats, setStats] = useState<ProductStats | null>(null);
  const [categoryStats, setCategoryStats] = useState<CategoryStats[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([productService.stats(), productService.statsByCategory()])
      .then(([s, cs]) => { setStats(s); setCategoryStats(cs); })
      .finally(() => setIsLoading(false));
  }, []);

  return { stats, categoryStats, isLoading };
}

// src/hooks/useCategories.ts (inline export)
import { categoryService } from '../services/categoryService';
import type { Category } from '../types';

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await categoryService.listAll();
      setCategories(result);
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Erro ao carregar categorias');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  return { categories, isLoading, error, refetch: fetch };
}