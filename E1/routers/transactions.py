from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sqlalchemy
from database import get_db
from models import DVFTransaction
from schemas import TransactionResponse, UserResponse
from utils.auth import get_current_user
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
    dependencies=[Depends(get_current_user)],  # Protection globale du router
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_transactions(
    code_commune: Optional[str] = None,
    type_local: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> List[TransactionResponse]:
    """Récupère les transactions"""
    
    try:
        query = db.query(DVFTransaction)

        # Filtrer les valeurs invalides dès la requête
        query = query.filter(
            DVFTransaction.valeur_fonciere.isnot(None),
            DVFTransaction.valeur_fonciere > 0
        )

        if code_commune:
            query = query.filter(DVFTransaction.code_commune == code_commune)

        if type_local:
            query = query.filter(DVFTransaction.type_local == type_local)

        if date_start:
            query = query.filter(DVFTransaction.date_mutation >= date_start)

        if date_end:
            query = query.filter(DVFTransaction.date_mutation <= date_end)

        if min_price:
            query = query.filter(DVFTransaction.valeur_fonciere >= min_price)

        if max_price:
            query = query.filter(DVFTransaction.valeur_fonciere <= max_price)

        transactions = query.order_by(
            DVFTransaction.date_mutation.desc()
        ).limit(limit).all()
        
        return [TransactionResponse.model_validate(t) for t in transactions]
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des transactions")


@router.get("/investment-opportunities")
async def get_investment_opportunities(
    budget_max: float,
    type_local: str = "Appartement",
    rentabilite_min: float = 4.0,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Opportunités d'investissement"""

    try:
        # Validation des paramètres
        if budget_max <= 0:
            raise HTTPException(status_code=400, detail="Le budget doit être positif")
        
        if rentabilite_min <= 0:
            raise HTTPException(status_code=400, detail="La rentabilité minimum doit être positive")

        # Requête complexe pour identifier les opportunités
        query = sqlalchemy.text("""
            WITH commune_stats AS (
                SELECT 
                    code_commune,
                    nom_commune,
                    LPAD(code_departement::text, 2, '0') || LPAD(code_commune::text, 3, '0') as code_com,
                    AVG(CAST(valeur_fonciere AS NUMERIC) / NULLIF(surface_reelle_bati, 0)) as prix_m2_moyen,
                    COUNT(*) as nb_transactions,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY valeur_fonciere) as prix_median
                FROM dvf_transactions
                WHERE type_local = :type_local
                AND valeur_fonciere <= :budget_max
                AND surface_reelle_bati > 0
                AND valeur_fonciere > 0
                GROUP BY code_commune, nom_commune, code_com
                HAVING COUNT(*) >= 5
            )
            SELECT 
                c.nom ,
                round(cs.prix_m2_moyen::numeric, 2) as prix_m2_moyen,
                cs.nb_transactions,
                cs.prix_median as prix_median,
                COALESCE(c.population, 0) as population,
                c.latitude, c.longitude 
            FROM commune_stats cs
            LEFT JOIN communes c ON cs.code_com = c.code
            WHERE cs.prix_m2_moyen <= :prix_m2_max
            AND cs.prix_m2_moyen > 0
            ORDER BY cs.prix_m2_moyen ASC
            LIMIT 20;
        """)

        # Paramètres de la requête
        params = {
            'type_local': type_local,
            'budget_max': budget_max,
            # 'date_start': datetime.now() - timedelta(days=365),
            'prix_m2_max': budget_max / 50  # Exemple de calcul
        }

        logger.info(f"Executing investment opportunities query with params: {params}")
        
        result = db.execute(query, params)
        opportunities = result.fetchall()

        logger.info(f"Found {len(opportunities)} investment opportunities")

        return {
            'criteria': {
                'budget_max': budget_max,
                'type_local': type_local,
                'rentabilite_min': rentabilite_min,
                'date_recherche': datetime.now().isoformat()
            },
            'opportunities': [
                {
                    'nom_commune': row[0],
                    'prix_m2_moyen': round(float(row[1]), 2) if row[1] else 0,
                    'nb_transactions': int(row[2]),
                    'prix_median': round(float(row[3]), 2) if row[3] else 0,
                    'population': int(row[4]) if row[4] else 0,
                    'lat': row[5],
                    'lon': row[6],
                    'ratio_prix_budget': round((float(row[3]) / budget_max * 100), 2) if row[3] else 0
                }
                for row in opportunities
            ],
            'meta': {
                'total_found': len(opportunities),
                'query_date': datetime.now().isoformat()
            }
        }

    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(f"Database error in get_investment_opportunities: {e}")
        raise HTTPException(status_code=500, detail="Erreur de base de données")
    
    except Exception as e:
        logger.error(f"Unexpected error in get_investment_opportunities: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")