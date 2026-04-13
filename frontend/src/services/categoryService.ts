import { api } from './api';
import type { Category, CategoryCreate, CategoryUpdate, PaginatedResponse } from '../types';

export const categoryService = {
  async list(skip = 0, limit = 100): Promise<PaginatedResponse<Category>> {
    const res = await api.get<PaginatedResponse<Category>>('/categories', { params: { skip, limit } });
    return res.data;
  },

  async listAll(): Promise<Category[]> {
    const res = await api.get<Category[]>('/categories/all');
    return res.data;
  },

  async get(id: number): Promise<Category> {
    const res = await api.get<Category>(`/categories/${id}`);
    return res.data;
  },

  async getBySlug(slug: string): Promise<Category> {
    const res = await api.get<Category>(`/categories/slug/${slug}`);
    return res.data;
  },

  async create(data: CategoryCreate): Promise<Category> {
    const res = await api.post<Category>('/categories', data);
    return res.data;
  },

  async update(id: number, data: CategoryUpdate): Promise<Category> {
    const res = await api.put<Category>(`/categories/${id}`, data);
    return res.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/categories/${id}`);
  },

  async productsCount(id: number): Promise<{ category_id: number; category_name: string; products_count: number }> {
    const res = await api.get(`/categories/${id}/products_count`);
    return res.data;
  },
};