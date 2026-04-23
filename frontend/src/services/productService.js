import { api } from './api';

export const productService = {
  async list(filters = {}) {
    const res = await api.get('/products', { params: filters });
    return res.data;
  },

  async search(q, limit = 10) {
    const res = await api.get('/products/search', { params: { q, limit } });
    return res.data;
  },

  async get(id) {
    const res = await api.get(`/products/${id}`);
    return res.data;
  },

  async getByFranquia(franquia, limit = 20) {
    const res = await api.get(`/products/franquia/${franquia}`, { params: { limit } });
    return res.data;
  },

  async create(data) {
    const res = await api.post('/products', data);
    return res.data;
  },

  async update(id, data) {
    const res = await api.put(`/products/${id}`, data);
    return res.data;
  },

  async updateStock(id, quantidade, operation = 'set') {
    const res = await api.patch(`/products/${id}/stock`, null, {
      params: { quantidade, operation },
    });
    return res.data;
  },

  async toggleActive(id) {
    const res = await api.patch(`/products/${id}/toggle-active`);
    return res.data;
  },

  async delete(id) {
    await api.delete(`/products/${id}`);
  },

  async stats() {
    const res = await api.get('/products/stats/overview');
    return res.data;
  },

  async statsByCategory() {
    const res = await api.get('/products/stats/by-category');
    return res.data;
  },
};
