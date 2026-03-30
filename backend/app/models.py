# app/models.py

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from decimal import Decimal


# ============================================================================
# USER MODEL (Admin)
# ============================================================================

class User(SQLModel, table=True):
    """
    Modelo de usuário administrador.
    Gerencia autenticação e acesso ao painel admin.
    """
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"


# ============================================================================
# CATEGORY MODEL
# ============================================================================

class Category(SQLModel, table=True):
    """
    Modelo de categorias de produtos.
    Ex: Animes, Games, Mangás, Action Figures
    """
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    slug: str = Field(unique=True, index=True, max_length=100)
    
    # Relacionamento: uma categoria tem vários produtos
    products: list["Product"] = Relationship(back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"


# ============================================================================
# PRODUCT MODEL
# ============================================================================

class Product(SQLModel, table=True):
    """
    Modelo de produtos da loja geek.
    """
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(min_length=2, max_length=200, index=True)
    descricao: str = Field(max_length=2000)
    preco: Decimal = Field(
        default=0,
        max_digits=10,
        decimal_places=2,
        ge=0
    )
    quantidade_estoque: int = Field(default=0, ge=0)
    image_url: str = Field(max_length=500)
    
    # Relacionamento com Category
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    category: Optional[Category] = Relationship(back_populates="products")
    
    franquia: str = Field(max_length=100, index=True)
    
    # Campos de controle
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product {self.nome} - R$ {self.preco}>"


# ============================================================================
# SCHEMAS (Request/Response models)
# ============================================================================

# --- USER SCHEMAS ---

class UserCreate(SQLModel):
    """Schema para criação de usuário (register)"""
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=100)


class UserLogin(SQLModel):
    """Schema para login"""
    username: str
    password: str


class UserResponse(SQLModel):
    """Schema de resposta (sem senha)"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime


class Token(SQLModel):
    """Schema de resposta de autenticação"""
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    """Dados extraídos do token JWT"""
    username: Optional[str] = None


# --- CATEGORY SCHEMAS ---

class CategoryCreate(SQLModel):
    """Schema para criar categoria"""
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class CategoryUpdate(SQLModel):
    """Schema para atualizar categoria"""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None


class CategoryResponse(SQLModel):
    """Schema de resposta de categoria"""
    id: int
    name: str
    description: Optional[str]
    slug: str


# --- PRODUCT SCHEMAS ---

class ProductCreate(SQLModel):
    """Schema para criar produto"""
    nome: str = Field(min_length=2, max_length=200)
    descricao: str = Field(max_length=2000)
    preco: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantidade_estoque: int = Field(ge=0)
    image_url: str = Field(max_length=500)
    category_id: int
    franquia: str = Field(max_length=100)


class ProductUpdate(SQLModel):
    """Schema para atualizar produto (todos campos opcionais)"""
    nome: Optional[str] = Field(default=None, min_length=2, max_length=200)
    descricao: Optional[str] = Field(default=None, max_length=2000)
    preco: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    quantidade_estoque: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
    category_id: Optional[int] = None
    franquia: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None


class ProductResponse(SQLModel):
    """Schema de resposta de produto com categoria"""
    id: int
    nome: str
    descricao: str
    preco: Decimal
    quantidade_estoque: int
    image_url: str
    franquia: str
    category: Optional[CategoryResponse] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime