#!/usr/bin/env python

from data_processor import DataProcessor
from database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info('Start CRON')
db = next(get_db())

try:
    processor = DataProcessor(db)

    # Récupération des communes
    processor.fetch_communes_data(logger_cron=logger)

    # Traitement des données DVF
    count = processor.download_and_process_dvf_data(logger_cron=logger)

    # Génération des analyses
    #processor.generate_market_analysis(code_commune="350", logger_cron=logger)

except Exception as e:
    logger.error(f"{'='*10} Erreur {'='*10}")
    logger.error(e)
    logger.error(f"{'='*10} Fin Erreur {'='*10}")

logger.info('End CRON')