from datetime import timedelta
from config import Config
from auth import (
    authenticate_user, create_access_token, get_current_user
)

from models import (
    Token, UserCreate, UserInDB, UserLogin
)
from fastapi import APIRouter, Depends, HTTPException, status

ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


# ==============================================================================
# ROUTES D'AUTHENTIFICATION
# ==============================================================================

@router.post("/login", response_model=Token)
async def login_for_access_token(user_credentials: UserLogin):
    """Connexion utilisateur"""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """Informations utilisateur actuel"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active
    }

@router.post("/auth/refresh")
async def refresh_token(current_user: UserInDB = Depends(get_current_user)):
    """Rafraîchit le token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=dict)
async def register_user(user: UserCreate):
    """Inscription utilisateur (optionnel)"""
    # Implémentez votre logique d'inscription ici
    return {"message": "User registration endpoint - to be implemented"}