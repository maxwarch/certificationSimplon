# models.py
from sqlalchemy import Boolean, Column, Integer, String, Float, Date, DateTime, func

from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"