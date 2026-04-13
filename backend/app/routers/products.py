# app/routers/products.py
# FIX BUG-B2: Rotas estáticas (/search, /franquia/{x}, /stats/*) movidas para
# ANTES de /{product_id}. FastAPI resolve por ordem de declaração — se
# /{product_id} vier primeiro, ele engole "/stats/overview" como product_id="stats"
# resultando em erro 422 (ValidationError: int expected).

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func, or_
from typing import List
from datetime import datetime, timezone

from app.database import get_session
from app.models import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    Category,
    User,
)
from app.auth import get_current_active_user
from app.dependencies import (
    get_product_or_404,
    validate_category_exists,
    PaginationParams,
    ProductFilterParams,
    paginated_response,
)

router = APIRouter(prefix="/products", tags=["Produtos"])


# ── Rotas públicas estáticas (devem vir antes de /{product_id}) ────────────

@router.get("/", response_model=dict)
def list_products(
    pagination: PaginationParams = Depends(),
    filters: ProductFilterParams = Depends(),
    session: Session = Depends(get_session),
):
    """Lista produtos com filtros avançados e paginação."""
    statement = select(Product).join(Category, isouter=True)

    if filters.search:
        term = f"%{filters.search}%"
        statement = statement.where(
            or_(
                Product.nome.ilike(term),
                Product.descricao.ilike(term),
                Product.franquia.ilike(term),
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
        statement = statement.where(Product.is_active == True)

    order_col = {
        "nome": Product.nome,
        "preco": Product.preco,
    }.get(filters.order_by, Product.created_at)

    statement = statement.order_by(
        order_col.asc() if filters.order_direction == "asc" else order_col.desc()
    )

    total = session.exec(select(func.count()).select_from(statement.subquery())).one()
    products = session.exec(statement.offset(pagination.skip).limit(pagination.limit)).all()

    return paginated_response(items=products, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session),
):
    """Busca rápida de produtos (autocomplete)."""
    term = f"%{q}%"
    statement = select(Product).where(
        Product.is_active == True,
        or_(
            Product.nome.ilike(term),
            Product.descricao.ilike(term),
            Product.franquia.ilike(term),
        ),
    ).limit(limit)
    return session.exec(statement).all()


@router.get("/franquia/{franquia}", response_model=List[ProductResponse])
def get_products_by_franquia(
    franquia: str,
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Lista produtos de uma franquia específica."""
    statement = select(Product).where(
        Product.franquia.ilike(f"%{franquia}%"),
        Product.is_active == True,
    ).limit(limit)
    return session.exec(statement).all()


# ── Endpoints de estatísticas (Admin) — estáticos, antes de /{product_id} ──

@router.get("/stats/overview")
def get_products_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Estatísticas gerais dos produtos. Requer autenticação."""
    total = session.exec(select(func.count(Product.id))).one()
    active = session.exec(select(func.count(Product.id)).where(Product.is_active == True)).one()
    out_of_stock = session.exec(
        select(func.count(Product.id)).where(Product.quantidade_estoque == 0)
    ).one()
    low_stock = session.exec(
        select(func.count(Product.id)).where(
            Product.quantidade_estoque > 0, Product.quantidade_estoque < 10
        )
    ).one()
    inventory_value = session.exec(
        select(func.sum(Product.preco * Product.quantidade_estoque))
    ).one() or 0

    return {
        "total_products": total,
        "active_products": active,
        "inactive_products": total - active,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "total_inventory_value": float(inventory_value),
    }


@router.get("/stats/by-category")
def get_products_by_category_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Estatísticas de produtos agrupadas por categoria. Requer autenticação."""
    statement = select(
        Product.category_id,
        Category.name.label("category_name"),
        func.count(Product.id).label("product_count"),
        func.sum(Product.preco * Product.quantidade_estoque).label("total_value"),
    ).join(Category).group_by(Product.category_id, Category.name)

    results = session.exec(statement).all()
    return [
        {
            "category_id": r.category_id,
            "category_name": r.category_name,
            "product_count": r.product_count,
            "total_value": float(r.total_value or 0),
        }
        for r in results
    ]


# ── Rota dinâmica (DEVE vir depois de todas as rotas estáticas) ────────────

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product: Product = Depends(get_product_or_404)):
    """Busca um produto por ID."""
    return product


# ── Endpoints protegidos (Admin) ───────────────────────────────────────────

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Cria um novo produto. Requer autenticação."""
    validate_category_exists(product_data.category_id, session)

    new_product = Product(
        nome=product_data.nome,
        descricao=product_data.descricao,
        preco=product_data.preco,
        quantidade_estoque=product_data.quantidade_estoque,
        image_url=product_data.image_url,
        category_id=product_data.category_id,
        franquia=product_data.franquia,
    )
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_data: ProductUpdate,
    product: Product = Depends(get_product_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza um produto existente. Requer autenticação."""
    update_data = product_data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        validate_category_exists(update_data["category_id"], session)

    for key, value in update_data.items():
        setattr(product, key, value)

    product.updated_at = datetime.now(timezone.utc)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    product_id: int,
    quantidade: int = Query(..., description="Quantidade"),
    operation: str = Query("set", regex="^(set|add|subtract)$"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza o estoque de um produto. Requer autenticação."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produto {product_id} não encontrado")

    new_stock = {
        "set": quantidade,
        "add": product.quantidade_estoque + quantidade,
        "subtract": product.quantidade_estoque - quantidade,
    }[operation]

    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Operação resultaria em estoque negativo ({new_stock})",
        )

    product.quantidade_estoque = new_stock
    product.updated_at = datetime.now(timezone.utc)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.patch("/{product_id}/toggle-active", response_model=ProductResponse)
def toggle_product_active(
    product: Product = Depends(get_product_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Ativa/Desativa um produto (soft delete). Requer autenticação."""
    product.is_active = not product.is_active
    product.updated_at = datetime.now(timezone.utc)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product: Product = Depends(get_product_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Deleta permanentemente um produto. Requer autenticação."""
    session.delete(product)
    session.commit()