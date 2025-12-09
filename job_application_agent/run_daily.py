#!/usr/bin/env python3
"""
Script d'exécution quotidienne du système d'automatisation
Recherche les offres, génère les documents, et envoie le rapport HTML par email
"""

import sys
import os
from pathlib import Path
from typing import List
from datetime import datetime

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

# Activer l'environnement virtuel si nécessaire
venv_path = Path(__file__).parent.parent / "job_agent_env"
if venv_path.exists():
    activate_this = venv_path / "bin" / "activate_this.py"
    if activate_this.exists():
        exec(open(activate_this).read(), {'__file__': str(activate_this)})

from config import (
    DEBUG_MODE,
    ENABLED_SCRAPERS,
    MAX_OFFERS_PER_RUN,
    LOGS_DIR,
    NOTIFICATION_EMAIL,
    CANDIDATE_EMAIL,
    CANDIDATE_EMAIL_PASSWORD,
    OUTPUT_DIR
)
from utils.logger import setup_logger
from utils.models import JobOffer, ApplicationResult
from scrapers import get_scraper
from filters import JobFilter
from cv_generator import CVGenerator
from cover_letter import CoverLetterGenerator
from email_manager import EmailSender
from tracking import ApplicationDatabase
from html_reporter import HTMLReporter

# Setup logger
logger = setup_logger(logs_dir=str(LOGS_DIR), debug=DEBUG_MODE)


