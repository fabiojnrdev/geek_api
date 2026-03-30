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
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Cria uma nova categoria.
    
    **Requer autenticação (Admin)**
    
    **Corpo da requisição:**
```json
    {
        "name": "Animes",
        "description": "Produtos relacionados a animes japoneses"
    }
```
    
    **Retorna:**
    - Categoria criada com slug gerado automaticamente
    
    **Erros:**
    - 400: Nome já existe
    - 401: Não autenticado
    
    **Nota:**
    - O slug é gerado automaticamente a partir do nome
    - Exemplo: "Animes e Mangás" → "animes-e-mangas"
    """
    # Valida se nome é único
    validate_unique_category_name(session, category_in.name)
    # Gera slug
    slug = generate_slug(category_in.name)
    # Valida se slug é único
    validate_unique_category_slug(session, slug)
    # Cria categoria
    new_category = Category(
        name=category_in.name,
        description=category_in.description,
        slug=slug
    )
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    
    return new_category
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_data: CategoryUpdate,
    category: Category = Depends(get_category_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza uma categoria existente.
    
    **Requer autenticação (Admin)**
    
    **Path Parameters:**
    - category_id: ID da categoria a atualizar
    
    **Corpo da requisição (todos campos opcionais):**
```json
    {
        "name": "Novo Nome",
        "description": "Nova descrição"
    }
```
    
    **Retorna:**
    - Categoria atualizada
    
    **Erros:**
    - 400: Novo nome já existe
    - 404: Categoria não encontrada
    - 401: Não autenticado
    
    **Nota:**
    - Se o nome for alterado, o slug é recalculado automaticamente
    """
    update_data = category_data.model_dump(exclude_unset=True)
    # Se o nome está sendo atualizado
    if "name" in update_data and update_data["name"] != category.name:
        # Valida se novo nome é único
        validate_unique_category_name(
            update_data["name"],
            session,
            exclude_id=category.id
        )
        
        # Gera novo slug
        new_slug = generate_slug(update_data["name"])
        
        # Valida se novo slug é único
        validate_unique_category_slug(
            new_slug,
            session,
            exclude_id=category.id
        )
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
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta uma categoria.
    
    **Requer autenticação (Admin)**
    
    **Path Parameters:**
    - category_id: ID da categoria a deletar
    
    **Retorna:**
    - 204 No Content (sucesso)
    
    **Erros:**
    - 400: Categoria possui produtos associados
    - 404: Categoria não encontrada
    - 401: Não autenticado
    
    **Nota:**
    - Não é possível deletar categorias com produtos associados
    - Delete os produtos primeiro ou reatribua-os a outra categoria
    """
    from app.models import Product
    # Verifica se categoria tem produtos associados
    statement = select(func.count(Product.id)).where(Product.category_id == category.id)
    product_count = session.exec(statement).one()
    
    if product_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível deletar esta categoria. Ela possui {product_count} produto(s) associado(s)."
        )
    
    # Deleta a categoria
    session.delete(category)
    session.commit()
    
    return None
@router.get("/{category_id}/products_count")
def get_category_products_count(
    category: Category = Depends(get_category_or_404),
    session: Session = Depends(get_session)
):
    """
    Retorna a quantidade de produtos em uma categoria.
    
    Path Parameters:
    - category_id: ID da categoria
    
    Retorna:
```json
    {
        "category_id": 1,
        "category_name": "Animes",
        "products_count": 25
    }
```
    
    Útil para:
    - Mostrar contadores no frontend
    - Validar antes de deletar categoria
    """
    from app.models import Product
    statement = select(func.count(Product.id)).where(Product.category_id == category.id)
    count = session.exec(statement).one()

    return {
        "category_id": category.id,
        "category_name": category.name,
        "products_count": count
    }