from typing import List
from loguru import logger
from langdetect import detect

from utils.models import JobOffer
from utils.ai_helper import AIHelper
from config import (
    LOCATION_KEYWORDS,
    CONTRACT_TYPES,
    EXCLUDE_KEYWORDS,
    OPENAI_API_KEY
)


class JobFilter:
    """Filtre les offres d'emploi selon les critères définis"""
    
    def __init__(self):
        self.ai_helper = AIHelper(api_key=OPENAI_API_KEY)
        logger.info("JobFilter initialized")
    
    def filter_offers(self, offers: List[JobOffer]) -> List[JobOffer]:
        """
        Filtre une liste d'offres selon tous les critères
        
        Args:
            offers: Liste d'offres à filtrer
            
        Returns:
            Liste d'offres filtrées
        """
        filtered = []
        
        for offer in offers:
            logger.debug(f"Filtering offer: {offer.title} at {offer.company}")
            
            # Vérifier chaque critère
            if not self.check_location(offer):
                logger.debug(f"Rejected: location '{offer.location}' not matching")
                continue
            
            if not self.check_contract_type(offer):
                logger.debug(f"Rejected: contract type '{offer.contract_type}' not matching")
                continue
            
            if not self.check_exclusions(offer):
                logger.debug(f"Rejected: contains excluded keywords")
                continue
            
            if not self.check_domain(offer):
                logger.debug(f"Rejected: not in communication/événementiel domain")
                continue
            
            # Détecter la langue
            offer.language = self.detect_language(offer)
            
            # Accepter seulement français et anglais
            if offer.language not in ["fr", "en"]:
                logger.debug(f"Rejected: language '{offer.language}' not supported")
                continue
            
            logger.info(f"✓ Offer accepted: {offer.title} at {offer.company}")
            filtered.append(offer)
        
        logger.info(f"Filtered {len(filtered)}/{len(offers)} offers")
        return filtered
    
    def check_location(self, offer: JobOffer) -> bool:
        """
        Vérifie si la localisation correspond aux critères
        
        Args:
            offer: Offre à vérifier
            
        Returns:
            True si localisation OK, False sinon
        """
        location_lower = offer.location.lower()
        
        for keyword in LOCATION_KEYWORDS:
            if keyword in location_lower:
                return True
        
        return False
    
    def check_contract_type(self, offer: JobOffer) -> bool:
        """
        Vérifie si le type de contrat correspond aux critères
        
        Args:
            offer: Offre à vérifier
            
        Returns:
            True si type de contrat OK, False sinon
        """
        contract_upper = offer.contract_type.upper()
        
        # Si non spécifié, on accepte (sera vérifié manuellement)
        if contract_upper == "NON SPÉCIFIÉ":
            return True
        
        for contract_type in CONTRACT_TYPES:
            if contract_type in contract_upper:
                return True
        
        return False
    
    def check_exclusions(self, offer: JobOffer) -> bool:
        """
        Vérifie qu'il n'y a pas de mots-clés exclus
        
        Args:
            offer: Offre à vérifier
            
        Returns:
            True si pas d'exclusions, False si exclusions trouvées
        """
        # Combiner titre et description
        full_text = f"{offer.title} {offer.description}".lower()
        
        for keyword in EXCLUDE_KEYWORDS:
            if keyword in full_text:
                return False
        
        return True
    
    def check_domain(self, offer: JobOffer) -> bool:
        """
        Vérifie si le poste est lié à la communication/événementiel
        
        Args:
            offer: Offre à vérifier
            
        Returns:
            True si domaine OK, False sinon
        """
        # Vérification rapide par mots-clés
        title_lower = offer.title.lower()
        desc_lower = offer.description.lower()
        
        domain_keywords = [
            "communication", "événementiel", "event", "marketing",
            "chargé de communication", "chargée de communication",
            "event manager", "project manager", "coordinateur",
            "coordinatrice", "relations publiques", "rp"
        ]
        
        # Si un mot-clé est dans le titre, accepter directement
        for keyword in domain_keywords:
            if keyword in title_lower:
                return True
        
        # Sinon, utiliser l'AI pour une analyse plus fine
        try:
            is_relevant = self.ai_helper.detect_job_domain(
                job_title=offer.title,
                job_description=offer.description
            )
            return is_relevant
        except Exception as e:
            logger.error(f"Error in AI domain detection: {e}")
            # En cas d'erreur AI, vérifier dans la description
            for keyword in domain_keywords:
                if keyword in desc_lower:
                    return True
            return False
    
    def detect_language(self, offer: JobOffer) -> str:
        """
        Détecte la langue de l'offre
        
        Args:
            offer: Offre à analyser
            
        Returns:
            Code langue (fr, en, etc.)
        """
        try:
            # Combiner titre et description pour la détection
            text = f"{offer.title} {offer.description}"
            
            # Détecter la langue
            lang = detect(text)
            
            logger.debug(f"Detected language: {lang} for '{offer.title}'")
            return lang
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            # Par défaut, français
            return "fr"
