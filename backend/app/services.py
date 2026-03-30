from typing import List, Optional
from sqlmodel import Session, select
from .models import Produto
from .schemas import ProdutoCreate, ProdutoUpdate

class ProdutoService:
    def __init__(self, session: Session):
        self.session = session

    def create_produto(self, produto_create: ProdutoCreate) -> Produto:
        produto = Produto(**produto_create.dict())
        self.session.add(produto)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def get_produtos(self, nome: Optional[str] = None, preco: Optional[float] = None, categoria: Optional[str] = None, franquia: Optional[str] = None) -> List[Produto]:
        query = select(Produto)
        if nome:
            query = query.where(Produto.nome == nome)
        if preco:
            query = query.where(Produto.preco == preco)
        if categoria:
            query = query.where(Produto.categoria == categoria)
        if franquia:
            query = query.where(Produto.franquia == franquia)
        return self.session.exec(query).all()

    def get_produto(self, produto_id: int) -> Optional[Produto]:
        return self.session.get(Produto, produto_id)

    def update_produto(self, produto_id: int, produto_update: ProdutoUpdate) -> Optional[Produto]:
        produto = self.session.get(Produto, produto_id)
        if not produto:
            return None
        for key, value in produto_update.dict(exclude_unset=True).items():
            setattr(produto, key, value)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def delete_produto(self, produto_id: int) -> bool:
        produto = self.session.get(Produto, produto_id)
        if not produto:
            return False
        if produto.quantidade_estoque > 0:
            return False
        self.session.delete(produto)
        self.session.commit()
        return True

    def atualizar_estoque(self, produto_id: int, quantidade: int) -> Optional[Produto]:
        produto = self.session.get(Produto, produto_id)
        if not produto:
            return None
        if produto.quantidade_estoque + quantidade < 0:
            return None
        produto.quantidade_estoque += quantidade
        self.session.commit()
        self.session.refresh(produto)
        return produto
