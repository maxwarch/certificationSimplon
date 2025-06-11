# routers/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse, UserChangePassword
from crud.users_crud import get_user_crud
from utils.auth import get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/users",
    tags=["Users Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)  # Seuls les admins
):
    """Liste des utilisateurs (Admin seulement)"""
    user_crud = get_user_crud(db)
    users = user_crud.get_users(skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)  # Seuls les admins
):
    """Créer un nouvel utilisateur (Admin seulement)"""
    user_crud = get_user_crud(db)
    try:
        db_user = user_crud.create_user(user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Informations de l'utilisateur actuel"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Met à jour l'utilisateur actuel"""
    user_crud = get_user_crud(db)
    # Empêcher la modification du statut admin par soi-même
    if hasattr(user_update, 'is_admin'):
        user_update.is_admin = None
    
    try:
        updated_user = user_crud.update_user(current_user.id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/change-password")
async def change_current_user_password(
    password_change: UserChangePassword,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Change le mot de passe de l'utilisateur actuel"""
    user_crud = get_user_crud(db)
    success = user_crud.change_password(
        current_user.id,
        password_change.current_password,
        password_change.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Récupère un utilisateur par ID (Admin seulement)"""
    user_crud = get_user_crud(db)
    user = user_crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Met à jour un utilisateur (Admin seulement)"""
    user_crud = get_user_crud(db)
    try:
        updated_user = user_crud.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Supprime un utilisateur (Admin seulement)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user_crud = get_user_crud(db)
    success = user_crud.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Désactive un utilisateur (Admin seulement)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    user_crud = get_user_crud(db)
    deactivated_user = user_crud.deactivate_user(user_id)
    if not deactivated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return deactivated_user
