# utils/data_loader.py
from pathlib import Path
import zipfile
import pandas as pd
import chardet
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


def download_file(url: str, filename: str) -> None:
    if Path(filename).exists():
        return filename

    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)
        return filename


def unzip_and_rename(zip_path: str, new_name: str, extract_to: str = ".") -> None:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extraire dans un dossier temporaire
        temp_dir = Path(extract_to) / "temp_extract"
        zip_ref.extractall(temp_dir)

        # Renommer le premier dossier/fichier extrait
        extracted_items = list(temp_dir.iterdir())
        if extracted_items:
            old_path = extracted_items[0]
            new_path = Path(extract_to) / new_name
            old_path.rename(new_path)

            # Supprimer le dossier temporaire
            temp_dir.rmdir()


def detect_encoding(file_path):
    """Détecte l'encodage d'un fichier"""
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)  # Lire les premiers 10KB
        result = chardet.detect(raw_data)
        return result['encoding']


def load_csv_safe(file_path, chunksize=10000, **kwargs):
    """Charge un CSV en détectant automatiquement l'encodage"""
    file_path = download_file(file_path, '/app/data/dvf.zip')
    unzip_and_rename(file_path, 'dvf.txt', '/app/data')
    file_path = '/app/data/dvf.txt'
    encoding = detect_encoding(file_path)

    if chunksize:
        return pd.read_csv(file_path, encoding=encoding, chunksize=chunksize, **kwargs)

    return pd.read_csv(file_path, encoding=encoding, **kwargs)


def load_dvf_data(file_path, chunksize=10000):
    """Charge les données DVF avec gestion d'encodage"""
    try:
        logger.info(f"📂 Chargement de {file_path}")

        # Chargement avec gestion d'encodage
        df = load_csv_safe(file_path, sep='|',
                           chunksize=chunksize, low_memory=False)

        logger.info(f"✅ {len(df)} lignes chargées")
        return df

    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement: {e}")
        return None


def load_dvf_data_streaming(file_path, chunksize=10000):
    """Traite les données DVF en streaming"""
    chunks = load_csv_safe(file_path, chunksize=chunksize,
                           sep='|', decimal=',', date_format='%d/%m/%Y', low_memory=False)

    for i, chunk in enumerate(chunks):
        yield chunk

def load_communes_data(file_path):
    """Charge les données des communes avec gestion d'encodage"""
    try:
        logger.info(f"📂 Chargement des communes depuis {file_path}")

        # Chargement avec gestion d'encodage
        df = load_csv_safe(file_path)

        logger.info(f"✅ {len(df)} communes chargées")
        return df

    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des communes: {e}")
        return None
