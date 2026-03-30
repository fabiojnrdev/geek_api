from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.database import get_session
from app.models import User, UserCreate, UserLogin, UserResponse, Token
from app.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_active_user,
    get_user_by_username,
    get_user_by_email,
    get_password_hash
)
from app.config import settings

# Configuração de rota

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Endpoints de autenticação

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    """ Endpoint para registrar um novo usuário.
    
    Uso:
        @app.post("/auth/register")
        def register(user_create: UserCreate, session: Session = Depends(get_session)):
            return register(user_create, session)
            Args:
        user_create: Dados para criar um novo usuário
        session: Sessão do banco de dados
        Raises:
        HTTPException 400: Se username ou email já estiverem em uso
    """
    if get_user_by_username(session, user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso"
        )
    if get_user_by_email(session, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    new_user = create_user(session, user_create.username, user_create.email, user_create.password)
    return new_user
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """ Autentica um usuário e retorna um token JWT.
    
    **Corpo da requisição (form-data):**
    - username: string
    - password: string
    
    **Retorna:**
    - access_token: Token JWT
    - token_type: "bearer"
    
    **Erros:**
    - 401: Credenciais inválidas
    
    **Exemplo de uso:**
```
    POST /api/auth/login
    Content-Type: application/x-www-form-urlencoded
    
    username=admin&password=senha123
```
"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Verifica se o usuáario é ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Cria o token JWT
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-json", response_model=Token)
def login_json(
    credentials: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Versão alternativa do login que aceita JSON ao invés de form-data.
    
    **Corpo da requisição (JSON):**
```json
    {
        "username": "admin",
        "password": "senha123"
    }
```
    
    **Retorna:**
    - access_token: Token JWT
    - token_type: "bearer"
    
    **Erros:**
    - 401: Credenciais inválidas
    """
    # Autentica o usuário
    user = authenticate_user(session, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Cria o token JWT
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
@router.post("/register-json", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_json(user_create: UserCreate, session: Session = Depends(get_session)):
    """ Endpoint para registrar um novo usuário usando JSON.
    
    **Corpo da requisição (JSON):**
    ```json
    {
        "username": "novo_usuario",
        "email": "
        "password: "senha123"
        }
        """
    if get_user_by_username(session, user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso"
        )
    if get_user_by_email(session, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    new_user = create_user(session, user_create.username, user_create.email, user_create.password)
    return new_user
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """ Endpoint para obter informações do usuário autenticado.
    
    **Retorna:**
    - id: ID do usuário
    - username: Username do usuário
    - email: Email do usuário
    - is_active: Status de atividade do usuário
    
    **Erros:**
    - 401: Token inválido ou ausente
    """
    return current_user
@router.put("/me", response_model=UserResponse)
def update_current_user(
    email: str = None,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Atualiza informações do usuário autenticado.
    
    **Requer autenticação:**
    - Header: `Authorization: Bearer {token}`
    
    **Corpo da requisição:**
```json
    {
        "email": "novo_email@example.com"
    }
```
    
    **Retorna:**
    - Dados atualizados do usuário
    
    **Erros:**
    - 400: Email já está em uso
    - 401: Token inválido
    """
    if email:
        existing_user = get_user_by_email(session, email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        current_user.email = email
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Altera a senha do usuário autenticado.
    
    **Requer autenticação:**
    - Header: `Authorization: Bearer {token}`
    
    **Corpo da requisição:**
```json
    {
        "current_password": "senha_atual",
        "new_password": "nova_senha_123"
    }
```
    
    **Retorna:**
    - Mensagem de sucesso
    
    **Erros:**
    - 400: Senha atual incorreta ou nova senha inválida
    - 401: Token inválido
    """
    if not authenticate_user(session, current_user.username, current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ter pelo menos 6 caracteres"
        )
    current_user.hashed_password = get_password_hash(new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Senha alterada com sucesso"}
@router.delete("/me", status_code=status.HTTP_200_OK)
def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Desativa a conta do usuário autenticado (soft delete).
    
    **Requer autenticação:**
    - Header: `Authorization: Bearer {token}`
    
    **Retorna:**
    - Mensagem de confirmação
    
    **Nota:**
    - A conta é desativada (is_active=False), não deletada permanentemente
    - O usuário não poderá mais fazer login
    """
    current_user.is_active = False
    session.add(current_user)
    session.commit()
    
    return {"message": "Conta desativada com sucesso"}