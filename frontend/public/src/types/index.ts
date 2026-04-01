// Espelha exatamente os schemas do backend (models.py)

// ─── AUTH ────────────────────────────────────────────────────
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// ─── CATEGORY ────────────────────────────────────────────────
export interface Category {
  id: number;
  name: string;
  description: string | null;
  slug: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
}

// ─── PRODUCT ─────────────────────────────────────────────────
export interface Product {
  id: number;
  nome: string;
  descricao: string;
  preco: number;
  quantidade_estoque: number;
  image_url: string;
  franquia: string;
  category: Category | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  nome: string;
  descricao: string;
  preco: number;
  quantidade_estoque: number;
  image_url: string;
  category_id: number;
  franquia: string;
}

export interface ProductUpdate {
  nome?: string;
  descricao?: string;
  preco?: number;
  quantidade_estoque?: number;
  image_url?: string;
  category_id?: number;
  franquia?: string;
  is_active?: boolean;
}

// ─── PAGINATION ──────────────────────────────────────────────
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  per_page: number;
}

// ─── STATS ───────────────────────────────────────────────────
export interface ProductStats {
  total_products: number;
  active_products: number;
  inactive_products: number;
  out_of_stock: number;
  low_stock: number;
  total_inventory_value: number;
}

export interface CategoryStats {
  category_id: number;
  category_name: string;
  product_count: number;
  total_value: number;
}

// ─── FILTERS ─────────────────────────────────────────────────
export interface ProductFilters {
  search?: string;
  category_id?: number;
  franquia?: string;
  min_preco?: number;
  max_preco?: number;
  is_active?: boolean;
  order_by?: 'nome' | 'preco' | 'created_at';
  order_direction?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}