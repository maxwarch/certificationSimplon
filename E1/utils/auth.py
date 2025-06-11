# auth.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_db
from models import User
from config import Config
from schemas import TokenData
from crud.users_crud import UserCRUD

# Contexte de cryptage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token d'accès JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie le mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash le mot de passe"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authentifie un utilisateur avec le CRUD"""
    user_crud = UserCRUD(db)
    
    # Récupérer l'utilisateur
    user = user_crud.get_user_by_username(username)
    if not user:
        return None
    
    # Vérifier le mot de passe
    if not verify_password(password, user.hashed_password):
        return None
    
    # Vérifier que l'utilisateur est actif
    if not user.is_active:
        return None
    
    # Mettre à jour la dernière connexion
    user_crud.update_last_login(user.id)
    
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Récupère l'utilisateur actuel à partir du token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Décoder le token
        payload = jwt.decode(
            credentials.credentials, 
            Config.SECRET_KEY, 
            algorithms=[Config.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Récupérer l'utilisateur avec le CRUD
    user_crud = UserCRUD(db)
    user = user_crud.get_user_by_username(token_data.username)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Vérifie que l'utilisateur actuel est admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Récupère l'utilisateur actuel actif"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def verify_token(token: str) -> Optional[dict]:
    """Vérifie un token JWT et retourne le payload"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        return payload
    except JWTError:
        return None


def create_password_reset_token(username: str) -> str:
    """Crée un token de réinitialisation de mot de passe"""
    expires_delta = timedelta(hours=1)  # Expire dans 1 heure
    to_encode = {
        "sub": username,
        "type": "password_reset",
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Vérifie un token de réinitialisation et retourne le username"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "password_reset":
            return None
            
        return username
    except JWTError:
        return None
