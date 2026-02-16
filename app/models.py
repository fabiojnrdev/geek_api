from sqlmodel import SQLModel, Field

class Produto(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nome: str
    descricao: str
    preco: float
    quantidade_estoque: int
    categoria: str
    franquia: str