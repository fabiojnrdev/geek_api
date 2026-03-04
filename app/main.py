from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.database import engine, create_db_and_tables

# Importa todas as rotas
from app.routers import auth, categories, products

# Eventos de Lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia eventos de inicialização e encerramento da aplicação.
    
    Startup:
    - Cria tabelas no banco de dados
    - Inicializa recursos necessários
    
    Shutdown:
    - Limpa recursos
    """
    # Startup
    print("🚀 Iniciando Geek Store API...")
    print(f"📊 Database: {settings.database_url}")
    
    # Cria as tabelas
    create_db_and_tables()
    print("✅ Tabelas criadas/verificadas com sucesso!")
    
    yield
    
    # Shutdown
    print("👋 Encerrando Geek Store API...")

# Instãncia do FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🎮 **Geek Store API** - Sistema de gerenciamento de loja geek
    
    ## 📦 Funcionalidades
    
    * **Produtos**: CRUD completo com filtros avançados, busca e gestão de estoque
    * **Categorias**: Organização de produtos por categorias (Animes, Games, Mangás, etc)
    * **Autenticação**: Sistema JWT para admins
    * **Estatísticas**: Dashboards e relatórios de produtos
    
    ## 🔐 Autenticação
    
    Para acessar endpoints protegidos:
    1. Faça login em `/api/auth/login`
    2. Copie o `access_token` retornado
    3. Clique em "Authorize" no topo da página
    4. Cole o token no formato: `Bearer {seu_token}`
    
    ## 🚀 Links Úteis
    
    * [Documentação Interativa (Swagger)](/docs)
    * [Documentação Alternativa (ReDoc)](/redoc)
    * [GitHub](https://github.com/seu-usuario/geek-store)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug,
     # Metadata adicional
    contact={
        "name": "Geek Store Team",
        "email": "contato.fjdev@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Autenticação",
            "description": "Endpoints de registro, login e gerenciamento de usuários"
        },
        {
            "name": "Categorias",
            "description": "CRUD de categorias de produtos"
        },
        {
            "name": "Produtos",
            "description": "CRUD de produtos, filtros, busca e estatísticas"
        },
    ]
)
# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.cors_origins,
    allor_credentials=True,
    allow_methods=["*"],
    allor_headers=["*"],
)

# Request Timing

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Adiciona header X-Process-Time com o tempo de processamento da requisição.
    Útil para monitorar performance.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    return response

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler customizado para tratamento de erros de validação
    Retorna mensagens de erro mais confortantes
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field" : "->".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"] 
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação",
            "errors": errors
        }
    )
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para exceções não tratadas.
    Em produção, não expõe detalhes internos
    """
    if settings.debug:
        # Dentro do debug, mostra o erro por completo
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Erro interno do servidor",
                "error": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        # Em produção, retorna mensagem genérica
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Erro interno do servidor. Por favor, tente novamente."
            }
        )
# Routers (Todas elas)

# Autenticação
app.include_router(
    auth.router,
    prefix="/api",
    tags=["Autenticação"]
)
# Categorias
app.include_router(
    categories.router,
    prefix="/api",
    tags=["Categorias"]
)
# Produtos
app.include_router(
    products.router,
    prefix="/api",
    tags=["Produtos"]
)

# Root 