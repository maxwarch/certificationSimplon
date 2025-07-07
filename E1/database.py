# database.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base

# Configuration de la base de données
engine = create_engine(os.getenv("DATABASE_URL"))

# Session pour les requêtes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database():
    """Création de toutes les tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données créée avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base de données: {e}")
        return False


def drop_database():
    """Suppression de toutes les tables"""
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables supprimées avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        return False


def get_db():
    """Générateur de session pour FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test de la connexion à la base de données"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        #print("✅ Connexion à la base de données réussie!")
        return True
    except Exception as e:
        raise e


if __name__ == "__main__":
    print("Configuration de la base de données...")

    # Test de connexion
    try:
        test_connection()

        # Création des tables
        create_database()

        # Vérification des tables créées
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables créées: {tables}")
    except Exception as e:
        print(f"❌ Erreur de connexion à la bdd: {e}")
