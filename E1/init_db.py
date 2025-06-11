# init_db.py
import sys
from sqlalchemy import text
from database import create_database, test_connection, engine


def init_database():
    """Initialisation complète de la base de données"""

    print("🚀 Initialisation de la base de données...")

    # 1. Test de connexion
    print("\n1. Test de connexion...")
    if not test_connection():
        print("❌ Impossible de continuer sans connexion")
        sys.exit(1)

    # 2. Création des tables
    print("\n2. Création des tables...")
    if not create_database():
        print("❌ Impossible de créer les tables")
        sys.exit(1)

    # 3. Création des index pour les performances
    print("\n3. Création des index...")
    create_indexes()

    # 4. Insertion de données de test (optionnel)
    # print("\n4. Données de test...")
    # insert_test_data()

    print("\n✅ Initialisation terminée!")


def create_indexes():
    """Création des index pour optimiser les performances"""
    indexes = [
        # Index sur DVFTransaction
        text("CREATE INDEX IF NOT EXISTS idx_dvf_date_mutation ON dvf_transactions(date_mutation);"),
        text("CREATE INDEX IF NOT EXISTS idx_dvf_code_commune ON dvf_transactions(code_commune);"),
        text("CREATE INDEX IF NOT EXISTS idx_dvf_code_postal ON dvf_transactions(code_postal);"),
        text("CREATE INDEX IF NOT EXISTS idx_dvf_type_local ON dvf_transactions(type_local);"),
        text("CREATE INDEX IF NOT EXISTS idx_dvf_nature_mutation ON dvf_transactions(nature_mutation);"),
        text("CREATE INDEX IF NOT EXISTS idx_dvf_valeur_fonciere ON dvf_transactions(valeur_fonciere);"),
        text("CREATE INDEX IF NOT EXISTS idx_dvf_surface_terrain ON dvf_transactions(surface_terrain);"),
        text("CREATE INDEX IF NOT EXISTS idx_dvf_location ON dvf_transactions(longitude, latitude);"),

        # Index sur Commune
        text("CREATE INDEX IF NOT EXISTS idx_commune_departement ON communes(code_departement);"),
        text("CREATE INDEX IF NOT EXISTS idx_commune_region ON communes(code_region);"),
        text("CREATE INDEX IF NOT EXISTS idx_commune_nom ON communes(nom);"),

        # Index sur MarketAnalysis
        text("CREATE INDEX IF NOT EXISTS idx_market_commune_period ON market_analysis(code_commune, period);"),
        text("CREATE INDEX IF NOT EXISTS idx_market_type_local ON market_analysis(type_local);"),
        text("CREATE INDEX IF NOT EXISTS idx_market_period ON market_analysis(period);"),
    ]

    try:
        with engine.connect() as connection:
            for index_sql in indexes:
                connection.execute(index_sql)
            connection.commit()
        print("✅ Index créés avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors de la création des index: {e}")

def create_default_users():
    from database import SessionLocal
    from crud.users_crud import UserCRUD
    from schemas import UserCreate

    """Crée les utilisateurs par défaut"""
    db = SessionLocal()
    user_crud = UserCRUD(db)
    
    try:
        # Créer l'admin par défaut
        admin_user = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",
            is_admin=True
        )
        
        # Créer l'utilisateur test
        test_user = UserCreate(
            username="user",
            email="user@example.com", 
            password="user123",
            is_admin=False
        )

        # Créer l'utilisateur test
        admin_user2 = UserCreate(
            username="admin2",
            email="admin2@example.com", 
            password="admin123",
            is_admin=True
        )
        
        # Vérifier et créer si nécessaire
        if not user_crud.get_user_by_username("admin"):
            user_crud.create_user(admin_user)
            print("✅ Utilisateur admin créé")
        
        user_crud.create_user(admin_user2)
        if not user_crud.get_user_by_username("user"):
            user_crud.create_user(test_user)
            print("✅ Utilisateur test créé")
            
            
    except Exception as e:
        print(f"❌ Erreur lors de la création des utilisateurs : {e}")


def check_tables():
    """Vérification des tables créées"""
    try:
        with engine.connect() as connection:
            # Vérification des tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))

            tables = [row[0] for row in result]
            print(f"📋 Tables disponibles: {tables}")

            # Vérification du contenu
            for table in ['communes', 'dvf_transactions', 'market_analysis']:
                if table in tables:
                    count_result = connection.execute(
                        text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    print(f"   - {table}: {count} enregistrements")

    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")


if __name__ == "__main__":
    init_database()
    create_default_users()
    check_tables()
