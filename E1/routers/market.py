from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user

from models import MarketAnalysis
from schemas import UserResponse
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix="/market",
    tags=["Market"],
    responses={404: {"description": "Not found"}},
)

@router.get("/analysis/{code_commune}")
async def get_market_analysis(
    code_commune: str,
    type_local: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Analyse du marché pour une commune"""

    query = db.query(MarketAnalysis).filter(
        MarketAnalysis.code_commune == code_commune
    )

    if type_local:
        query = query.filter(MarketAnalysis.type_local == type_local)

    if period_start:
        query = query.filter(MarketAnalysis.period >= period_start)

    if period_end:
        query = query.filter(MarketAnalysis.period <= period_end)

    analysis = query.order_by(MarketAnalysis.period.desc()).all()

    if not analysis:
        raise HTTPException(status_code=404, message="Aucune analyse trouvée")

    return analysis
