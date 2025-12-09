import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from loguru import logger

from utils.models import JobOffer, ApplicationResult
from config import DATABASE_PATH


class ApplicationDatabase:
    """Gère la base de données SQLite pour le tracking des candidatures"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._init_database()
        logger.info(f"Database initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialise la base de données et crée les tables"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des offres d'emploi scrapées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_offers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                contract_type TEXT,
                description TEXT,
                requirements TEXT,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                language TEXT,
                application_type TEXT,
                application_url TEXT,
                scraped_at TIMESTAMP,
                processed BOOLEAN DEFAULT 0
            )
        ''')
        
        # Table des candidatures envoyées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_offer_id TEXT NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                contract_type TEXT,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                language TEXT,
                application_type TEXT,
                cv_path TEXT,
                cover_letter_path TEXT,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                applied_at TIMESTAMP NOT NULL,
                notification_sent BOOLEAN DEFAULT 0,
                FOREIGN KEY (job_offer_id) REFERENCES job_offers (id)
            )
        ''')
        
        # Table des erreurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_offer_id TEXT,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                occurred_at TIMESTAMP NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def job_offer_exists(self, job_offer: JobOffer) -> bool:
        """
        Vérifie si une offre existe déjà dans la base
        
        Args:
            job_offer: Offre à vérifier
            
        Returns:
            True si existe, False sinon
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM job_offers WHERE id = ?",
            (job_offer.id,)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def save_job_offer(self, job_offer: JobOffer):
        """Sauvegarde une offre d'emploi"""
        if self.job_offer_exists(job_offer):
            logger.debug(f"Job offer already exists: {job_offer.id}")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO job_offers (
                id, title, company, location, contract_type, description,
                requirements, url, source, language, application_type,
                application_url, scraped_at, processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_offer.id,
            job_offer.title,
            job_offer.company,
            job_offer.location,
            job_offer.contract_type,
            job_offer.description,
            job_offer.requirements,
            job_offer.url,
            job_offer.source,
            job_offer.language,
            job_offer.application_type,
            job_offer.application_url,
            job_offer.scraped_at,
            False
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Job offer saved: {job_offer.id}")
    
    def mark_offer_as_processed(self, job_offer_id: str):
        """Marque une offre comme traitée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE job_offers SET processed = 1 WHERE id = ?",
            (job_offer_id,)
        )
        
        conn.commit()
        conn.close()
    
    def save_application(self, result: ApplicationResult):
        """Sauvegarde une candidature"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO applications (
                job_offer_id, job_title, company, location, contract_type,
                url, source, language, application_type, cv_path,
                cover_letter_path, success, error_message, applied_at,
                notification_sent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.job_offer.id,
            result.job_offer.title,
            result.job_offer.company,
            result.job_offer.location,
            result.job_offer.contract_type,
            result.job_offer.url,
            result.job_offer.source,
            result.job_offer.language,
            result.job_offer.application_type,
            result.cv_path,
            result.cover_letter_path,
            result.success,
            result.error_message,
            result.applied_at,
            result.notification_sent
        ))
        
        conn.commit()
        conn.close()
        
        # Marquer l'offre comme traitée
        self.mark_offer_as_processed(result.job_offer.id)
        
        logger.info(f"Application saved: {result.job_offer.title} at {result.job_offer.company}")
    
    def log_error(self, job_offer_id: Optional[str], error_type: str, error_message: str):
        """Log une erreur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO errors (job_offer_id, error_type, error_message, occurred_at)
            VALUES (?, ?, ?, ?)
        ''', (job_offer_id, error_type, error_message, datetime.now()))
        
        conn.commit()
        conn.close()
        
        logger.error(f"Error logged: {error_type} - {error_message}")
    
    def get_all_applications(self) -> List[dict]:
        """Récupère toutes les candidatures"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM applications
            ORDER BY applied_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> dict:
        """Récupère des statistiques sur les candidatures"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total candidatures
        cursor.execute("SELECT COUNT(*) FROM applications")
        total = cursor.fetchone()[0]
        
        # Candidatures réussies
        cursor.execute("SELECT COUNT(*) FROM applications WHERE success = 1")
        successful = cursor.fetchone()[0]
        
        # Candidatures échouées
        cursor.execute("SELECT COUNT(*) FROM applications WHERE success = 0")
        failed = cursor.fetchone()[0]
        
        # Par source
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM applications
            GROUP BY source
        ''')
        by_source = dict(cursor.fetchall())
        
        # Par langue
        cursor.execute('''
            SELECT language, COUNT(*) as count
            FROM applications
            GROUP BY language
        ''')
        by_language = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "by_source": by_source,
            "by_language": by_language
        }
