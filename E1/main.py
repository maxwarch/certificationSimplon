# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from database import get_db, test_connection
from data_processor import DataProcessor
from utils.logger import get_logger

from schemas import UserResponse

from routers import (
    auth_router,
    transactions_router,
    communes_router,
    market_router,
    stats_router,
    users_router
)

logger = get_logger(__name__)

app = FastAPI(title="Plateforme Immobilière", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(communes_router)
app.include_router(market_router)
app.include_router(stats_router)
app.include_router(users_router)


@app.get("/")
async def root():
    return {"message": "Plateforme d'analyse immobilière"}


@app.post("/data/refresh")
async def refresh_data(db: Session = Depends(get_db)):
    """Rafraîchit les données"""
    count = None
    try:
        processor = DataProcessor(db)

        # Récupération des communes
        processor.fetch_communes_data()

        # Traitement des données DVF
        count = processor.download_and_process_dvf_data()

        # Génération des analyses
        processor.generate_market_analysis()

        return {
            'status': 'success',
            'transactions_processed': count,
            'message': 'Données rafraîchies avec succès'
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    try:
        test_connection()
        
        return {
            "status": "healthy",
            "service": "immobilier_api",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Connexion impossible à la bdd: {e}")
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "unhealthy",
                "service": "immobilier_api",
                "error": str(e)
            }
        )
