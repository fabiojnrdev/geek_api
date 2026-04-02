# app/routers/categories.py — CORRIGIDO
# Bugs originais corrigidos:
#   1. list_categories: offset aplicado duas vezes (statement já tinha .offset/.limit)
#   2. create_category: argumentos invertidos em validate_unique_category_name/slug
#   3. update_category: argumentos invertidos em validate_unique_category_slug

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
    paginated_response,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/all", response_model=List[CategoryResponse])
def list_all_categories(session: Session = Depends(get_session)):
    """Lista TODAS as categorias sem paginação (para selects/dropdowns)."""
    return session.exec(select(Category).order_by(Category.name)).all()


@router.get("/", response_model=dict)
def list_categories(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
):
    """Lista categorias com paginação."""
    statement = select(Category).order_by(Category.name)
    total = session.exec(select(func.count(Category.id))).one()   # ✅ FIX: era select_from(Category.id)
    categories = session.exec(
        statement.offset(pagination.skip).limit(pagination.limit)  # ✅ FIX: offset aplicado só uma vez
    ).all()
    return paginated_response(items=categories, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/slug/{slug}", response_model=CategoryResponse)
def get_category_by_slug(slug: str, session: Session = Depends(get_session)):
    category = session.exec(select(Category).where(Category.slug == slug)).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return category


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category: Category = Depends(get_category_or_404)):
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    # ✅ FIX: argumentos na ordem correta (name, session)
    validate_unique_category_name(category_in.name, session)
    slug = generate_slug(category_in.name)
    validate_unique_category_slug(slug, session)  # ✅ FIX

    new_category = Category(name=category_in.name, description=category_in.description, slug=slug)
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_data: CategoryUpdate,
    category: Category = Depends(get_category_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    update_data = category_data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != category.name:
        validate_unique_category_name(update_data["name"], session, exclude_id=category.id)  # ✅ FIX
        new_slug = generate_slug(update_data["name"])
        validate_unique_category_slug(new_slug, session, exclude_id=category.id)            # ✅ FIX
        update_data["slug"] = new_slug

    for key, value in update_data.items():
        setattr(category, key, value)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category: Category = Depends(get_category_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    from app.models import Product
    count = session.exec(select(func.count(Product.id)).where(Product.category_id == category.id)).one()
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível deletar: categoria possui {count} produto(s) associado(s).",
        )
    session.delete(category)
    session.commit()


@router.get("/{category_id}/products_count")
def get_category_products_count(
    category: Category = Depends(get_category_or_404),
    session: Session = Depends(get_session),
):
    from app.models import Product
    count = session.exec(select(func.count(Product.id)).where(Product.category_id == category.id)).one()
    return {"category_id": category.id, "category_name": category.name, "products_count": count}