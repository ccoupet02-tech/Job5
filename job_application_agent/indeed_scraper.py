from typing import List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from loguru import logger

from .base_scraper import BaseScraper
from utils.models import JobOffer
from utils.web_utils import sleep_random, get_user_agent
from config import SCRAPING_DELAY_MIN, SCRAPING_DELAY_MAX


class IndeedScraper(BaseScraper):
    """Scraper pour Indeed.fr"""
    
    def __init__(self):
        super().__init__(name="indeed", use_selenium=False)
        self.base_url = "https://fr.indeed.com"
    
    def scrape(self, max_offers: int = 50) -> List[JobOffer]:
        """
        Scrape les offres d'emploi depuis Indeed
        
        Args:
            max_offers: Nombre maximum d'offres à récupérer
            
        Returns:
            Liste d'offres d'emploi
        """
        offers = []
        
        # Recherches multiples pour couvrir les critères
        search_queries = [
            "communication Lyon",
            "événementiel Lyon",
            "chargé communication Lyon",
            "event manager Lyon",
            "communication remote",
            "événementiel remote"
        ]
        
        for query in search_queries:
            if len(offers) >= max_offers:
                break
            
            logger.info(f"Searching Indeed for: {query}")
            
            try:
                page_offers = self._scrape_search_page(query, max_offers - len(offers))
                offers.extend(page_offers)
                sleep_random(SCRAPING_DELAY_MIN, SCRAPING_DELAY_MAX)
                
            except Exception as e:
                logger.error(f"Error scraping Indeed for '{query}': {e}")
                continue
        
        logger.info(f"Indeed scraper found {len(offers)} offers")
        return offers[:max_offers]
    
    def _scrape_search_page(self, query: str, max_results: int) -> List[JobOffer]:
        """Scrape une page de résultats de recherche"""
        offers = []
        
        # Paramètres de recherche
        params = {
            "q": query,
            "l": "",  # Localisation gérée dans la requête
            "sort": "date",
            "fromage": "7"  # Offres des 7 derniers jours
        }
        
        headers = {
            "User-Agent": get_user_agent(),
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
        }
        
        try:
            # Requête
            response = requests.get(
                f"{self.base_url}/jobs",
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Parser le HTML
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Trouver les cartes d'offres
            job_cards = soup.find_all("div", class_="job_seen_beacon")
            
            logger.debug(f"Found {len(job_cards)} job cards on page")
            
            for card in job_cards[:max_results]:
                offer = self.parse_job_offer(card)
                if offer:
                    offers.append(offer)
            
        except Exception as e:
            logger.error(f"Error fetching Indeed search page: {e}")
        
        return offers
    
    def parse_job_offer(self, element) -> Optional[JobOffer]:
        """Parse une carte d'offre Indeed"""
        try:
            # Titre
            title_elem = element.find("h2", class_="jobTitle")
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Entreprise
            company_elem = element.find("span", {"data-testid": "company-name"})
            company = company_elem.get_text(strip=True) if company_elem else "Non spécifié"
            
            # Localisation
            location_elem = element.find("div", {"data-testid": "text-location"})
            location = location_elem.get_text(strip=True) if location_elem else "Non spécifié"
            
            # URL
            link_elem = title_elem.find("a")
            if not link_elem or not link_elem.get("href"):
                return None
            job_url = self.base_url + link_elem["href"]
            
            # Description courte
            description_elem = element.find("div", class_="job-snippet")
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Type de contrat (essayer de détecter dans le texte)
            full_text = element.get_text().upper()
            contract_type = "Non spécifié"
            if "CDI" in full_text:
                contract_type = "CDI"
            elif "CDD" in full_text:
                contract_type = "CDD"
            
            # Créer l'offre
            offer = JobOffer(
                title=title,
                company=company,
                location=location,
                contract_type=contract_type,
                description=description,
                requirements="",
                url=job_url,
                source="indeed",
                language="fr",  # Sera détecté par le filtre
                application_type="form",  # Indeed utilise généralement des formulaires
                application_url=job_url,
                scraped_at=datetime.now()
            )
            
            logger.debug(f"Parsed offer: {title} at {company}")
            return offer
            
        except Exception as e:
            logger.error(f"Error parsing Indeed job offer: {e}")
            return None
