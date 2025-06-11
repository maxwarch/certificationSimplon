from typing import Optional
from fastapi import APIRouter, Depends, Query
from requests import Session
from models import Commune
from database import get_db
#from auth import get_current_user

router = APIRouter(
    prefix="/communes",
    tags=["Communes"],
    #dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_communes(
    departement: Optional[str] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Récupère la liste des communes"""
    query = db.query(Commune)

    if departement:
        query = query.filter(Commune.code_departement == departement)

    communes = query.limit(limit).all()
    return communes