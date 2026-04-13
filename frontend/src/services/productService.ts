// src/services/productService.ts
import { api } from './api';
import type {
  Product,
  ProductCreate,
  ProductUpdate,
  ProductFilters,
  PaginatedResponse,
  ProductStats,
  CategoryStats,
} from '../types';

export const productService = {
  async list(filters: ProductFilters = {}): Promise<PaginatedResponse<Product>> {
    const res = await api.get<PaginatedResponse<Product>>('/products', { params: filters });
    return res.data;
  },

  async search(q: string, limit = 10): Promise<Product[]> {
    const res = await api.get<Product[]>('/products/search', { params: { q, limit } });
    return res.data;
  },

  async get(id: number): Promise<Product> {
    const res = await api.get<Product>(`/products/${id}`);
    return res.data;
  },

  async getByFranquia(franquia: string, limit = 20): Promise<Product[]> {
    const res = await api.get<Product[]>(`/products/franquia/${franquia}`, { params: { limit } });
    return res.data;
  },

  async create(data: ProductCreate): Promise<Product> {
    const res = await api.post<Product>('/products', data);
    return res.data;
  },

  async update(id: number, data: ProductUpdate): Promise<Product> {
    const res = await api.put<Product>(`/products/${id}`, data);
    return res.data;
  },

  async updateStock(id: number, quantidade: number, operation: 'set' | 'add' | 'subtract' = 'set'): Promise<Product> {
    const res = await api.patch<Product>(`/products/${id}/stock`, null, {
      params: { quantidade, operation },
    });
    return res.data;
  },

  async toggleActive(id: number): Promise<Product> {
    const res = await api.patch<Product>(`/products/${id}/toggle-active`);
    return res.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/products/${id}`);
  },

  async stats(): Promise<ProductStats> {
    const res = await api.get<ProductStats>('/products/stats/overview');
    return res.data;
  },

  async statsByCategory(): Promise<CategoryStats[]> {
    const res = await api.get<CategoryStats[]>('/products/stats/by-category');
    return res.data;
  },
};