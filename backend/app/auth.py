# app/auth.py — CORRIGIDO
# Bugs originais corrigidos:
#   1. authenticate_user: `if not User:` → `if not user:`
#   2. authenticate_user: query usava `User` (classe) em vez de `user` (instância)
#   3. create_access_token: settings attributes usam lowercase (pydantic-settings)
#   4. decode_access_token: settings.SECRET_KEY → settings.secret_key
#   5. create_access_token_for_user: settings.ACCESS_TOKEN_EXPIRE_MINUTES → lowercase

from datetime import timedelta, datetime
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.config import settings
from app.models import User, TokenData
from app.database import get_session

# ── Configuração de segurança ────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Password hashing ─────────────────────────────────────────

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ── JWT ───────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)   # ✅ FIX: lowercase
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)  # ✅ FIX


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,       # ✅ FIX: lowercase
            algorithms=[settings.algorithm]  # ✅ FIX
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(username=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Autenticação ─────────────────────────────────────────────

def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:                                          # ✅ FIX: era `if not User:`
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ── FastAPI Dependencies ──────────────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    token_data = decode_access_token(token)
    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo")
    return current_user


# ── Helpers ───────────────────────────────────────────────────

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(select(User).where(User.username == username)).first()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()


def create_user(session: Session, username: str, email: str, password: str) -> User:
    if get_user_by_username(session, username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username já existe")
    if get_user_by_email(session, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já existe")

    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def create_access_token_for_user(user: User) -> str:
    expires = timedelta(minutes=settings.access_token_expire_minutes)  # ✅ FIX: lowercase
    return create_access_token(data={"sub": user.username}, expires_delta=expires)


def authenticate_and_get_token(session: Session, username: str, password: str) -> str:
    user = authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token_for_user(user)


def register_user(session: Session, username: str, email: str, password: str) -> User:
    return create_user(session, username, email, password)