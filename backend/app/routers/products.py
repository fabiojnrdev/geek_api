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


# Setup de rotas

router = APIRouter(
    prefix="/products",
    tags=["Produtos"]
)


# Endpoints Públicos

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
    
    # Ordenação
    if filters.order_by == "nome":
        order_column = Product.nome
    elif filters.order_by == "preco":
        order_column = Product.preco
    else:  # created_at (padrão)
        order_column = Product.created_at
    
    if filters.order_direction == "asc":
        statement = statement.order_by(order_column.asc())
    else:
        statement = statement.order_by(order_column.desc())
    
    # Total de produtos (com filtros aplicados)
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # Aplica paginação
    products = session.exec(
        statement.offset(pagination.skip).limit(pagination.limit)
    ).all()
    
    return paginated_response(
        items=products,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., min_length=1, max_length=100, description="Termo de busca"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados"),
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
            Product.franquia.ilike(search_term)
        )
    ).limit(limit)
    
    products = session.exec(statement).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product: Product = Depends(get_product_or_404)
):
    """
    Busca um produto por ID.
    
    **Path Parameters:**
    - product_id: ID do produto
    
    **Retorna:**
    - Produto com categoria completa
    
    **Erros:**
    - 404: Produto não encontrado
    
    **Exemplo:**
```
    GET /api/products/1
```
    """
    return product