class DailyJobApplicationRunner:
    """Exécute le processus quotidien d'automatisation"""
    
    def __init__(self, test_data_path=None):
        logger.info("=" * 70)
        logger.info("DAILY JOB APPLICATION RUNNER - Starting")
        logger.info(f"Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        self.test_data_path = test_data_path
        
        # Initialiser les composants
        self.job_filter = JobFilter()
        self.cv_generator = CVGenerator()
        self.cover_letter_generator = CoverLetterGenerator()
        self.email_sender = EmailSender()
        self.database = ApplicationDatabase()
        self.html_reporter = HTMLReporter()
        
        logger.info("All components initialized")
    
    def run(self):
        """Exécute le processus complet"""
        try:
            # 1. Scraping
            logger.info("\n📍 STEP 1: Scraping job offers...")
            all_offers = self._scrape_offers()
            logger.info(f"✓ Total offers scraped: {len(all_offers)}")
            
            if not all_offers:
                logger.warning("No offers found. Exiting.")
                return False
            
            # 2. Filtrage
            logger.info("\n📍 STEP 2: Filtering job offers...")
            filtered_offers = self._filter_offers(all_offers)
            logger.info(f"✓ Offers after filtering: {len(filtered_offers)}")
            
            if not filtered_offers:
                logger.warning("No offers passed filters.")
                return False
            
            # 3. Traitement des offres
            logger.info(f"\n📍 STEP 3: Processing {len(filtered_offers)} qualified offers...")
            results = self._process_offers(filtered_offers)
            
            successful = sum(1 for r in results if r.success)
            logger.info(f"✓ Processed: {successful}/{len(results)} successful")
            
            # 4. Génération du rapport HTML
            logger.info("\n📍 STEP 4: Generating HTML report...")
            html_path = self.html_reporter.generate_report(results)
            logger.info(f"✓ HTML report generated: {html_path}")
            
            # 5. Envoi du rapport par email
            logger.info("\n📍 STEP 5: Sending report via email...")
            email_sent = self._send_report_email(html_path, len(filtered_offers), successful)
            
            if email_sent:
                logger.info(f"✓ Report sent to {NOTIFICATION_EMAIL}")
            else:
                logger.warning("Failed to send report email")
            
            # Résumé final
            logger.info("\n" + "=" * 70)
            logger.info("DAILY JOB APPLICATION RUNNER - COMPLETED SUCCESSFULLY")
            logger.info(f"Total offers found: {len(all_offers)}")
            logger.info(f"Offers qualified: {len(filtered_offers)}")
            logger.info(f"Candidatures ready: {successful}")
            logger.info(f"Report sent to: {NOTIFICATION_EMAIL}")
            logger.info("=" * 70 + "\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return False
    
    def _scrape_offers(self) -> List[JobOffer]:
        """Scrape les offres depuis toutes les sources ou charge les données de test"""
        
        if self.test_data_path:
            logger.info(f"  Loading test data from: {self.test_data_path}")
            import json
            from utils.models import JobOffer
            
            with open(self.test_data_path, 'r', encoding='utf-8') as f:
                raw_offers = json.load(f)
            
            all_offers = [JobOffer(**offer) for offer in raw_offers]
            
            logger.info(f"  Loaded {len(all_offers)} offers from test data.")
            return all_offers
        
        all_offers = []
        
        for scraper_name in ENABLED_SCRAPERS:
            logger.info(f"  Scraping from: {scraper_name}")
            
            try:
                scraper = get_scraper(scraper_name)
                
                with scraper:
                    offers = scraper.scrape(max_offers=MAX_OFFERS_PER_RUN)
                    logger.info(f"    Found {len(offers)} offers")
                    
                    # Sauvegarder dans la base
                    for offer in offers:
                        self.database.save_job_offer(offer)
                    
                    all_offers.extend(offers)
                    
            except Exception as e:
                logger.error(f"  Error scraping {scraper_name}: {e}")
                continue
        
        return all_offers
    
    def _filter_offers(self, offers: List[JobOffer]) -> List[JobOffer]:
        """Filtre les offres"""
        # Éliminer les doublons
        new_offers = [
            offer for offer in offers
            if not self.database.job_offer_exists(offer)
        ]
        
        logger.info(f"  New offers (not already processed): {len(new_offers)}")
        
        # Appliquer les filtres
        filtered = self.job_filter.filter_offers(new_offers)
        
        return filtered
    
    def _process_offers(self, offers: List[JobOffer]) -> List[ApplicationResult]:
        """Traite les offres: génère CV et lettre"""
        results = []
        
        for i, offer in enumerate(offers, 1):
            logger.info(f"  [{i}/{len(offers)}] {offer.title} @ {offer.company}")
            
            try:
                # Générer le CV
                cv_path = self.cv_generator.generate_optimized_cv(offer)
                logger.info(f"      ✓ CV generated")
                
                # Générer la lettre
                cover_letter_path = self.cover_letter_generator.generate_cover_letter(offer)
                logger.info(f"      ✓ Cover letter generated")
                
                # Créer le résultat
                result = ApplicationResult(
                    job_offer=offer,
                    success=True,
                    error_message=None,
                    cv_path=cv_path,
                    cover_letter_path=cover_letter_path,
                    notification_sent=False
                )
                
                results.append(result)
                
                # Sauvegarder dans la base
                self.database.save_application(result)
                
            except Exception as e:
                logger.error(f"      ✗ Error: {e}")
                
                # Créer un résultat d'erreur
                result = ApplicationResult(
                    job_offer=offer,
                    success=False,
                    error_message=str(e),
                    cv_path=None,
                    cover_letter_path=None,
                    notification_sent=False
                )
                
                results.append(result)
                self.database.log_error(offer.id, "processing_error", str(e))
        
        return results
    
    def _send_report_email(self, html_path: str, total_offers: int, successful: int) -> bool:
        """Envoie le rapport HTML par email"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Lire le fichier HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Job Application Agent <{CANDIDATE_EMAIL}>"
            msg['To'] = NOTIFICATION_EMAIL
            msg['Subject'] = f"📊 Rapport Quotidien - {total_offers} offres trouvées ({successful} prêtes)"
            
            # Corps du message
            body_text = f"""
Bonjour Camille,

Votre rapport quotidien est prêt !

📊 Résumé:
- Offres trouvées: {total_offers}
- Candidatures prêtes: {successful}
- Date: {datetime.now().strftime('%d/%m/%Y à %H:%M')}

Consultez le document HTML ci-joint pour voir toutes les offres qualifiées.

Vous pouvez télécharger votre CV et lettre de motivation optimisés directement depuis le document HTML.

Bonne chance !

---
Agent d'Automatisation de Candidatures
"""
            
            msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Attacher le fichier HTML
            with open(html_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {Path(html_path).name}')
            msg.attach(part)
            
            # Envoyer l'email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(CANDIDATE_EMAIL, CANDIDATE_EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Report email sent to {NOTIFICATION_EMAIL}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending report email: {e}")
            return False


def main():
    """Point d'entrée"""
    import argparse
    parser = argparse.ArgumentParser(description="Daily Job Application Runner")
    parser.add_argument("--test-data", type=str, help="Path to a JSON file with test job offers to bypass scraping.")
    args = parser.parse_args()

    try:
        runner = DailyJobApplicationRunner(test_data_path=args.test_data)
        success = runner.run()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()