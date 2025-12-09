from typing import List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from loguru import logger

from .base_scraper import BaseScraper
from utils.models import JobOffer
from utils.web_utils import sleep_random, get_user_agent
from config import SCRAPING_DELAY_MIN, SCRAPING_DELAY_MAX


class FranceTravailScraper(BaseScraper):
    """Scraper pour France Travail (ex-Pôle Emploi)"""
    
    def __init__(self):
        super().__init__(name="france_travail", use_selenium=False)
        self.base_url = "https://candidat.francetravail.fr"
    
    def scrape(self, max_offers: int = 50) -> List[JobOffer]:
        """
        Scrape les offres d'emploi depuis France Travail
        
        Args:
            max_offers: Nombre maximum d'offres à récupérer
            
        Returns:
            Liste d'offres d'emploi
        """
        offers = []
        
        # Recherches multiples
        search_queries = [
            "communication",
            "événementiel",
            "chargé de communication",
            "event manager"
        ]
        
        locations = ["Lyon", ""]  # Lyon ou toute la France (pour remote)
        
        for query in search_queries:
            for location in locations:
                if len(offers) >= max_offers:
                    break
                
                logger.info(f"Searching France Travail for: {query} in {location or 'all France'}")
                
                try:
                    page_offers = self._scrape_search_page(query, location, max_offers - len(offers))
                    offers.extend(page_offers)
                    sleep_random(SCRAPING_DELAY_MIN, SCRAPING_DELAY_MAX)
                    
                except Exception as e:
                    logger.error(f"Error scraping France Travail for '{query}': {e}")
                    continue
        
        logger.info(f"France Travail scraper found {len(offers)} offers")
        return offers[:max_offers]
    
    def _scrape_search_page(self, query: str, location: str, max_results: int) -> List[JobOffer]:
        """Scrape une page de résultats de recherche"""
        offers = []
        
        # URL de recherche France Travail
        search_url = f"{self.base_url}/offres/recherche"
        
        params = {
            "motsCles": query,
            "lieuRecherche": location,
            "rayon": "30",  # 30 km autour de Lyon
            "tri": "0"  # Tri par date
        }
        
        headers = {
            "User-Agent": get_user_agent(),
            "Accept-Language": "fr-FR,fr;q=0.9"
        }
        
        try:
            response = requests.get(
                search_url,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Trouver les offres (structure peut varier)
            job_cards = soup.find_all("li", class_="result")
            
            if not job_cards:
                # Essayer une autre structure
                job_cards = soup.find_all("article", class_="card")
            
            logger.debug(f"Found {len(job_cards)} job cards on France Travail")
            
            for card in job_cards[:max_results]:
                offer = self.parse_job_offer(card)
                if offer:
                    offers.append(offer)
            
        except Exception as e:
            logger.error(f"Error fetching France Travail search page: {e}")
        
        return offers
    
    def parse_job_offer(self, element) -> Optional[JobOffer]:
        """Parse une carte d'offre France Travail"""
        try:
            # Titre
            title_elem = element.find("h2") or element.find("h3")
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Entreprise
            company_elem = element.find("span", class_="company") or element.find("p", class_="company")
            company = company_elem.get_text(strip=True) if company_elem else "Non spécifié"
            
            # Localisation
            location_elem = element.find("span", class_="location") or element.find("p", class_="location")
            location = location_elem.get_text(strip=True) if location_elem else "Non spécifié"
            
            # URL
            link_elem = element.find("a")
            if not link_elem or not link_elem.get("href"):
                return None
            
            job_url = link_elem["href"]
            if not job_url.startswith("http"):
                job_url = self.base_url + job_url
            
            # Description
            description_elem = element.find("p", class_="description")
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Type de contrat
            contract_elem = element.find("span", class_="contract") or element.find("p", class_="contract")
            contract_type = "Non spécifié"
            if contract_elem:
                contract_text = contract_elem.get_text(strip=True).upper()
                if "CDI" in contract_text:
                    contract_type = "CDI"
                elif "CDD" in contract_text:
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
                source="france_travail",
                language="fr",
                application_type="form",
                application_url=job_url,
                scraped_at=datetime.now()
            )
            
            logger.debug(f"Parsed France Travail offer: {title} at {company}")
            return offer
            
        except Exception as e:
            logger.error(f"Error parsing France Travail job offer: {e}")
            return None
