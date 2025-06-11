from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sqlalchemy
from database import get_db
from models import UserInDB
from auth import get_current_user
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
    dependencies=[Depends(get_current_user)],  # Protection globale du router
    responses={404: {"description": "Not found"}},
)

@router.get("/department/{code_departement}")
async def get_department_statistics(
    code_departement: str,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """Statistiques par département"""

    # Requête pour obtenir les statistiques agrégées
    query = sqlalchemy.text("""
        SELECT 
            type_local,
            COUNT(*) as transaction_count,
            round(AVG(valeur_fonciere)::numeric, 2) as avg_price,
            round(AVG(valeur_fonciere / NULLIF(surface_reelle_bati, 0))::numeric , 2) as avg_price_m2,
            round(SUM(valeur_fonciere)::numeric, 2) as total_volume
        FROM dvf_transactions 
        WHERE code_departement = :dept
          AND valeur_fonciere > 0 
          AND surface_reelle_bati > 0
        GROUP BY type_local
        ORDER BY transaction_count DESC
    """)

    params = {
        'dept': str(code_departement).removeprefix('0'),
    }
    result = db.execute(query, params)
    stats = result.fetchall()

    return {
        'department': code_departement,
        'statistics': [
            {
                'type_local': row[0],
                'transaction_count': row[1],
                'avg_price': row[2],
                'avg_price_m2': row[3],
                'total_volume': row[4]
            }
            for row in stats
        ]
    }