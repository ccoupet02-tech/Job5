import sys
from pathlib import Path
from loguru import logger
from datetime import datetime


def setup_logger(logs_dir: str = "data/logs", debug: bool = False):
    """Configure le logger avec rotation des fichiers"""
    
    # Créer le répertoire de logs s'il n'existe pas
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    
    # Supprimer la configuration par défaut
    logger.remove()
    
    # Niveau de log
    level = "DEBUG" if debug else "INFO"
    
    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # Fichier de log général avec rotation
    logger.add(
        f"{logs_dir}/app_{{time:YYYY-MM-DD}}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=level,
        rotation="00:00",  # Nouveau fichier chaque jour à minuit
        retention="30 days",  # Garder 30 jours de logs
        compression="zip"  # Compresser les anciens logs
    )
    
    # Fichier de log pour les erreurs uniquement
    logger.add(
        f"{logs_dir}/errors_{{time:YYYY-MM-DD}}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="90 days",
        compression="zip"
    )
    
    logger.info("Logger initialized successfully")
    return logger
