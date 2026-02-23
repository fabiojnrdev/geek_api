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

# Configuração de segurança

# Contexto para hash de senhas(bcrypt)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funções de password hashing

def verify_password(plain_password, hashed_password):
    """ Verifica se a senha em texto plano corresponde ao hash.
    
    Args:
        plain_password: Senha digitada pelo usuário
        hashed_password: Hash armazenado no banco
        
    Returns:
        True se a senha está correta, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """ Gera um hash para a senha fornecida.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)

# Funções JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Cria um token de acesso JWT.
    
    Args:
        data: Dados a serem incluídos no token
        expires_delta: Tempo de expiração do token (opcional)
        
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Codifica e retorna o token
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
def decode_access_token(token: str) -> TokenData:
    """ Decodifica um token JWT e extrai os dados do usuário.
    
    Args:
        token: Token JWT a ser decodificado
        
    Returns:
        TokenData contendo o username extraído do token
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
# Autenticação do usuário

def authenticate_user(session: Session,
                      username: str,
                      password: str) -> Optional[User]:
    """ Autentica um usuário verificando o username e a senha.
    Args:
        session: Sessão do banco de dados
        username: Username do usuário
        password: Senha em texto plano
        
    Returns:
        User se autenticado, None caso contrário
    """
    # Busca o usuário no banco de dados
    statement = select(User).where(User.username == User)
    user = Session.exec(statement).first()
    # Verifica se o usuário existe e se a senha está correta
    if not User or not verify_password(password, user.hashed_password):
        return None
    return user
# Dependências

async def get_current_user(token: str = Depends(oauth2_scheme), 
                           session: Session = Depends(get_session))-> User:
    """ Dependência que extrai e valida o usuário atual do token JWT.
    
    Uso:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    
    Args:
        token: Token JWT extraído do header Authorization
        session: Sessão do banco de dados
        
    Returns:
        Usuário autenticado
        
    Raises:
        HTTPException 401: Se token inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Decodifica token
    token_data = decode_access_token(token)
    # Busca usuário no banco de dados
    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependência que verifica se o usuário está ativo.
    
    Uso:
        @app.get("/admin")
        def admin_route(user: User = Depends(get_current_active_user)):
            return {"admin": user.username}
    
    Args:
        current_user: Usuário extraído do token
        
    Returns:
        Usuário ativo
        
    Raises:
        HTTPException 400: Se usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    return current_user

# Funções auxiliares

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """ Busca um usuário pelo username.
    
    Args:
        session: Sessão do banco de dados
        username: Username do usuário a ser buscado
        
    Returns:
        User se encontrado, None caso contrário
    """
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """ Busca um usuário pelo email.
    
    Args:
        session: Sessão do banco de dados
        email: Email do usuário a ser buscado
        
    Returns:
        User se encontrado, None caso contrário
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()
def create_user(session: Session, username: str, email: str, password: str) -> User:
    """ Cria um novo usuário no banco de dados.
    
    Args:
        session: Sessão do banco de dados
        username: Username do novo usuário
        email: Email do novo usuário
        password: Senha em texto plano do novo usuário
        
    Returns:
        User criado
    Raises:
        HTTPException 400: Se username ou email já existirem
    """
    if get_user_by_username(session, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe"
        )
    if get_user_by_email(session, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já existe"
        )
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
def create_access_token_for_user(user: User) -> str:
    """ Cria um token de acesso JWT para um usuário específico.
    
    Args:
        user: Usuário para o qual o token será criado
        
    Returns:
        Token JWT como string
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
def authenticate_and_get_token(session: Session, username: str, password: str) -> str:
    """ Autentica um usuário e retorna um token de acesso JWT.
    
    Args:
        session: Sessão do banco de dados
        username: Username do usuário
        password: Senha em texto plano do usuário
        
    Returns:
        Token JWT se autenticado, None caso contrário
    """
    user = authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token_for_user(user)
def register_user(session: Session, username: str, email: str, password: str) -> User:
    """ Registra um novo usuário e retorna o usuário criado.
    
    Args:
        session: Sessão do banco de dados
        username: Username do novo usuário
        email: Email do novo usuário
        password: Senha em texto plano do novo usuário
        
    Returns:
        User criado
    """
    return create_user(session, username, email, password)

