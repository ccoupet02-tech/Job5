from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from loguru import logger

from utils.models import JobOffer
from utils.ai_helper import AIHelper
from config import COVER_LETTER_TEMPLATE_PATH, OUTPUT_DIR, OPENAI_API_KEY, CV_BASE_PATH
import json


class CoverLetterGenerator:
    """Génère des lettres de motivation personnalisées"""
    
    def __init__(self):
        self.ai_helper = AIHelper(api_key=OPENAI_API_KEY)
        self.template = self._load_template()
        self.cv_data = self._load_cv_data()
        logger.info("CoverLetterGenerator initialized")
    
    def _load_template(self) -> str:
        """Charge le template de lettre de motivation"""
        try:
            with open(COVER_LETTER_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                template = f.read()
            logger.info("Cover letter template loaded")
            return template
        except Exception as e:
            logger.error(f"Error loading cover letter template: {e}")
            return ""
    
    def _load_cv_data(self) -> dict:
        """Charge les données du CV"""
        try:
            with open(CV_BASE_PATH, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
            return cv_data
        except Exception as e:
            logger.error(f"Error loading CV data: {e}")
            return {}
    
    def generate_cover_letter(self, job_offer: JobOffer) -> str:
        """
        Génère une lettre de motivation pour une offre
        
        Args:
            job_offer: Offre d'emploi cible
            
        Returns:
            Chemin du fichier PDF généré
        """
        logger.info(f"Generating cover letter for: {job_offer.title} at {job_offer.company}")
        
        try:
            # Préparer les informations de l'offre
            job_info = {
                "title": job_offer.title,
                "company": job_offer.company,
                "description": job_offer.description,
                "requirements": job_offer.requirements
            }
            
            # Générer le contenu avec AI
            letter_content = self.ai_helper.generate_cover_letter(
                job_offer=job_info,
                cv_data=self.cv_data,
                reference_letter=self.template,
                target_language=job_offer.language
            )
            
            # Générer le PDF
            output_filename = self._generate_filename(job_offer)
            output_path = OUTPUT_DIR / output_filename
            
            self._create_pdf(letter_content, job_offer, output_path, job_offer.language)
            
            logger.info(f"Cover letter generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            # En cas d'erreur, utiliser le template de base
            return self._generate_basic_letter(job_offer)
    
    def _generate_basic_letter(self, job_offer: JobOffer) -> str:
        """Génère une lettre basique en cas d'erreur AI"""
        logger.warning("Generating basic cover letter without AI")
        
        output_filename = self._generate_filename(job_offer)
        output_path = OUTPUT_DIR / output_filename
        
        # Utiliser le template avec des remplacements basiques
        basic_content = self.template.replace(
            "chargée de projets privatisations et traiteur",
            job_offer.title.lower()
        ).replace(
            "Toast / HEAT",
            job_offer.company
        )
        
        self._create_pdf(basic_content, job_offer, output_path, job_offer.language)
        
        return str(output_path)
    
    def _generate_filename(self, job_offer: JobOffer) -> str:
        """Génère un nom de fichier unique"""
        company_clean = "".join(c for c in job_offer.company if c.isalnum() or c in (' ', '-', '_'))
        company_clean = company_clean.replace(' ', '_')[:30]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"Lettre_Motivation_{company_clean}_{timestamp}.pdf"
    
    def _create_pdf(self, content: str, job_offer: JobOffer, output_path: Path, language: str = "fr"):
        """
        Crée un PDF de lettre de motivation
        
        Args:
            content: Contenu de la lettre
            job_offer: Offre d'emploi
            output_path: Chemin de sortie
            language: Langue de la lettre
        """
        # Créer le document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style pour l'en-tête (coordonnées)
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT
        )
        
        # Style pour le destinataire
        recipient_style = ParagraphStyle(
            'Recipient',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_RIGHT
        )
        
        # Style pour le corps de la lettre
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT,
            spaceAfter=12
        )
        
        # Contenu
        story = []
        
        # En-tête avec coordonnées
        story.append(Paragraph("Camille Coupet", header_style))
        story.append(Paragraph("Lyon, France", header_style))
        story.append(Paragraph("+33 6 26 72 76 83", header_style))
        story.append(Paragraph("ccoupet02@gmail.com", header_style))
        story.append(Spacer(1, 1*cm))
        
        # Destinataire
        story.append(Paragraph(job_offer.company, recipient_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Date et lieu
        date_str = datetime.now().strftime("%d/%m/%Y")
        if language == "fr":
            date_text = f"Lyon, le {date_str}"
        else:
            date_text = f"Lyon, {datetime.now().strftime('%B %d, %Y')}"
        
        story.append(Paragraph(date_text, header_style))
        story.append(Spacer(1, 1*cm))
        
        # Objet
        if language == "fr":
            objet = f"<b>Objet : Candidature {job_offer.title}</b>"
        else:
            objet = f"<b>Subject: Application for {job_offer.title}</b>"
        
        story.append(Paragraph(objet, body_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Corps de la lettre
        # Diviser le contenu en paragraphes
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.3*cm))
        
        # Construire le PDF
        doc.build(story)
        logger.info(f"Cover letter PDF created: {output_path}")
