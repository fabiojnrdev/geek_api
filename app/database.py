# app/database.py

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from app.config import settings


# Configuração do engine
def get_engine():
    """
    Cria e retorna o engine do banco de dados.
    SQLite: usa StaticPool e check_same_thread=False
    PostgreSQL: configuração padrão otimizada
    """
    connect_args = {}
    poolclass = None
    
    if settings.database_url.startswith("sqlite"):
        # SQLite específico
        connect_args = {"check_same_thread": False}
        poolclass = StaticPool
        return create_engine(
            settings.database_url,
            echo=settings.debug,
            connect_args=connect_args,
            poolclass=poolclass
        )
    else:
        # PostgreSQL ou outros
        return create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )


# Instância global do engine
engine = get_engine()


def create_db_and_tables():
    """
    Cria todas as tabelas no banco de dados.
    Deve ser chamado na inicialização da aplicação (main.py).
    
    IMPORTANTE: Os models devem ser importados ANTES de chamar esta função
    para que SQLModel.metadata tenha conhecimento deles.
    """
    # Importa todos os models aqui para garantir que sejam registrados
    from app.models import User, Category, Product  # ✅ CORREÇÃO
    
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency que fornece uma sessão do banco de dados.
    Usado como dependência do FastAPI: Depends(get_session)
    """
    with Session(engine) as session:
        yield session


# Função auxiliar para transações manuais (opcional)
def get_session_context():
    """
    Retorna uma sessão para uso em context manager.
    
    Uso:
        with get_session_context() as session:
            session.add(item)
            session.commit()
    """
    return Session(engine)