@router.get("/franquia/{franquia}", response_model=List[ProductResponse])
def get_products_by_franquia(
    franquia: str,
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """
    Lista produtos de uma franquia específica.
    
    **Path Parameters:**
    - franquia: Nome da franquia (ex: "Naruto", "One Piece")
    
    **Query Parameters:**
    - limit: Limite de resultados (default: 20, max: 100)
    
    **Exemplo:**
```
    GET /api/products/franquia/Naruto?limit=10
```
    
    **Retorna:**
    - Lista de produtos da franquia
    """
    statement = select(Product).where(
        Product.franquia.ilike(f"%{franquia}%"),
        Product.is_active == True
    ).limit(limit)
    
    products = session.exec(statement).all()
    return products


# Endpoints protegidos (Admin)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria um novo produto.
    
    **Requer autenticação (Admin)**
    
    **Corpo da requisição:**
```json
    {
        "nome": "Action Figure Naruto Uzumaki",
        "descricao": "Figure de alta qualidade do personagem Naruto",
        "preco": 299.90,
        "quantidade_estoque": 50,
        "image_url": "https://example.com/naruto.jpg",
        "category_id": 1,
        "franquia": "Naruto Shippuden"
    }
```
    
    **Retorna:**
    - Produto criado
    
    **Erros:**
    - 400: Categoria não existe
    - 401: Não autenticado
    """
    # Valida se categoria existe
    validate_category_exists(product_data.category_id, session)
    
    # Cria o produto
    new_product = Product(
        nome=product_data.nome,
        descricao=product_data.descricao,
        preco=product_data.preco,
        quantidade_estoque=product_data.quantidade_estoque,
        image_url=product_data.image_url,
        category_id=product_data.category_id,
        franquia=product_data.franquia
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
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza um produto existente.
    
    **Requer autenticação (Admin)**
    
    **Path Parameters:**
    - product_id: ID do produto
    
    **Corpo da requisição (todos campos opcionais):**
```json
    {
        "nome": "Novo nome",
        "preco": 349.90,
        "quantidade_estoque": 30
    }
```
    
    **Retorna:**
    - Produto atualizado
    
    **Erros:**
    - 400: Categoria não existe (se category_id fornecido)
    - 404: Produto não encontrado
    - 401: Não autenticado
    """
    update_data = product_data.model_dump(exclude_unset=True)
    
    # Se está atualizando a categoria, valida
    if "category_id" in update_data:
        validate_category_exists(update_data["category_id"], session)
    
    # Atualiza os campos
    for key, value in update_data.items():
        setattr(product, key, value)
    
    # Atualiza timestamp
    product.updated_at = datetime.utcnow()
    
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    product_id: int,
    quantidade: int = Query(..., description="Nova quantidade em estoque (pode ser negativa para diminuir)"),
    operation: str = Query("set", regex="^(set|add|subtract)$", description="Operação: set (definir), add (adicionar), subtract (subtrair)"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza o estoque de um produto.
    
    **Requer autenticação (Admin)**
    
    **Path Parameters:**
    - product_id: ID do produto
    
    **Query Parameters:**
    - quantidade: Quantidade
    - operation: Tipo de operação
      - "set": Define o estoque (substitui)
      - "add": Adiciona ao estoque atual
      - "subtract": Subtrai do estoque atual
    
    **Exemplos:**
```
    PATCH /api/products/1/stock?quantidade=100&operation=set
    PATCH /api/products/1/stock?quantidade=10&operation=add
    PATCH /api/products/1/stock?quantidade=5&operation=subtract
```
    
    **Retorna:**
    - Produto com estoque atualizado
    
    **Erros:**
    - 400: Operação resultaria em estoque negativo
    - 404: Produto não encontrado
    - 401: Não autenticado
    """
    product = session.get(Product, product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {product_id} não encontrado"
        )
    
    # Calcula novo estoque baseado na operação
    if operation == "set":
        new_stock = quantidade
    elif operation == "add":
        new_stock = product.quantidade_estoque + quantidade
    else:  # subtract
        new_stock = product.quantidade_estoque - quantidade
    
    # Valida se estoque não fica negativo
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Operação resultaria em estoque negativo ({new_stock})"
        )
    
    product.quantidade_estoque = new_stock
    product.updated_at = datetime.utcnow()
    
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product


@router.patch("/{product_id}/toggle-active", response_model=ProductResponse)
def toggle_product_active(
    product: Product = Depends(get_product_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ativa/Desativa um produto (soft delete).
    
    **Requer autenticação (Admin)**
    
    **Path Parameters:**
    - product_id: ID do produto
    
    **Retorna:**
    - Produto com is_active alternado
    
    **Nota:**
    - Produtos inativos não aparecem em listagens públicas
    - Útil para "ocultar" produtos sem deletá-los
    """
    product.is_active = not product.is_active
    product.updated_at = datetime.utcnow()
    
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product: Product = Depends(get_product_or_404),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta permanentemente um produto.
    
    **Requer autenticação (Admin)**
    
    **Path Parameters:**
    - product_id: ID do produto
    
    **Retorna:**
    - 204 No Content (sucesso)
    
    **Erros:**
    - 404: Produto não encontrado
    - 401: Não autenticado
    
    **⚠️ ATENÇÃO:**
    - Deleção permanente (não pode ser desfeita)
    - Considere usar PATCH /toggle-active para soft delete
    """
    session.delete(product)
    session.commit()
    
    return None



# Endpoints de estatisticas (Admin)


@router.get("/stats/overview")
def get_products_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna estatísticas gerais dos produtos.
    
    **Requer autenticação (Admin)**
    
    **Retorna:**
```json
    {
        "total_products": 150,
        "active_products": 142,
        "inactive_products": 8,
        "out_of_stock": 5,
        "low_stock": 12,
        "total_inventory_value": 45890.50
    }
```
    """
    # Total de produtos
    total = session.exec(select(func.count(Product.id))).one()
    
    # Produtos ativos
    active = session.exec(
        select(func.count(Product.id)).where(Product.is_active == True)
    ).one()
    
    # Produtos inativos
    inactive = total - active
    
    # Sem estoque
    out_of_stock = session.exec(
        select(func.count(Product.id)).where(Product.quantidade_estoque == 0)
    ).one()
    
    # Estoque baixo (menos de 10 unidades)
    low_stock = session.exec(
        select(func.count(Product.id)).where(
            Product.quantidade_estoque > 0,
            Product.quantidade_estoque < 10
        )
    ).one()
    
    # Valor total do inventário
    inventory_value = session.exec(
        select(func.sum(Product.preco * Product.quantidade_estoque))
    ).one() or 0
    
    return {
        "total_products": total,
        "active_products": active,
        "inactive_products": inactive,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "total_inventory_value": float(inventory_value)
    }


@router.get("/stats/by-category")
def get_products_by_category_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna estatísticas de produtos por categoria.
    
    **Requer autenticação (Admin)**
    
    **Retorna:**
```json
    [
        {
            "category_id": 1,
            "category_name": "Animes",
            "product_count": 45,
            "total_value": 12500.00
        },
        ...
    ]
```
    """
    from sqlmodel import col
    
    statement = select(
        Product.category_id,
        Category.name.label("category_name"),
        func.count(Product.id).label("product_count"),
        func.sum(Product.preco * Product.quantidade_estoque).label("total_value")
    ).join(Category).group_by(Product.category_id, Category.name)
    
    results = session.exec(statement).all()
    
    return [
        {
            "category_id": r.category_id,
            "category_name": r.category_name,
            "product_count": r.product_count,
            "total_value": float(r.total_value or 0)
        }
        for r in results
    ]