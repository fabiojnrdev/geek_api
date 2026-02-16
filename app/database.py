from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import StaticPool
from app.config import settings
from app.models import Produto

DATABASE_URL = "sqlite:///./geek_store.db"
def get_engine():
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        poolclass = StaticPool if settings.database_url.startswith("sqlite") else None
        return create_engine(
            settings.database_url,
            connect_args=connect_args,
            poolclass=poolclass
    )
    else:
        return create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size = 8,
            max_overflow = 10
        )
engine = get_engine()
SQLModel.metadata.create_all(engine)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
"""
    Cria todas as tabelas no banco de dados.
    Deve ser chamado na inicialização da aplicação (main.py).
    """
def get_session():
    """
    Retorna uma sessã o de banco de dados.
    Usado como dependência do FastAPI: Depends(get_session)
    
    Uso:
        @app.get("/items")
        def read_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_session_context():
    return Session(engine)