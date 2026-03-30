# app/dependencies.py

from typing import Optional
from fastapi import Depends, HTTPException, status, Query, Path
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_active_user
from app.models import User, Category, Product


# ============================================================================
# DATABASE DEPENDENCIES
# ============================================================================

def get_db() -> Session:
    """
    Alias para get_session (mais intuitivo).
    """
    return Depends(get_session)


# ============================================================================
# AUTH DEPENDENCIES
# ============================================================================

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency que garante que apenas admins autenticados acessem a rota.
    """
    return current_user


# ============================================================================
# QUERY PARAMETERS DEPENDENCIES
# ============================================================================

class PaginationParams:
    """
    Dependency para paginação de resultados.
    """
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Número de registros a pular"),
        limit: int = Query(100, ge=1, le=100, description="Limite de registros por página")
    ):
        self.skip = skip
        self.limit = limit


class ProductFilterParams:
    """
    Dependency para filtros de produtos.
    """
    def __init__(
        self,
        search: Optional[str] = Query(None, min_length=1, max_length=100, description="Buscar por nome ou descrição"),
        category_id: Optional[int] = Query(None, ge=1, description="Filtrar por ID da categoria"),
        franquia: Optional[str] = Query(None, min_length=1, max_length=100, description="Filtrar por franquia"),
        min_preco: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
        max_preco: Optional[float] = Query(None, ge=0, description="Preço máximo"),
        is_active: Optional[bool] = Query(None, description="Filtrar produtos ativos/inativos"),
        order_by: Optional[str] = Query("created_at", description="Ordenar por: nome, preco, created_at"),
        order_direction: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Direção: asc ou desc")
    ):
        self.search = search
        self.category_id = category_id
        self.franquia = franquia
        self.min_preco = min_preco
        self.max_preco = max_preco
        self.is_active = is_active
        self.order_by = order_by
        self.order_direction = order_direction


# ============================================================================
# ENTITY GETTERS (com validação) - CORRIGIDO
# ============================================================================

def get_category_or_404(
    category_id: int = Path(..., description="ID da categoria"),  # ✅ CORREÇÃO
    session: Session = Depends(get_session)
) -> Category:
    """
    Busca uma categoria por ID ou retorna 404.
    """
    statement = select(Category).where(Category.id == category_id)
    category = session.exec(statement).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {category_id} não encontrada"
        )
    
    return category


def get_product_or_404(
    product_id: int = Path(..., description="ID do produto"),  # ✅ CORREÇÃO
    session: Session = Depends(get_session)
) -> Product:
    """
    Busca um produto por ID ou retorna 404.
    """
    statement = select(Product).where(Product.id == product_id)
    product = session.exec(statement).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {product_id} não encontrado"
        )
    
    return product


def get_user_or_404(
    user_id: int = Path(..., description="ID do usuário"),  # ✅ CORREÇÃO
    session: Session = Depends(get_session)
) -> User:
    """
    Busca um usuário por ID ou retorna 404.
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {user_id} não encontrado"
        )
    
    return user


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_category_exists(
    category_id: int,
    session: Session
) -> None:
    """
    Valida se uma categoria existe (para uso em outros endpoints).
    """
    statement = select(Category).where(Category.id == category_id)
    category = session.exec(statement).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria com ID {category_id} não existe"
        )


def validate_unique_category_name(
    name: str,
    session: Session,
    exclude_id: Optional[int] = None
) -> None:
    """
    Valida se o nome da categoria é único.
    """
    statement = select(Category).where(Category.name == name)
    
    if exclude_id:
        statement = statement.where(Category.id != exclude_id)
    
    existing = session.exec(statement).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma categoria com o nome '{name}'"
        )


def validate_unique_category_slug(
    slug: str,
    session: Session,
    exclude_id: Optional[int] = None
) -> None:
    """
    Valida se o slug da categoria é único.
    """
    statement = select(Category).where(Category.slug == slug)
    
    if exclude_id:
        statement = statement.where(Category.id != exclude_id)
    
    existing = session.exec(statement).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma categoria com o slug '{slug}'"
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_slug(text: str) -> str:
    """
    Gera um slug URL-friendly a partir de um texto.
    """
    import unicodedata
    import re
    
    # Remove acentos
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Lowercase e substitui espaços por hífens
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remove hífens duplicados e nas pontas
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    
    return text


def format_price(price: float) -> str:
    """
    Formata um preço para exibição em Real brasileiro.
    """
    return f"R$ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================================================
# RESPONSE HELPERS
# ============================================================================

def paginated_response(items: list, total: int, skip: int, limit: int) -> dict:
    """
    Cria uma resposta paginada padronizada.
    """
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
        "per_page": limit
    }