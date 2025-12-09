import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
from loguru import logger

from utils.models import JobOffer
from config import (
    CANDIDATE_EMAIL,
    CANDIDATE_EMAIL_PASSWORD,
    NOTIFICATION_EMAIL,
    SMTP_SERVER,
    SMTP_PORT,
    CANDIDATE_INFO
)


class EmailSender:
    """Gère l'envoi d'emails pour les candidatures et notifications"""
    
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.sender_email = CANDIDATE_EMAIL
        self.sender_password = CANDIDATE_EMAIL_PASSWORD
        logger.info("EmailSender initialized")
    
    def send_application_email(
        self,
        job_offer: JobOffer,
        cv_path: str,
        cover_letter_path: str,
        recipient_email: Optional[str] = None
    ) -> bool:
        """
        Envoie un email de candidature
        
        Args:
            job_offer: Offre d'emploi
            cv_path: Chemin du CV
            cover_letter_path: Chemin de la lettre de motivation
            recipient_email: Email du destinataire (si différent de application_url)
            
        Returns:
            True si succès, False sinon
        """
        # Déterminer l'email du destinataire
        to_email = recipient_email or job_offer.application_url
        
        # Vérifier que c'est bien un email
        if not "@" in to_email:
            logger.error(f"Invalid email address: {to_email}")
            return False
        
        logger.info(f"Sending application email to {to_email} for {job_offer.title}")
        
        try:
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = f"{CANDIDATE_INFO['name']} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = self._generate_subject(job_offer)
            
            # Corps de l'email
            body = self._generate_email_body(job_offer)
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Attacher le CV
            self._attach_file(msg, cv_path, "CV_Camille_Coupet.pdf")
            
            # Attacher la lettre de motivation
            self._attach_file(msg, cover_letter_path, "Lettre_Motivation_Camille_Coupet.pdf")
            
            # Envoyer l'email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Application email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending application email: {e}")
            return False
    
    def send_notification_email(
        self,
        job_offer: JobOffer,
        cv_path: str,
        cover_letter_path: str,
        application_success: bool,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Envoie un email de notification à l'utilisateur
        
        Args:
            job_offer: Offre d'emploi
            cv_path: Chemin du CV
            cover_letter_path: Chemin de la lettre
            application_success: Succès de la candidature
            error_message: Message d'erreur si échec
            
        Returns:
            True si succès, False sinon
        """
        logger.info(f"Sending notification email to {NOTIFICATION_EMAIL}")
        
        try:
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = f"Job Application Agent <{self.sender_email}>"
            msg['To'] = NOTIFICATION_EMAIL
            
            if application_success:
                msg['Subject'] = f"✅ Candidature envoyée - {job_offer.title} chez {job_offer.company}"
            else:
                msg['Subject'] = f"❌ Échec candidature - {job_offer.title} chez {job_offer.company}"
            
            # Corps de l'email
            body = self._generate_notification_body(
                job_offer,
                application_success,
                error_message
            )
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Attacher les documents
            if Path(cv_path).exists():
                self._attach_file(msg, cv_path)
            
            if Path(cover_letter_path).exists():
                self._attach_file(msg, cover_letter_path)
            
            # Envoyer
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info("Notification email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification email: {e}")
            return False
    
    def _generate_subject(self, job_offer: JobOffer) -> str:
        """Génère l'objet de l'email de candidature"""
        if job_offer.language == "en":
            return f"Application for {job_offer.title} - Camille Coupet"
        else:
            return f"Candidature {job_offer.title} - Camille Coupet"
    
    def _generate_email_body(self, job_offer: JobOffer) -> str:
        """Génère le corps de l'email de candidature"""
        if job_offer.language == "en":
            body = f"""Dear Hiring Manager,

I am writing to express my interest in the {job_offer.title} position at {job_offer.company}.

With my extensive experience in communication and event management, particularly my recent role as Communication & Marketing Coordinator at THALES in Orlando, I believe I would be a valuable addition to your team.

Please find attached my resume and cover letter for your consideration.

I would welcome the opportunity to discuss how my skills and experience align with your needs.

Thank you for your time and consideration.

Best regards,
Camille Coupet
{CANDIDATE_INFO['phone']}
{CANDIDATE_INFO['email']}"""
        else:
            body = f"""Madame, Monsieur,

Je me permets de vous adresser ma candidature pour le poste de {job_offer.title} au sein de {job_offer.company}.

Forte de mon expérience en communication et événementiel, notamment en tant que Coordinatrice Communication & Marketing chez THALES à Orlando, je suis convaincue de pouvoir apporter une réelle valeur ajoutée à votre équipe.

Vous trouverez ci-joint mon CV ainsi qu'une lettre de motivation détaillant mon parcours et mes motivations.

Je reste à votre disposition pour un entretien afin d'échanger sur ma candidature.

Dans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

Cordialement,
Camille Coupet
{CANDIDATE_INFO['phone']}
{CANDIDATE_INFO['email']}"""
        
        return body
    
    def _generate_notification_body(
        self,
        job_offer: JobOffer,
        success: bool,
        error_message: Optional[str]
    ) -> str:
        """Génère le corps de l'email de notification"""
        from datetime import datetime
        
        if success:
            body = f"""Bonjour Camille,

Une candidature a été envoyée avec succès !

📋 Poste: {job_offer.title}
🏢 Entreprise: {job_offer.company}
📍 Lieu: {job_offer.location}
💼 Type de contrat: {job_offer.contract_type}
🔗 Lien: {job_offer.url}
📅 Date: {datetime.now().strftime("%d/%m/%Y à %H:%M")}
🌐 Langue: {"Français" if job_offer.language == "fr" else "Anglais"}

Type de candidature: {job_offer.application_type}

Les documents envoyés sont joints à cet email.

Bonne chance !

---
Job Application Agent
"""
        else:
            body = f"""Bonjour Camille,

Une erreur s'est produite lors de l'envoi d'une candidature.

📋 Poste: {job_offer.title}
🏢 Entreprise: {job_offer.company}
📍 Lieu: {job_offer.location}
🔗 Lien: {job_offer.url}
📅 Date: {datetime.now().strftime("%d/%m/%Y à %H:%M")}

❌ Erreur: {error_message or "Erreur inconnue"}

Type de candidature: {job_offer.application_type}

Vous pouvez candidater manuellement en utilisant les documents joints.

---
Job Application Agent
"""
        
        return body
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str, filename: Optional[str] = None):
        """Attache un fichier au message"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.warning(f"File not found: {file_path}")
                return
            
            with open(path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='pdf')
            
            attachment_name = filename or path.name
            attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
            msg.attach(attachment)
            
            logger.debug(f"File attached: {attachment_name}")
            
        except Exception as e:
            logger.error(f"Error attaching file {file_path}: {e}")
