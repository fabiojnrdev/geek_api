from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class User(SQLModel, table = True):
    '''Modelo de usuário adminstrador. Gerencia autenticação e autorização ao acesso do painel admin'''
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True, min_length=5, max_length=100)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
# Classe de categoria
class Category(SQLModel, table=True):
    """Modelo de categoria dos produtos
    Ex: Animes, Games, Mangás, etc.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index= True, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=255)
    slug: str = Field(unique=True, index=True, min_length=1, max_length=120)
    products: List["Produto"] = Relationship(back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"

class Produto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(unique=True, index=True, min_length=1, max_length=120)
    descricao: str = Field(max_length=2000)
    preco: float = Field(
        default=0,
        max_digits=10,
        decimal_places=2,
        ge=0
    )
    quantidade_estoque: int = Field(default=0, ge=0, alias="quantidade_estoque")
    image_url: str = Field(default=None, max_length=500)
    categoria_id: Optional[int] = Field(default=None, foreign_key="category.id")
    categoria: Optional[Category] = Relationship(back_populates="products")
    franquia: str = Field(default=None, max_length=120, index=True)

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"<Produto(id={self.id}, nome='{self.nome}', preco={self.preco}, quantidade_estoque={self.quantidade_estoque})>"
    
#Schemas

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

# Schemas de categoria

class CategoryCreate(SQLModel):
    "Schema para criação de categoria"
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=255)
class CategoryUpdate(SQLModel):
    "Schema para atualização de categoria"
    name: Optional[str] = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=255)
class CategoryResponse(SQLModel):
    """Schema de resposta de categoria"""
    id: int
    name: str
    description: Optional[str]
    slug: str

# Schemas de produto

class ProdutoCreate(SQLModel):
    """Schema para criação de produto"""
    nome: str = Field(min_length=1, max_length=120)
    descricao: str = Field(max_length=2000)
    preco: float = Field(
        default=0,
        max_digits=10,
        decimal_places=2,
        ge=0
    )
    quantidade_estoque: int = Field(default=0, ge=0, alias="quantidade_estoque")
    image_url: Optional[str] = Field(default=None, max_length=500)
    categoria_id: int
    franquia: Optional[str] = Field(default=None, max_length=120)

class ProdutoUpdate(SQLModel):
    """Schema para atualização de produto"""
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
    category: Optional[CategoryResponse]
    is_active: bool
    created_at: datetime
    updated_at: datetime