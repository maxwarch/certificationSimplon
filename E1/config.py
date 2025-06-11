"""Configuration settings for the sports observatory project"""
import os
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"

    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
