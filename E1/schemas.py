import math
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    date_mutation: Optional[datetime] = None
    valeur_fonciere: Optional[float] = None
    code_commune: Optional[str] = None
    nom_commune: Optional[str] = None
    type_local: Optional[str] = None
    surface_reelle_bati: Optional[float] = None
    nombre_pieces: Optional[int] = None
    
    # Validators pour nettoyer les valeurs float
    @field_validator('valeur_fonciere', 'surface_reelle_bati', mode='before')
    @classmethod
    def clean_float_values(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            if math.isnan(v) or math.isinf(v):
                return None
            return float(v)
        return v
        
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    is_admin: bool = False
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('New password must be at least 6 characters long')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None


class MaketAnalysis(BaseModel):
    code_commune: str
    code_departement: Optional[str] = None
    type_local: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None