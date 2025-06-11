# crud/users.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from passlib.context import CryptContext
from models import User
from schemas import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_password_hash(self, password: str) -> str:
        """Hash le mot de passe"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie le mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par nom d'utilisateur"""
        return self.db.query(User).filter(User.username == username.lower()).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    def get_users(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
        """Récupère une liste d'utilisateurs"""
        query = self.db.query(User)
        if active_only:
            query = query.filter(User.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def create_user(self, user: UserCreate) -> User:
        """Crée un nouvel utilisateur"""
        # Vérifier si l'utilisateur existe déjà
        existing_user = self.get_user_by_username(user.username)
        if existing_user:
            raise ValueError(f"Username '{user.username}' already exists")
        
        if user.email:
            existing_email = self.get_user_by_email(user.email)
            if existing_email:
                raise ValueError(f"Email '{user.email}' already exists")
        
        # Créer l'utilisateur
        hashed_password = self.get_password_hash(user.password)
        db_user = User(
            username=user.username.lower(),
            email=user.email.lower() if user.email else None,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=getattr(user, 'is_admin', False)
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Met à jour un utilisateur"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        # Vérifier l'email si changé
        if user_update.email and user_update.email != db_user.email:
            existing_email = self.get_user_by_email(user_update.email)
            if existing_email and existing_email.id != user_id:
                raise ValueError(f"Email '{user_update.email}' already exists")
        
        # Mettre à jour les champs
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'email' and value:
                value = value.lower()
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change le mot de passe d'un utilisateur"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        # Vérifier le mot de passe actuel
        if not self.verify_password(current_password, db_user.hashed_password):
            return False
        
        # Mettre à jour le mot de passe
        db_user.hashed_password = self.get_password_hash(new_password)
        self.db.commit()
        return True
    
    def delete_user(self, user_id: int) -> bool:
        """Supprime un utilisateur"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Désactive un utilisateur"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        db_user.is_active = False
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    def update_last_login(self, user_id: int) -> None:
        """Met à jour la dernière connexion"""
        from datetime import datetime
        db_user = self.get_user(user_id)
        if db_user:
            db_user.last_login = datetime.now()
            self.db.commit()

def get_user_crud(db: Session) -> UserCRUD:
    """Factory pour UserCRUD"""
    return UserCRUD(db)

def update_user_password(self, user_id: int, hashed_password: str):
    """Met à jour le mot de passe d'un utilisateur"""
    user = self.db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Utilisateur non trouvé")
    
    user.hashed_password = hashed_password
    user.updated_at = func.now()
    self.db.commit()
    self.db.refresh(user)
    return user

def get_user_by_email(self, email: str) -> Optional[User]:
    """Récupère un utilisateur par email"""
    return self.db.query(User).filter(User.email == email.lower()).first()