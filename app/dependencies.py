from typing import Optional
from fastapi import Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.database import get_session
from routers.auth import get_current_active_user
from app.models import User, Category, Product

def get_db():
    """ Dependência para obter uma sessão do banco de dados.
    
    Uso:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.exec(select(Item)).all()
            return items
            """
    return Depends(get_session)
def require_admin():
    """
   
    Dependencia que garante que apenas admins autenticados acessem a rota.
    
    Uso:
        @app.post("/admin/products")
        def create_product(admin: User = Depends(require_admin)):
            return {"admin": admin.username}
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        User admin
        
    Raises:
        HTTPException 403: Se usuário não for admin
        """
    return get_current_active_user
class PaginationParams:
    """ Dependência para obter parâmetros de paginação.
    
    Uso:
        @app.get("/products")
        def get_products(pagination: PaginationParams = Depends()):
            skip = pagination.skip
            limit = pagination.limit
            """
    def __init__(
        self, skip: int = Query(0, ge=0, description="Número de registros a pular"),
        limit: int = Query(10, ge=1, le=100, description="Limite de registros a retornar")
    ):
        self.skip = skip
        self.limit = limit
class ProductFilterParams:
    """ Dependência para obter parâmetros de filtro para produtos.
    
    Uso:
        @app.get("/products")
        def get_products(filters: ProductFilterParams = Depends()):
            category_id = filters.category_id
            price_min = filters.price_min
            price_max = filters.price_max
            """
    def __init__(
        self, 
        search: Optional[str] = Query(None, description="Termo de busca para nome ou descrição"),        category_id: Optional[int] = Query(None, description="ID da categoria para filtrar"),
        price_min: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
        price_max: Optional[float] = Query(None, ge=0, description="Preço máximo"),
        franquia_id: Optional[str] = Query(None, description="ID da franquia para filtrar"),
        is_active: Optional[bool] = Query(None, description="Filtrar por produtos ativos/inativos"),
        order_by: Optional[str] = Query("created_at", description="Ordenar por: nome, preco, created_at"),
        order_direction: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Direção: asc ou desc")
    ):
        self.search = search
        self.category_id = category_id
        self.franquia = franquia_id
        self.min_preco = price_min
        self.max_preco = price_min
        self.is_active = is_active
        self.order_by = order_by
        self.order_direction = order_direction
def get_category_or_404(category_id: int, session: Session) -> Category:
    """ Dependência para obter uma categoria pelo ID ou retornar 404.
    
    Uso:
        @app.get("/categories/{category_id}")
        def read_category(category: Category = Depends(get_category_or_404)):
            return category
    Args:
        category_id: ID da categoria a ser buscada
        session: Sessão do banco de dados
    Returns:
        Category se encontrado
    Raises:
        HTTPException 404: Se categoria não for encontrada
    """
    statement = select(Category).where(Category.id == category_id)
    category = session.exec(statement).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Categoria com ID {category_id} não encontrada")
    return category
def get_product_or_404(product_id: int, session: Session) -> Product:
    """ Dependência para obter um produto pelo ID ou retornar 404.
    Uso:
        @app.get("/products/{product_id}")
        def get_product(product: Product = Depends(get_product_or_404)):
            return product
    
    Args:
        product_id: ID do produto
        session: Sessão do banco
        
    Returns:
        Product encontrado
        
    Raises:
        HTTPException 404: Se produto não existir
    """
    statement = select(Product).where(Product.id == product_id)
    product = session.exec(statement).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Produto com ID {product_id} não encontrado")
    return product

def get_user_or_404(user_id: int, session: Session = Depends(get_session)) -> User:
    """ Dependência para obter um usuário pelo ID ou retornar 404.
    
    Uso:
        @app.get("/users/{user_id}")
        def read_user(user: User = Depends(get_user_or_404)):
            return user
    Args:
        user_id: ID do usuário a ser buscado
        session: Sessão do banco de dados
    Returns:
        User se encontrado
    Raises:
        HTTPException 404: Se usuário não for encontrado
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Usuário com ID {user_id} não encontrado")
    return user

def validate_category_exists(category_id: int, session: Session = Depends(get_session)) -> None:
    """ Dependência para validar se uma categoria existe.
    Args:
        category_id: ID da categoria a ser validada
        session: Sessão do banco de dados
    Raises:
        HTTPException 400: Se categoria não existir
    """
    statement = select(Category).where(Category.id == category_id)
    category = session.exec(statement).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Categoria com ID {category_id} não existe")
def validate_unique_category_name(name: str, session: Session = Depends(get_session), exclude_id: Optional[int] = None) -> None:
    """ Dependência para validar se o nome da categoria é único.
    
    Args:
    name: Nome da categoria a ser validada
    session: Sessão do banco de dados
    exclude_id: ID da categoria a ser excluída da validação (usado para updates)
    Raises:
    HTTPException 400: Se já existir uma categoria com o mesmo nome
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
def validate_unique_category_slug(slug: str, session: Session = Depends(get_session), exclude_id: Optional[int] = None
    ) -> None:
    """ Dependência para validar se o slug da categoria é único.
    
    Args:
        slug: Slug da categoria a ser validada
        session: Sessão do banco de dados
        exclude_id: ID da categoria a ser excluída da validação (usado para updates)
        
    Raises:
        HTTPException 400: Se já existir uma categoria com o mesmo slug
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