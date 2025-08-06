# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import test_connection
from utils.logger import get_logger

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

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Erreur de validation: {str(exc)}"}
    )

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
