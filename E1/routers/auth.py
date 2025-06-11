# routers/auth.py
from datetime import timedelta
from sqlalchemy.orm import Session
from database import get_db
from config import Config
from utils.auth import (
    create_access_token, 
    get_current_user, 
    authenticate_user,
    get_password_hash
)
from crud.users_crud import UserCRUD 
from schemas import (
    Token, 
    UserCreate, 
    UserResponse,
    UserLogin
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_credentials: UserLogin, 
    db: Session = Depends(get_db)
):
    """Connexion utilisateur"""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": Config.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Ajout du temps d'expiration
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    """Informations utilisateur actuel"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user = Depends(get_current_user)):
    """Rafraîchit le token"""
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": Config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/register", response_model=dict)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Inscription utilisateur"""
    user_crud = UserCRUD(db)
    
    # Vérifier si l'utilisateur existe déjà
    if user_crud.get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec ce nom d'utilisateur existe déjà"
        )
    
    if user.email and user_crud.get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Créer l'utilisateur
    try:
        new_user = user_crud.create_user(user)
        return {
            "message": "Utilisateur créé avec succès",
            "username": new_user.username,
            "email": new_user.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
        )


@router.post("/logout", response_model=dict)
async def logout(current_user = Depends(get_current_user)):
    """Déconnexion utilisateur (optionnel - côté client)"""
    return {
        "message": "Déconnexion réussie. Supprimez le token côté client.",
        "username": current_user.username
    }


@router.post("/change-password", response_model=dict)
async def change_password(
    old_password: str,
    new_password: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Changer le mot de passe"""
    from utils.auth import verify_password
    
    # Vérifier l'ancien mot de passe
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect"
        )
    
    # Changer le mot de passe
    user_crud = UserCRUD(db)
    hashed_new_password = get_password_hash(new_password)
    
    try:
        user_crud.change_password(current_user.id, old_password, hashed_new_password)
        return {"message": "Mot de passe modifié avec succès"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du changement de mot de passe: {str(e)}"
        )
