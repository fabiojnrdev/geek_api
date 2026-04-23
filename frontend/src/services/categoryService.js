import { api } from './api';

export const categoryService = {
  async list(skip = 0, limit = 100) {
    const res = await api.get('/categories', { params: { skip, limit } });
    return res.data;
  },

  async listAll() {
    const res = await api.get('/categories/all');
    return res.data;
  },

  async get(id) {
    const res = await api.get(`/categories/${id}`);
    return res.data;
  },

  async getBySlug(slug) {
    const res = await api.get(`/categories/slug/${slug}`);
    return res.data;
  },

  async create(data) {
    const res = await api.post('/categories', data);
    return res.data;
  },

  async update(id, data) {
    const res = await api.put(`/categories/${id}`, data);
    return res.data;
  },

  async delete(id) {
    await api.delete(`/categories/${id}`);
  },

  async productsCount(id) {
    const res = await api.get(`/categories/${id}/products_count`);
    return res.data;
  },
};
