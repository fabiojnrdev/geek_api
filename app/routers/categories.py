from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List
from app.database import get_session
from app.models import Category, CategoryCreate, CategoryUpdate, CategoryResponse
from app.auth import get_current_active_user
from app.models import User
from app.dependencies import (
    get_category_or_404,
    validate_unique_category_name,
    validate_unique_category_slug,
    generate_slug,
    PaginationParams,
    paginated_response
)
router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session)
):
    """ Lista categorias com suporte a paginação.
     **Query Parameters:**
    - skip: Número de registros a pular (default: 0)
    - limit: Limite de registros por página (default: 100, max: 100)
    
    **Retorna:**
    - Lista paginada de categorias
    
    **Exemplo:**
```
    GET /api/categories?skip=0&limit=10
```
    """
    statement = select(Category).order_by(Category.name).offset(pagination.skip).limit(pagination.limit)
    total_statement = select(func.count()).select_from(Category.id)
    total = session.exec(total_statement).scalar()
    categories = session.exec(
        statement.offset(pagination.skip).limit(pagination.limit)
    ).all()
    return paginated_response(
        items=categories,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )
@router.get("/all", response_model=List[CategoryResponse])
def list_all_categories(session: Session = Depends(get_session)):
    """
    Lista TODAS as categorias sem paginação.
    
    **Útil para:**
    - Selects/dropdowns no frontend
    - Filtros de produtos
    
    **Retorna:**
    - Lista completa de categorias ordenadas por nome
    """
    statement = select(Category).order_by(Category.name)
    categories = session.exec(statement).all()
    return categories
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category: Category = Depends(get_category_or_404)):

    """
    Busca uma categoria por ID.
    
    **Path Parameters:**
    - category_id: ID da categoria
    
    **Retorna:**
    - Dados da categoria
    
    **Erros:**
    - 404: Categoria não encontrada
    
    **Exemplo:**
```
    GET /api/categories/1
```
    """
    return category
@router.get("/slug/{slug}", response_model=CategoryResponse)
def get_category_by_slug(slug: str, session: Session = Depends(get_session)):
    """
    Busca uma categoria por slug.
    
    **Path Parameters:**
    - slug: Slug da categoria (ex: "animes", "games")
    
    **Retorna:**
    - Dados da categoria
    
    **Erros:**
    - 404: Categoria não encontrada
    
    **Exemplo:**
```
    GET /api/categories/slug/animes
```
    """
    statement = select(Category).where(Category.slug == slug)
    category = session.exec(statement).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return category

# Endpoints do admin