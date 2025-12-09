import os
from typing import Optional, Dict, Any
from openai import OpenAI
from loguru import logger


class AIHelper:
    """Helper pour interactions avec OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-mini"):
        """
        Initialise le client OpenAI
        
        Args:
            api_key: Clé API OpenAI (utilise OPENAI_API_KEY si None)
            model: Modèle à utiliser (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"AIHelper initialized with model: {model}")
    
    def generate_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Génère une completion avec OpenAI
        
        Args:
            prompt: Le prompt utilisateur
            system_message: Le message système
            temperature: Température (0-1)
            max_tokens: Nombre maximum de tokens
            
        Returns:
            La réponse générée
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Generated completion: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    def analyze_job_offer(self, job_description: str) -> Dict[str, Any]:
        """
        Analyse une offre d'emploi et extrait les informations clés
        
        Args:
            job_description: Description complète de l'offre
            
        Returns:
            Dictionnaire avec les informations extraites
        """
        system_message = """Tu es un expert en analyse d'offres d'emploi. 
        Analyse l'offre et extrais les informations clés au format JSON."""
        
        prompt = f"""Analyse cette offre d'emploi et extrais les informations suivantes au format JSON:
- required_skills: liste des compétences requises
- preferred_skills: liste des compétences souhaitées
- experience_years: nombre d'années d'expérience requis (nombre ou null)
- keywords: mots-clés importants pour l'ATS
- company_values: valeurs de l'entreprise mentionnées
- main_responsibilities: principales responsabilités

Offre d'emploi:
{job_description}

Réponds uniquement avec le JSON, sans texte additionnel."""

        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3
            )
            
            # Parser le JSON
            import json
            analysis = json.loads(response)
            logger.info("Job offer analyzed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing job offer: {e}")
            return {
                "required_skills": [],
                "preferred_skills": [],
                "experience_years": None,
                "keywords": [],
                "company_values": [],
                "main_responsibilities": []
            }
    
    def optimize_cv_content(
        self,
        cv_data: Dict[str, Any],
        job_analysis: Dict[str, Any],
        target_language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Optimise le contenu du CV selon l'analyse de l'offre
        
        Args:
            cv_data: Données structurées du CV
            job_analysis: Analyse de l'offre d'emploi
            target_language: Langue cible (fr ou en)
            
        Returns:
            CV optimisé
        """
        system_message = """Tu es un expert en rédaction de CV et optimisation ATS.
        Tu dois adapter le CV pour maximiser les chances de succès."""
        
        prompt = f"""Optimise ce CV pour l'offre d'emploi analysée.

CV actuel (JSON):
{cv_data}

Analyse de l'offre:
{job_analysis}

Langue cible: {target_language}

Instructions:
1. Réorganise les expériences pour mettre en avant les plus pertinentes
2. Adapte les descriptions pour inclure les mots-clés de l'offre
3. Modifie le profil pour matcher l'offre
4. Ajoute les compétences manquantes si pertinentes
5. Si langue = "en", traduis tout le contenu en anglais professionnel
6. Garde le même format JSON

Réponds uniquement avec le JSON du CV optimisé, sans texte additionnel."""

        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.5,
                max_tokens=3000
            )
            
            import json
            optimized_cv = json.loads(response)
            logger.info(f"CV optimized for language: {target_language}")
            return optimized_cv
            
        except Exception as e:
            logger.error(f"Error optimizing CV: {e}")
            return cv_data
    
    def generate_cover_letter(
        self,
        job_offer: Dict[str, Any],
        cv_data: Dict[str, Any],
        reference_letter: str,
        target_language: str = "fr"
    ) -> str:
        """
        Génère une lettre de motivation personnalisée
        
        Args:
            job_offer: Informations sur l'offre d'emploi
            cv_data: Données du CV
            reference_letter: Lettre de motivation de référence
            target_language: Langue cible (fr ou en)
            
        Returns:
            Lettre de motivation générée
        """
        system_message = """Tu es un expert en rédaction de lettres de motivation.
        Tu dois créer une lettre personnalisée, professionnelle et convaincante."""
        
        prompt = f"""Génère une lettre de motivation personnalisée pour cette candidature.

Offre d'emploi:
- Titre: {job_offer.get('title')}
- Entreprise: {job_offer.get('company')}
- Description: {job_offer.get('description')}

Profil du candidat:
{cv_data.get('profile')}

Expériences clés:
{cv_data.get('experiences')[:2]}

Lettre de motivation de référence (pour le style):
{reference_letter}

Langue: {target_language}

Instructions:
1. Inspire-toi du style et du ton de la lettre de référence
2. Personnalise pour l'offre et l'entreprise spécifiques
3. Mets en avant les expériences les plus pertinentes du CV
4. Reste authentique et motivé
5. Maximum 1 page (environ 300-400 mots)
6. Si langue = "en", écris en anglais professionnel
7. Structure: introduction, corps (2-3 paragraphes), conclusion

Génère uniquement la lettre, sans titre ni métadonnées."""

        try:
            cover_letter = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.7,
                max_tokens=800
            )
            
            logger.info(f"Cover letter generated for {job_offer.get('company')}")
            return cover_letter.strip()
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return ""
    
    def detect_job_domain(self, job_title: str, job_description: str) -> bool:
        """
        Détecte si un poste est lié à la communication/événementiel
        
        Args:
            job_title: Titre du poste
            job_description: Description du poste
            
        Returns:
            True si le poste est pertinent, False sinon
        """
        system_message = """Tu es un expert en classification d'offres d'emploi.
        Réponds uniquement par 'OUI' ou 'NON'."""
        
        prompt = f"""Ce poste est-il lié à la communication, l'événementiel, le marketing événementiel, 
ou la gestion de projets événementiels ?

Titre: {job_title}
Description: {job_description[:500]}

Réponds uniquement par 'OUI' ou 'NON'."""

        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.1
            )
            
            is_relevant = response.strip().upper() == "OUI"
            logger.debug(f"Job domain detection for '{job_title}': {is_relevant}")
            return is_relevant
            
        except Exception as e:
            logger.error(f"Error detecting job domain: {e}")
            return False
