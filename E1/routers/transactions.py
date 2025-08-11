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
    prix_m2_max: float = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Opportunités d'investissement"""

    try:
        # Validation des paramètres
        if budget_max <= 0:
            raise HTTPException(status_code=400, detail="Le budget doit être positif")
        
        # Requête complexe pour identifier les opportunités
        query = sqlalchemy.text("""
            WITH commune_stats AS (
                SELECT 
                    code_commune,
                    commune,
                    LPAD(code_departement::text, 2, '0') || LPAD(code_commune::text, 3, '0') as code_com,
                    AVG(prix_m2) as prix_m2_moyen,
                    COUNT(*) as nb_transactions,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY valeur_fonciere) as prix_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY prix_m2) as prix_m2_median
                FROM dvf_transactions
                WHERE type_local = :type_local
                AND valeur_fonciere <= :budget_max
                AND surface_reelle_bati > 0
                AND valeur_fonciere > 0
                GROUP BY code_commune, commune, code_com
                HAVING COUNT(*) >= 5
            )
            SELECT 
                c.nom ,
                round(cs.prix_m2_moyen::numeric, 2) as prix_m2_moyen,
                cs.nb_transactions,
                round(cs.prix_median::numeric, 2) as prix_median,
                round(cs.prix_m2_median::numeric, 2) as prix_m2_median,
                COALESCE(c.population, 0) as population,
                c.latitude, c.longitude 
            FROM commune_stats cs
            LEFT JOIN communes c ON cs.code_com = c.code
            WHERE cs.prix_m2_moyen <= :prix_m2_max
            AND cs.prix_m2_moyen >= (SELECT PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY prix_m2_moyen) FROM commune_stats)
            ORDER BY cs.prix_m2_moyen ASC
            LIMIT 5;
        """)

        # Paramètres de la requête
        params = {
            'type_local': type_local,
            'budget_max': budget_max,
            # 'date_start': datetime.now() - timedelta(days=365),
            'prix_m2_max': budget_max / 50 if not(prix_m2_max) else prix_m2_max  # Exemple de calcul
        }

        logger.info(f"Executing investment opportunities query with params: {params}")
        
        result = db.execute(query, params)
        opportunities = result.fetchall()

        logger.info(f"Found {len(opportunities)} investment opportunities")
        print(opportunities)
        return {
            'criteria': {
                'budget_max': budget_max,
                'm2_max': params['prix_m2_max'],
                'type_local': type_local,
                'date_recherche': datetime.now().isoformat()
            },
            'opportunities': [
                {
                    'nom_commune': row[0],
                    'prix_m2_moyen': row[1] if row[1] else 0,
                    'nb_transactions': int(row[2]),
                    'prix_median': row[3] if row[3] else 0,
                    'prix_m2_median': row[4] if row[3] else 0,
                    'population': int(row[5]) if row[4] else 0,
                    'lat': row[6],
                    'lon': row[7],
                    'ratio_prix_budget': round((float(row[3]) / budget_max * 100), 2) if row[3] else 0,
                    'ratio_prix_m2_budget': round((float(row[4]) / params['prix_m2_max'] * 100), 2) if row[4] else 0
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

# %% [markdown]
"""
**Cette expression crée un code commune sur 5 caractères :**

```sql
LPAD(code_departement::text, 2, '0') || LPAD(code_commune::text, 3, '0') as code_com
```

**Décomposition :**

1. **`LPAD(code_departement::text, 2, '0')`** : 
   - Complète le code département à 2 chiffres avec des 0 à gauche
   - Ex: `6` → `"06"`

2. **`LPAD(code_commune::text, 3, '0')`** :
   - Complète le code commune à 3 chiffres avec des 0 à gauche  
   - Ex: `123` → `"123"`, `45` → `"045"`

3. **`||`** : Concatène les deux chaînes

**Exemple concret :**
- Département: `6`, Commune: `123`
- Résultat: `"06123"` (code INSEE officiel)

**But :** Créer le **code INSEE** standardisé pour faire le `JOIN` avec la table `communes` qui utilise ce format dans sa colonne `code`.
"""
# %%
