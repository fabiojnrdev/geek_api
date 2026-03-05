🎮 Geek Store API

> API REST completa para gerenciamento de loja geek com produtos de animes, games, mangás e mais!

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Sobre o Projeto

Sistema de gerenciamento de e-commerce geek desenvolvido com FastAPI** e SQLModel. A API oferece funcionalidades completas de CRUD para produtos, categorias e autenticação JWT para administradores.

Destaques

Autenticação JWT completa com bcrypt
CRUD de Produtos com filtros avançados e busca
Sistema de Categorias com slugs URL-friendly
Filtros e Busca avançados (preço, categoria, franquia, nome)
Dashboard de Estatísticas para admin
Documentação Interativa (Swagger UI)
Código Limpo e arquitetura profissional

---
Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno e rápido
- [SQLModel](https://sqlmodel.tiangolo.com/) - ORM com integração Pydantic
- [Pydantic](https://docs.pydantic.dev/) - Validação de dados
- [JWT](https://jwt.io/) - Autenticação stateless
- [Bcrypt](https://pypi.org/project/bcrypt/) - Hash de senhas
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

---

## 📁 Estrutura do Projeto
```
apigeek/
├── app/
│   ├── routers/
│   │   ├── auth.py          # Autenticação (register, login, me)
│   │   ├── categories.py    # CRUD de categorias
│   │   └── products.py      # CRUD de produtos
│   ├── models.py            # Models SQLModel + Schemas
│   ├── auth.py              # JWT + password hashing
│   ├── database.py          # Configuração do banco
│   ├── config.py            # Settings e env vars
│   ├── dependencies.py      # Dependencies reutilizáveis
│   └── main.py              # App FastAPI
├── seed.py                  # Popular banco com dados
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---
Instalação e Uso

Pré-requisitos

- Python 3.11+
- pip

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/geek-store-api.git
cd geek-store-api
```

2. Crie um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env com suas configurações
```

5. Popule o banco de dados
```bash
python seed.py
```

Credenciais padrão:
- Username: `admin`
- Password: `admin123`

6. Inicie o servidor
```bash
uvicorn app.main:app --reload
```

API rodando em: http://localhost:8000

---
Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI (interativa)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

🔐 Autenticação

A API usa **JWT (JSON Web Tokens)** para autenticação.

Fluxo de Autenticação

1. **Registrar usuário** (opcional, se não usar seed):
```bash
POST /api/auth/register
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "senha123"
}
```

2. **Fazer login**:
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

3. **Usar token** em requisições protegidas:
```bash
Authorization: Bearer {seu_token_aqui}
```

---

 Principais Endpoints

Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/register` | Criar conta admin | ❌ |
| POST | `/api/auth/login` | Login | ❌ |
| GET | `/api/auth/me` | Dados do usuário logado | ✅ |

Categorias

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/categories` | Listar categorias (paginado) | ❌ |
| GET | `/api/categories/all` | Todas categorias | ❌ |
| GET | `/api/categories/{id}` | Buscar por ID | ❌ |
| GET | `/api/categories/slug/{slug}` | Buscar por slug | ❌ |
| POST | `/api/categories` | Criar categoria | ✅ |
| PUT | `/api/categories/{id}` | Atualizar categoria | ✅ |
| DELETE | `/api/categories/{id}` | Deletar categoria | ✅ |

Produtos

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/products` | Listar produtos (filtros) | ❌ |
| GET | `/api/products/search?q=...` | Busca rápida | ❌ |
| GET | `/api/products/{id}` | Buscar por ID | ❌ |
| GET | `/api/products/franquia/{nome}` | Por franquia | ❌ |
| POST | `/api/products` | Criar produto | ✅ |
| PUT | `/api/products/{id}` | Atualizar produto | ✅ |
| PATCH | `/api/products/{id}/stock` | Atualizar estoque | ✅ |
| PATCH | `/api/products/{id}/toggle-active` | Ativar/Desativar | ✅ |
| DELETE | `/api/products/{id}` | Deletar produto | ✅ |
| GET | `/api/products/stats/overview` | Estatísticas gerais | ✅ |

---

Exemplos de Uso

 Listar produtos com filtros
```bash
GET /api/products?search=naruto&category_id=1&min_preco=50&max_preco=300&order_by=preco&order_direction=asc
```
Criar produto
```bash
POST /api/products
Authorization: Bearer {token}

{
  "nome": "Action Figure Goku",
  "descricao": "Figure articulada do Goku SSJ",
  "preco": 299.90,
  "quantidade_estoque": 50,
  "image_url": "https://example.com/goku.jpg",
  "category_id": 1,
  "franquia": "Dragon Ball Z"
}
```

Atualizar estoque
```bash
PATCH /api/products/1/stock?quantidade=10&operation=add
Authorization: Bearer {token}
```

---

Banco de Dados

Models

- User: Administradores (autenticação)
- Category: Categorias de produtos
- Product: Produtos da loja

Relacionamentos
```
Category (1) ──< (N) Product
```

Desenvolvimento

Por padrão usa **SQLite** (`geek_store.db`).

Produção

Configure para **PostgreSQL** no `.env`:
```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

---

Dados de Exemplo (Seed)

O seed cria:

- **1 usuário admin** (admin/admin123)
- **6 categorias** (Animes, Games, Mangás, Action Figures, Acessórios, Camisetas)
- **17 produtos** de exemplo variados

---

🚢 Deploy

Backend (Railway / Render)
```bash
# Railway
railway login
railway init
railway up

# Render
# Conecte seu repo GitHub e configure:
# Build Command: pip install -r requirements.txt
# Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Variáveis de Ambiente (Produção)
```env
DATABASE_URL=postgresql://...
SECRET_KEY=sua-chave-super-secreta-aqui
DEBUG=false
CORS_ORIGINS=["https://seu-frontend.vercel.app"]
```

---

Testes
```bash
# Rodar testes (quando implementados)
pytest

# Com coverage
pytest --cov=app tests/
```

---

Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---
Licença

Este projeto está sob a licença MIT. Veja o arquivo License para mais detalhes.

---

Autor

Fábio Júnior

- GitHub:(https://github.com/fabiojnrdev)
- LinkedIn: [Fábio Júnior](https://linkedin.com/in/fabiojnrdev)
- Email: contato.fjdev@gmail.com


---

<p align="center">
  Feito com dedicação total.
</p