
# Atualização:
#   - Nomes corrigidos: Produto → Product, ProdutoCreate → ProductCreate, etc.
#   - session.query() substituído por session.exec(select(...)) — API SQLModel correta
#   - Regra de negócio: deleção por estoque removida (responsabilidade do router/domínio)
#   - Importações corrigidas (models, não routers)

from typing import List, Optional
from sqlmodel import Session, select, or_
from decimal import Decimal

from app.models import Product, ProductCreate, ProductUpdate


class ProductService:
    """
    Serviço de domínio para operações com produtos.
    Encapsula queries reutilizáveis e lógica de negócio.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_product(self, product_create: ProductCreate) -> Product:
        product = Product(**product_create.model_dump())
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_products(
        self,
        nome: Optional[str] = None,
        preco: Optional[float] = None,
        category_id: Optional[int] = None,
        franquia: Optional[str] = None,
    ) -> List[Product]:
        query = select(Product)
        if nome:
            query = query.where(Product.nome.ilike(f"%{nome}%"))
        if preco is not None:
            query = query.where(Product.preco == Decimal(str(preco)))
        if category_id:
            query = query.where(Product.category_id == category_id)
        if franquia:
            query = query.where(Product.franquia.ilike(f"%{franquia}%"))
        return self.session.exec(query).all()

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.session.get(Product, product_id)

    def update_product(self, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        product = self.session.get(Product, product_id)
        if not product:
            return None
        for key, value in product_update.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        """
        Deleta produto permanentemente.
        Retorna True se deletado, False se não encontrado.
        """
        product = self.session.get(Product, product_id)
        if not product:
            return False
        self.session.delete(product)
        self.session.commit()
        return True

    def update_stock(self, product_id: int, quantidade: int) -> Optional[Product]:
        """
        Ajusta estoque somando `quantidade` (pode ser negativo para subtrair).
        Retorna None se produto não encontrado ou se o resultado seria negativo.
        """
        product = self.session.get(Product, product_id)
        if not product:
            return None
        new_qty = product.quantidade_estoque + quantidade
        if new_qty < 0:
            return None
        product.quantidade_estoque = new_qty
        self.session.commit()
        self.session.refresh(product)
        return product

    def search(self, term: str, limit: int = 10) -> List[Product]:
        """Busca full-text em nome, descrição e franquia."""
        pattern = f"%{term}%"
        statement = select(Product).where(
            Product.is_active == True,
            or_(
                Product.nome.ilike(pattern),
                Product.descricao.ilike(pattern),
                Product.franquia.ilike(pattern),
            ),
        ).limit(limit)
        return self.session.exec(statement).all()