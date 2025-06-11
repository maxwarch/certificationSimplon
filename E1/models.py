# models.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

import math
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

Base = declarative_base()


class DVFTransaction(Base):
    __tablename__ = 'dvf_transactions'

    id = Column(Integer, primary_key=True, index=True)
    date_mutation = Column(Date)
    nature_mutation = Column(String(50))
    valeur_fonciere = Column(Float)
    adresse_numero = Column(String(10))
    adresse_suffixe = Column(String(10))
    adresse_nom_voie = Column(String(255))
    adresse_code_voie = Column(String(10))
    code_postal = Column(String(50))
    code_commune = Column(String(50))
    nom_commune = Column(String(100))
    code_departement = Column(String(30))
    ancien_code_commune = Column(String(50))
    ancien_nom_commune = Column(String(100))
    ancien_id_parcelle = Column(String(50))
    numero_volume = Column(String(10))
    lot1_numero = Column(String(10))
    lot1_surface_carrez = Column(Float)
    lot2_numero = Column(String(10))
    lot2_surface_carrez = Column(Float)
    lot3_numero = Column(String(10))
    lot3_surface_carrez = Column(Float)
    lot4_numero = Column(String(10))
    lot4_surface_carrez = Column(Float)
    lot5_numero = Column(String(10))
    lot5_surface_carrez = Column(Float)
    nombre_lots = Column(Integer)
    type_local = Column(String(50))
    surface_reelle_bati = Column(Float)
    nombre_pieces_principales = Column(Integer)
    surface_terrain = Column(Float)
    longitude = Column(Float)
    latitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Commune(Base):
    __tablename__ = 'communes'

    code = Column(String(5), primary_key=True, unique=True)
    nom = Column(String(100))
    code_departement = Column(String(3))
    code_region = Column(String(3))
    population = Column(Integer)
    surface = Column(Float)
    longitude = Column(Float)
    latitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketAnalysis(Base):
    __tablename__ = 'market_analysis'

    id = Column(Integer, primary_key=True, index=True)
    code_commune = Column(String(5))
    period = Column(String(20))  # YYYY-MM
    type_local = Column(String(50))
    avg_price_m2 = Column(Float)
    median_price_m2 = Column(Float)
    min_price_m2 = Column(Float)
    max_price_m2 = Column(Float)
    transaction_count = Column(Integer)
    total_volume = Column(Float)
    price_evolution = Column(Float)  # % par rapport à la période précédente
    created_at = Column(DateTime, default=datetime.utcnow)



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


# Auth Modèles
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(BaseModel):
    username: str
    email: Optional[str] = None
    hashed_password: str
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str