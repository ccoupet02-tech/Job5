from abc import ABC, abstractmethod
from typing import List, Optional
from selenium import webdriver
from loguru import logger

from utils.models import JobOffer
from utils.web_utils import setup_selenium_driver, sleep_random
from config import HEADLESS_BROWSER, CHROME_PROFILE_DIR


class BaseScraper(ABC):
    """Classe abstraite de base pour tous les scrapers"""
    
    def __init__(self, name: str, use_selenium: bool = False):
        """
        Initialise le scraper
        
        Args:
            name: Nom du scraper
            use_selenium: Utiliser Selenium ou requests
        """
        self.name = name
        self.use_selenium = use_selenium
        self.driver: Optional[webdriver.Chrome] = None
        logger.info(f"Initializing {name} scraper")
    
    def setup_driver(self):
        """Configure le WebDriver Selenium"""
        if self.use_selenium and not self.driver:
            self.driver = setup_selenium_driver(
                headless=HEADLESS_BROWSER,
                user_data_dir=str(CHROME_PROFILE_DIR / self.name)
            )
            logger.info(f"WebDriver setup for {self.name}")
    
    def close_driver(self):
        """Ferme le WebDriver proprement"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info(f"WebDriver closed for {self.name}")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    @abstractmethod
    def scrape(self, max_offers: int = 50) -> List[JobOffer]:
        """
        Méthode abstraite pour scraper les offres
        
        Args:
            max_offers: Nombre maximum d'offres à récupérer
            
        Returns:
            Liste d'offres d'emploi
        """
        raise NotImplementedError("Subclasses must implement scrape()")
    
    @abstractmethod
    def parse_job_offer(self, element) -> Optional[JobOffer]:
        """
        Parse un élément HTML en objet JobOffer
        
        Args:
            element: Element HTML à parser
            
        Returns:
            JobOffer ou None si erreur
        """
        raise NotImplementedError("Subclasses must implement parse_job_offer()")
    
    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()
