from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import hashlib


class JobOffer(BaseModel):
    """Modèle représentant une offre d'emploi"""
    
    id: str = Field(default="", description="Hash unique de l'offre")
    title: str = Field(..., description="Titre du poste")
    company: str = Field(..., description="Nom de l'entreprise")
    location: str = Field(..., description="Localisation du poste")
    contract_type: str = Field(..., description="Type de contrat (CDI, CDD, etc.)")
    description: str = Field(..., description="Description complète du poste")
    requirements: str = Field(default="", description="Exigences et qualifications")
    url: str = Field(..., description="URL de l'offre")
    source: str = Field(..., description="Source de l'offre (indeed, linkedin, etc.)")
    language: str = Field(default="fr", description="Langue de l'offre (fr, en)")
    posted_date: Optional[datetime] = Field(default=None, description="Date de publication")
    application_type: str = Field(..., description="Type de candidature (email, easy_apply, form)")
    application_url: str = Field(..., description="URL ou email pour candidater")
    scraped_at: datetime = Field(default_factory=datetime.now, description="Date de scraping")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = self.generate_id()
    
    def generate_id(self) -> str:
        """Génère un ID unique basé sur titre + entreprise + lieu"""
        unique_string = f"{self.title}_{self.company}_{self.location}".lower()
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ApplicationResult(BaseModel):
    """Modèle représentant le résultat d'une candidature"""
    
    job_offer: JobOffer
    success: bool = Field(..., description="Succès de la candidature")
    error_message: Optional[str] = Field(default=None, description="Message d'erreur si échec")
    cv_path: Optional[str] = Field(default=None, description="Chemin du CV généré")
    cover_letter_path: Optional[str] = Field(default=None, description="Chemin de la lettre de motivation")
    applied_at: datetime = Field(default_factory=datetime.now, description="Date de candidature")
    notification_sent: bool = Field(default=False, description="Notification envoyée")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CVData(BaseModel):
    """Modèle représentant les données structurées du CV"""
    
    personal_info: dict = Field(..., description="Informations personnelles")
    profile: str = Field(..., description="Profil professionnel")
    experiences: List[dict] = Field(..., description="Expériences professionnelles")
    skills: List[str] = Field(..., description="Compétences")
    education: List[dict] = Field(..., description="Formations")
    languages: List[dict] = Field(..., description="Langues")
    volunteer: Optional[List[dict]] = Field(default=None, description="Bénévolat")
