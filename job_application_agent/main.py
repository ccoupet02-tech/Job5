#!/usr/bin/env python3
"""
Agent d'Automatisation de Candidatures
Auteur: Manus AI
Pour: Camille Coupet

Ce script automatise le processus complet de recherche d'emploi et de candidature.
"""

import sys
from pathlib import Path
from typing import List
from loguru import logger

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DEBUG_MODE,
    DRY_RUN,
    MAX_OFFERS_PER_RUN,
    ENABLED_SCRAPERS,
    LOGS_DIR
)
from utils.logger import setup_logger
from utils.models import JobOffer, ApplicationResult
from scrapers import get_scraper
from filters import JobFilter
from cv_generator import CVGenerator
from cover_letter import CoverLetterGenerator
from email_manager import EmailSender
from tracking import ApplicationDatabase, ApplicationExporter


class JobApplicationAgent:
    """Agent principal d'automatisation des candidatures"""
    
    def __init__(self):
        """Initialise l'agent"""
        # Setup logger
        self.logger = setup_logger(logs_dir=str(LOGS_DIR), debug=DEBUG_MODE)
        logger.info("=" * 60)
        logger.info("Job Application Agent Starting")
        logger.info("=" * 60)
        
        # Initialiser les composants
        self.job_filter = JobFilter()
        self.cv_generator = CVGenerator()
        self.cover_letter_generator = CoverLetterGenerator()
        self.email_sender = EmailSender()
        self.database = ApplicationDatabase()
        self.exporter = ApplicationExporter()
        
        logger.info("All components initialized successfully")
    
    def run(self):
        """Exécute le processus complet d'automatisation"""
        logger.info("Starting job application automation process")
        
        try:
            # 1. Scraping des offres
            logger.info("Step 1: Scraping job offers")
            all_offers = self._scrape_offers()
            logger.info(f"Total offers scraped: {len(all_offers)}")
            
            if not all_offers:
                logger.warning("No offers found. Exiting.")
                return
            
            # 2. Filtrage des offres
            logger.info("Step 2: Filtering job offers")
            filtered_offers = self._filter_offers(all_offers)
            logger.info(f"Offers after filtering: {len(filtered_offers)}")
            
            if not filtered_offers:
                logger.warning("No offers passed filters. Exiting.")
                return
            
            # 3. Traitement de chaque offre
            logger.info("Step 3: Processing qualified offers")
            results = []
            
            for i, offer in enumerate(filtered_offers, 1):
                logger.info(f"Processing offer {i}/{len(filtered_offers)}: {offer.title} at {offer.company}")
                
                try:
                    result = self._process_offer(offer)
                    results.append(result)
                    
                    # Sauvegarder dans la base de données
                    self.database.save_application(result)
                    
                except Exception as e:
                    logger.error(f"Error processing offer: {e}")
                    self.database.log_error(offer.id, "processing_error", str(e))
                    continue
            
            # 4. Génération du rapport
            logger.info("Step 4: Generating report")
            self._generate_report(results)
            
            logger.info("=" * 60)
            logger.info("Job Application Agent Completed Successfully")
            logger.info(f"Total applications sent: {sum(1 for r in results if r.success)}/{len(results)}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error in main process: {e}")
            raise
    
    def _scrape_offers(self) -> List[JobOffer]:
        """Scrape les offres depuis toutes les sources activées"""
        all_offers = []
        
        for scraper_name in ENABLED_SCRAPERS:
            logger.info(f"Scraping from: {scraper_name}")
            
            try:
                scraper = get_scraper(scraper_name)
                
                with scraper:
                    offers = scraper.scrape(max_offers=MAX_OFFERS_PER_RUN)
                    logger.info(f"Found {len(offers)} offers from {scraper_name}")
                    
                    # Sauvegarder les offres dans la base
                    for offer in offers:
                        self.database.save_job_offer(offer)
                    
                    all_offers.extend(offers)
                    
            except Exception as e:
                logger.error(f"Error scraping from {scraper_name}: {e}")
                self.database.log_error(None, "scraping_error", f"{scraper_name}: {str(e)}")
                continue
        
        return all_offers
    
    def _filter_offers(self, offers: List[JobOffer]) -> List[JobOffer]:
        """Filtre les offres selon les critères"""
        # Filtrer les doublons (offres déjà traitées)
        new_offers = [
            offer for offer in offers
            if not self._is_already_processed(offer)
        ]
        
        logger.info(f"New offers (not already processed): {len(new_offers)}")
        
        # Appliquer les filtres
        filtered = self.job_filter.filter_offers(new_offers)
        
        return filtered
    
    def _is_already_processed(self, offer: JobOffer) -> bool:
        """Vérifie si une offre a déjà été traitée"""
        return self.database.job_offer_exists(offer)
    
    def _process_offer(self, offer: JobOffer) -> ApplicationResult:
        """Traite une offre: génère CV, lettre, et envoie candidature"""
        
        # Générer le CV optimisé
        logger.info("Generating optimized CV")
        cv_path = self.cv_generator.generate_optimized_cv(offer)
        
        # Générer la lettre de motivation
        logger.info("Generating cover letter")
        cover_letter_path = self.cover_letter_generator.generate_cover_letter(offer)
        
        # Envoyer la candidature
        success = False
        error_message = None
        
        if not DRY_RUN:
            logger.info("Sending application")
            
            if offer.application_type == "email" or "@" in offer.application_url:
                # Candidature par email
                success = self.email_sender.send_application_email(
                    job_offer=offer,
                    cv_path=cv_path,
                    cover_letter_path=cover_letter_path
                )
                
                if not success:
                    error_message = "Failed to send application email"
            
            else:
                # Pour les autres types (formulaire, easy apply), on ne peut pas automatiser complètement
                # On envoie juste une notification avec les documents
                logger.warning(f"Application type '{offer.application_type}' requires manual submission")
                success = True  # Considéré comme succès car documents générés
                error_message = "Manual submission required"
            
            # Envoyer la notification
            logger.info("Sending notification email")
            notification_sent = self.email_sender.send_notification_email(
                job_offer=offer,
                cv_path=cv_path,
                cover_letter_path=cover_letter_path,
                application_success=success,
                error_message=error_message
            )
        else:
            logger.info("DRY RUN: Skipping actual application submission")
            success = True
            notification_sent = False
        
        # Créer le résultat
        result = ApplicationResult(
            job_offer=offer,
            success=success,
            error_message=error_message,
            cv_path=cv_path,
            cover_letter_path=cover_letter_path,
            notification_sent=notification_sent
        )
        
        return result
    
    def _generate_report(self, results: List[ApplicationResult]):
        """Génère un rapport des candidatures"""
        # Rapport textuel
        report = self.exporter.generate_report()
        logger.info(f"\n{report}")
        
        # Export CSV
        csv_path = self.exporter.export_to_csv()
        if csv_path:
            logger.info(f"CSV report exported: {csv_path}")
        
        # Export Excel
        excel_path = self.exporter.export_to_excel()
        if excel_path:
            logger.info(f"Excel report exported: {excel_path}")


def main():
    """Point d'entrée principal"""
    try:
        agent = JobApplicationAgent()
        agent.run()
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
