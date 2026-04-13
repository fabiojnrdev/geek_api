
# FIX BUG-B3: Docstring de register_json tinha string não-fechada causando SyntaxError.

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
    get_password_hash,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    """Registra um novo usuário admin."""
    if get_user_by_username(session, user_create.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username já está em uso")
    if get_user_by_email(session, user_create.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já está em uso")
    return create_user(session, user_create.username, user_create.email, user_create.password)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Login via OAuth2 form-data (compatível com Swagger UI).

    Corpo: `username=admin&password=senha123` (x-www-form-urlencoded)
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo")

    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login-json", response_model=Token)
def login_json(credentials: UserLogin, session: Session = Depends(get_session)):
    """
    Login via JSON (para uso no frontend).

    ```json
    { "username": "admin", "password": "senha123" }
    ```
    """
    user = authenticate_user(session, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo")

    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register-json", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_json(user_create: UserCreate, session: Session = Depends(get_session)):
    """
    Registro via JSON.

    ```json
    { "username": "novo_usuario", "email": "user@example.com", "password": "senha123" }
    ```
    """
    if get_user_by_username(session, user_create.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username já está em uso")
    if get_user_by_email(session, user_create.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já está em uso")
    return create_user(session, user_create.username, user_create.email, user_create.password)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Retorna dados do usuário autenticado."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    email: str = None,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    """Atualiza email do usuário autenticado."""
    if email:
        existing = get_user_by_email(session, email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já está em uso")
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
    session: Session = Depends(get_session),
):
    """Altera a senha do usuário autenticado."""
    if not authenticate_user(session, current_user.username, current_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta")
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nova senha deve ter pelo menos 6 caracteres")
    current_user.hashed_password = get_password_hash(new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Senha alterada com sucesso"}


@router.delete("/me", status_code=status.HTTP_200_OK)
def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    """Desativa a conta do usuário autenticado (soft delete)."""
    current_user.is_active = False
    session.add(current_user)
    session.commit()
    return {"message": "Conta desativada com sucesso"}