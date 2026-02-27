from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func, or_
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.database import get_session
from app.models import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    Category,
    User
)
from app.auth import get_current_active_user
from app.dependencies import (
    get_product_or_404,
    validate_category_exists,
    PaginationParams,
    ProductFilterParams,
    paginated_response
)
router = APIRouter(
    prefix="/products",
    tags=["Produtos"]
)

# Endpoints públicos
@router.get("/", response_model=dict)
def list_products(
    pagination: PaginationParams = Depends(),
    filters: ProductFilterParams = Depends(),
    session: Session = Depends(get_session)
):
     """
    Lista produtos com filtros avançados e paginação.
    
    **Query Parameters:**
    - skip: Número de registros a pular (default: 0)
    - limit: Limite por página (default: 100, max: 100)
    - search: Buscar por nome ou descrição
    - category_id: Filtrar por categoria
    - franquia: Filtrar por franquia (ex: "Naruto", "One Piece")
    - min_preco: Preço mínimo
    - max_preco: Preço máximo
    - is_active: Filtrar ativos/inativos
    - order_by: Ordenar por (nome, preco, created_at)
    - order_direction: Direção (asc, desc)
    
    **Exemplo:**
```
    GET /api/products?search=naruto&category_id=1&min_preco=50&max_preco=200&order_by=preco&order_direction=asc
```
    
    **Retorna:**
    - Lista paginada de produtos com suas categorias
    """
    # Query base com join na categoria
     statement = select(Product).join(Category, isouter=True)
    
    # Aplicar filtros
     if filters.search:
        search_term = f"%{filters.search}%"
        statement = statement.where(
            or_(
                Product.nome.ilike(search_term),
                Product.descricao.ilike(search_term),
                Product.franquia.ilike(search_term)
            )
        )
    
     if filters.category_id:
        statement = statement.where(Product.category_id == filters.category_id)
    
     if filters.franquia:
        statement = statement.where(Product.franquia.ilike(f"%{filters.franquia}%"))
    
     if filters.min_preco is not None:
        statement = statement.where(Product.preco >= filters.min_preco)
    
     if filters.max_preco is not None:
        statement = statement.where(Product.preco <= filters.max_preco)
    
     if filters.is_active is not None:
        statement = statement.where(Product.is_active == filters.is_active)
     else:
        # Por padrão, mostrar apenas produtos ativos para usuários não-autenticados
        statement = statement.where(Product.is_active == True)

     count_statement = select(func.count()).select_from(statement.subquery())
     total = session.exec(count_statement).one()

     products = session.exec(
        statement.offset(pagination.skip).limit(pagination.limit)
     ).all()
     return paginated_response(
        items= products,
        total= total,
        skip= pagination.skip,
        limit= pagination.limit
     )
@router.get("/search", response_model=List[ProductResponse])
def search_products(
   q: str = Query(..., min_length=1, max_length=100, description="Pesquise"),
   limit: int = Query(10, ge = 1, le=50, description="Limite de resultados"),
   session: Session = Depends(get_session)
):
    """
    Busca rápida de produtos (para autocomplete/search bar).
    
    **Query Parameters:**
    - q: Termo de busca (obrigatório)
    - limit: Limite de resultados (default: 10, max: 50)
    
    **Busca em:**
    - Nome do produto
    - Descrição
    - Franquia
    
    **Exemplo:**
```
    GET /api/products/search?q=naruto&limit=5
```
    
    **Retorna:**
    - Lista de produtos encontrados (apenas ativos)
    """
    search_term = f"%{q}%"

    statement = select(Product).where(
       Product.is_active == True,
       or_(
          Product.nome.ilike(search_term),
          Product.descricao.ilike(search_term),
          Product.franquia.ilke(search_term)
       )
    ).limit()
    products = session.exec(statement).all()
    return products
