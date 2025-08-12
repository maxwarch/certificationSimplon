from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from data_processor import DataProcessor
from database import get_db
from utils.auth import get_current_user

from models import MarketAnalysis
from schemas import MaketAnalysis, UserResponse
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix="/market",
    tags=["Market"],
    responses={404: {"description": "Not found"}},
)

@router.get("/analysis")
async def get_market_analysis(
    market_params: MaketAnalysis,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Analyse du marché pour une commune"""

    sql_conditions = ["ma.code_commune = :code_commune"]
    params = {"code_commune": market_params.code_commune}
    
    if market_params.code_departement:
        sql_conditions.append("ma.code_departement = :code_departement")
        params["code_departement"] = market_params.code_departement
    
    if market_params.type_local:
        sql_conditions.append("ma.type_local = :type_local")
        params["type_local"] = market_params.type_local
        
    if market_params.period_start:
        sql_conditions.append("ma.period >= :period_start")
        params["period_start"] = market_params.period_start
        
    if market_params.period_end:
        sql_conditions.append("ma.period <= :period_end")
        params["period_end"] = market_params.period_end
    
    where_clause = " AND ".join(sql_conditions)
    
    sql_query = f"""
        SELECT 
            ma.*,
            c.nom as commune_nom,
            c.longitude as commune_longitude,
            c.latitude as commune_latitude
        FROM market_analysis ma
        JOIN communes c ON c.code = LPAD(ma.code_departement::text, 2, '0') || LPAD(ma.code_commune::text, 3, '0')
        WHERE {where_clause}
        ORDER BY ma.period DESC
    """
    
    results = db.execute(text(sql_query), params).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail="Aucune analyse trouvée")
    
    # Convertir les résultats en dictionnaires
    analysis = [dict(row._mapping) for row in results]
    
    return analysis

@router.post('/generate')
def generate(db: Session = Depends(get_db),
    code_commune: str = None,
    current_user: UserResponse = Depends(get_current_user)):
    processor = DataProcessor(db)
    processor.generate_market_analysis(code_commune)

    return True