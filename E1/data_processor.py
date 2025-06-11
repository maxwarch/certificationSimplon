# data_processor.py
import pandas as pd
import requests
from sqlalchemy.orm import Session
from utils.data_loader import load_dvf_data_streaming
from models import DVFTransaction, Commune, MarketAnalysis
import logging
from typing import Optional
import numpy as np
from utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    def __init__(self, db_session: Session):
        self.db = db_session

    def download_and_process_dvf_data(self, year: int = 2023):
        """Télécharge et traite les données DVF"""
        try:
            # URL des données DVF
            url = "https://www.data.gouv.fr/fr/datasets/r/5ffa8553-0e8f-4622-add9-5c0b593ca1f8"

            # Lecture des données
            count = 0
            lendf = 0
            for df in load_dvf_data_streaming(url, chunksize=100):
                # Nettoyage des données
                df = self._clean_dvf_data(df)

                # Sauvegarde en base
                self._save_dvf_data(df)

                logger.info(
                    f"Traitement en cours: {len(df)} transactions")
                count = count + 1
                lendf = len(df) + lendf

                if count > 3:
                    return lendf

            return lendf

        except Exception as e:
            logger.error(f"Erreur lors du traitement DVF: {e}")
            raise

    def _clean_dvf_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données DVF"""

        # Suppression des valeurs aberrantes
        df = df.dropna(subset=['Valeur fonciere'])
        df = df[df['Valeur fonciere'] > 0]

        # Calcul du prix au m²
        df['Prix_m2'] = df['Valeur fonciere'] / \
            df['Surface reelle bati'].replace(0, np.nan)

        # Filtrage des prix au m² aberrants
        Q1 = df['Prix_m2'].quantile(0.25)
        Q3 = df['Prix_m2'].quantile(0.75)
        IQR = Q3 - Q1
        df = df[
            (df['Prix_m2'] >= Q1 - 1.5 * IQR) &
            (df['Prix_m2'] <= Q3 + 1.5 * IQR)
        ]

        # Conversion des dates
        df['Date mutation'] = pd.to_datetime(
            df['Date mutation'], format='%d/%m/%Y')

        return df

    def _save_dvf_data(self, df: pd.DataFrame):
        """Sauvegarde les données DVF en base"""
        for _, row in df.iterrows():
            transaction = DVFTransaction(
                date_mutation=row['Date mutation'],
                nature_mutation=row['Nature mutation'],
                valeur_fonciere=row['Valeur fonciere'],
                adresse_numero=row.get('Adresse numero'),
                adresse_nom_voie=row.get('Adresse nom voie'),
                code_postal=row.get('Code postal'),
                code_commune=row.get('Code commune'),
                nom_commune=row.get('Nom commune'),
                code_departement=row.get('Code departement'),
                type_local=row.get('Type local'),
                surface_reelle_bati=row.get('Surface reelle bati'),
                nombre_pieces_principales=row.get('Nombre pieces principales'),
                surface_terrain=row.get('Surface terrain'),
                longitude=row.get('Longitude'),
                latitude=row.get('Latitude')
            )
            self.db.add(transaction)

        self.db.commit()

    def fetch_communes_data(self):
        """Récupère les données des communes depuis l'API Géo"""
        try:
            url = "https://geo.api.gouv.fr/communes"
            params = {
                'fields': 'nom,code,codeDepartement,codeRegion,population,surface,centre',
                'format': 'json'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            communes_data = response.json()

            for commune_data in communes_data:
                commune = Commune(
                    code=commune_data['code'],
                    nom=commune_data['nom'],
                    code_departement=commune_data['codeDepartement'],
                    code_region=commune_data.get('codeRegion'),
                    population=commune_data.get('population'),
                    surface=commune_data.get('surface'),
                    longitude=commune_data.get('centre', {}).get(
                        'coordinates', [None, None])[0],
                    latitude=commune_data.get('centre', {}).get(
                        'coordinates', [None, None])[1]
                )
                self.db.merge(commune)

            self.db.commit()
            logger.info(
                f"Données de {len(communes_data)} communes récupérées")

        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des communes: {e}")
            raise

    def generate_market_analysis(self, code_commune: Optional[str] = None):
        """Génère l'analyse du marché"""
        try:
            query = self.db.query(DVFTransaction).filter(
                DVFTransaction.valeur_fonciere.isnot(None),
                DVFTransaction.surface_reelle_bati.isnot(None),
                DVFTransaction.surface_reelle_bati > 0
            )

            if code_commune:
                query = query.filter(
                    DVFTransaction.code_commune == code_commune)

            transactions = query.all()

            # Groupement par commune, période et type
            analysis_data = {}

            for transaction in transactions:
                key = (
                    transaction.code_commune,
                    transaction.date_mutation.strftime('%Y-%m'),
                    transaction.type_local
                )

                if key not in analysis_data:
                    analysis_data[key] = []

                prix_m2 = transaction.valeur_fonciere / transaction.surface_reelle_bati
                analysis_data[key].append({
                    'prix_m2': prix_m2,
                    'valeur_fonciere': transaction.valeur_fonciere
                })

            # Calcul des statistiques
            for key, data in analysis_data.items():
                code_commune, period, type_local = key
                prix_m2_list = [d['prix_m2'] for d in data]
                valeurs_list = [d['valeur_fonciere'] for d in data]

                analysis = MarketAnalysis(
                    code_commune=code_commune,
                    period=period,
                    type_local=type_local,
                    avg_price_m2=np.mean(prix_m2_list),
                    median_price_m2=np.median(prix_m2_list),
                    min_price_m2=np.min(prix_m2_list),
                    max_price_m2=np.max(prix_m2_list),
                    transaction_count=len(data),
                    total_volume=sum(valeurs_list)
                )

                self.db.add(analysis)

            self.db.commit()
            logger.info("Analyse du marché générée")

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {e}")
            raise
