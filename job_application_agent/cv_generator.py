import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from loguru import logger

from utils.models import JobOffer
from utils.ai_helper import AIHelper
from config import CV_BASE_PATH, OUTPUT_DIR, OPENAI_API_KEY


class CVGenerator:
    """Génère des CV optimisés pour chaque offre d'emploi"""
    
    def __init__(self):
        self.ai_helper = AIHelper(api_key=OPENAI_API_KEY)
        self.cv_base = self._load_cv_base()
        logger.info("CVGenerator initialized")
    
    def _load_cv_base(self) -> Dict[str, Any]:
        """Charge le CV de base depuis le fichier JSON"""
        try:
            with open(CV_BASE_PATH, 'r', encoding='utf-8') as f:
                cv_data = json.load(f)
            logger.info("Base CV loaded successfully")
            return cv_data
        except Exception as e:
            logger.error(f"Error loading base CV: {e}")
            raise
    
    def generate_optimized_cv(self, job_offer: JobOffer) -> str:
        """
        Génère un CV optimisé pour une offre spécifique
        
        Args:
            job_offer: Offre d'emploi cible
            
        Returns:
            Chemin du fichier PDF généré
        """
        logger.info(f"Generating optimized CV for: {job_offer.title} at {job_offer.company}")
        
        try:
            # Analyser l'offre d'emploi
            job_analysis = self.ai_helper.analyze_job_offer(
                job_description=f"{job_offer.title}\n\n{job_offer.description}\n\n{job_offer.requirements}"
            )
            
            # Optimiser le CV
            optimized_cv = self.ai_helper.optimize_cv_content(
                cv_data=self.cv_base,
                job_analysis=job_analysis,
                target_language=job_offer.language
            )
            
            # Générer le PDF
            output_filename = self._generate_filename(job_offer)
            output_path = OUTPUT_DIR / output_filename
            
            self._create_pdf(optimized_cv, output_path, job_offer.language)
            
            logger.info(f"CV generated successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating CV: {e}")
            # En cas d'erreur, générer un CV basique
            return self._generate_basic_cv(job_offer)
    
    def _generate_basic_cv(self, job_offer: JobOffer) -> str:
        """Génère un CV basique sans optimisation AI"""
        logger.warning("Generating basic CV without AI optimization")
        
        output_filename = self._generate_filename(job_offer)
        output_path = OUTPUT_DIR / output_filename
        
        self._create_pdf(self.cv_base, output_path, job_offer.language)
        
        return str(output_path)
    
    def _generate_filename(self, job_offer: JobOffer) -> str:
        """Génère un nom de fichier unique pour le CV"""
        # Nettoyer le nom de l'entreprise
        company_clean = "".join(c for c in job_offer.company if c.isalnum() or c in (' ', '-', '_'))
        company_clean = company_clean.replace(' ', '_')[:30]
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"CV_Camille_Coupet_{company_clean}_{timestamp}.pdf"
    
    def _create_pdf(self, cv_data: Dict[str, Any], output_path: Path, language: str = "fr"):
        """
        Crée un PDF à partir des données du CV
        
        Args:
            cv_data: Données structurées du CV
            output_path: Chemin de sortie du PDF
            language: Langue du CV (fr ou en)
        """
        # Créer le document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style pour le nom
        name_style = ParagraphStyle(
            'CustomName',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        
        # Style pour les titres de section
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            spaceBefore=15,
            borderWidth=0,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=5
        )
        
        # Style pour le texte normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#333333')
        )
        
        # Contenu du document
        story = []
        
        # En-tête avec informations personnelles
        personal_info = cv_data.get('personal_info', {})
        
        story.append(Paragraph(personal_info.get('name', 'Camille Coupet'), name_style))
        
        contact_info = f"{personal_info.get('location', 'Lyon, France')} | "
        contact_info += f"{personal_info.get('phone', '+33 6 26 72 76 83')} | "
        contact_info += f"{personal_info.get('email', 'ccoupet02@gmail.com')}"
        
        story.append(Paragraph(contact_info, ParagraphStyle('Contact', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
        story.append(Spacer(1, 0.5*cm))
        
        # Profil
        if language == "fr":
            story.append(Paragraph("PROFIL PROFESSIONNEL", section_style))
        else:
            story.append(Paragraph("PROFESSIONAL PROFILE", section_style))
        
        story.append(Paragraph(cv_data.get('profile', ''), normal_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Expériences professionnelles
        if language == "fr":
            story.append(Paragraph("EXPÉRIENCES PROFESSIONNELLES", section_style))
        else:
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))
        
        for exp in cv_data.get('experiences', []):
            # Titre et entreprise
            exp_title = f"<b>{exp.get('title', '')}</b> - {exp.get('company', '')}"
            story.append(Paragraph(exp_title, normal_style))
            
            # Lieu et période
            exp_details = f"<i>{exp.get('location', '')} | {exp.get('period', '')}</i>"
            story.append(Paragraph(exp_details, ParagraphStyle('ExpDetails', parent=normal_style, fontSize=9, textColor=colors.HexColor('#666666'))))
            story.append(Spacer(1, 0.1*cm))
            
            # Responsabilités
            for resp in exp.get('responsibilities', []):
                story.append(Paragraph(f"• {resp}", normal_style))
            
            story.append(Spacer(1, 0.3*cm))
        
        # Compétences
        if language == "fr":
            story.append(Paragraph("COMPÉTENCES", section_style))
        else:
            story.append(Paragraph("SKILLS", section_style))
        
        for skill in cv_data.get('skills', []):
            story.append(Paragraph(f"• {skill}", normal_style))
        
        story.append(Spacer(1, 0.3*cm))
        
        # Formation
        if language == "fr":
            story.append(Paragraph("FORMATION", section_style))
        else:
            story.append(Paragraph("EDUCATION", section_style))
        
        for edu in cv_data.get('education', []):
            edu_text = f"<b>{edu.get('degree', '')}</b> - {edu.get('school', '')} ({edu.get('year', '')})"
            story.append(Paragraph(edu_text, normal_style))
            story.append(Spacer(1, 0.1*cm))
        
        story.append(Spacer(1, 0.3*cm))
        
        # Langues
        if language == "fr":
            story.append(Paragraph("LANGUES", section_style))
        else:
            story.append(Paragraph("LANGUAGES", section_style))
        
        languages_text = " | ".join([f"{lang.get('language', '')}: {lang.get('level', '')}" for lang in cv_data.get('languages', [])])
        story.append(Paragraph(languages_text, normal_style))
        
        # Construire le PDF
        doc.build(story)
        logger.info(f"PDF created: {output_path}")
