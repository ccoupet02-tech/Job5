import pandas as pd
from datetime import datetime
from pathlib import Path
from loguru import logger

from .database import ApplicationDatabase
from config import OUTPUT_DIR


class ApplicationExporter:
    """Exporte les candidatures en CSV/Excel"""
    
    def __init__(self):
        self.db = ApplicationDatabase()
        logger.info("ApplicationExporter initialized")
    
    def export_to_csv(self, output_path: str = None) -> str:
        """
        Exporte toutes les candidatures en CSV
        
        Args:
            output_path: Chemin de sortie (généré automatiquement si None)
            
        Returns:
            Chemin du fichier généré
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_DIR / f"candidatures_{timestamp}.csv"
        
        logger.info(f"Exporting applications to CSV: {output_path}")
        
        try:
            # Récupérer les données
            applications = self.db.get_all_applications()
            
            if not applications:
                logger.warning("No applications to export")
                return None
            
            # Créer un DataFrame
            df = pd.DataFrame(applications)
            
            # Sélectionner et renommer les colonnes
            columns_mapping = {
                'applied_at': 'Date',
                'job_title': 'Poste',
                'company': 'Entreprise',
                'location': 'Lieu',
                'contract_type': 'Type de contrat',
                'url': 'Lien offre',
                'source': 'Source',
                'language': 'Langue',
                'application_type': 'Type de candidature',
                'success': 'Succès',
                'error_message': 'Erreur',
                'cv_path': 'Chemin CV',
                'cover_letter_path': 'Chemin lettre'
            }
            
            df = df[list(columns_mapping.keys())]
            df = df.rename(columns=columns_mapping)
            
            # Formater la date
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Formater le succès
            df['Succès'] = df['Succès'].map({1: 'Oui', 0: 'Non'})
            
            # Exporter
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"CSV exported successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None
    
    def export_to_excel(self, output_path: str = None) -> str:
        """
        Exporte toutes les candidatures en Excel
        
        Args:
            output_path: Chemin de sortie (généré automatiquement si None)
            
        Returns:
            Chemin du fichier généré
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_DIR / f"candidatures_{timestamp}.xlsx"
        
        logger.info(f"Exporting applications to Excel: {output_path}")
        
        try:
            # Récupérer les données
            applications = self.db.get_all_applications()
            
            if not applications:
                logger.warning("No applications to export")
                return None
            
            # Créer un DataFrame
            df = pd.DataFrame(applications)
            
            # Sélectionner et renommer les colonnes
            columns_mapping = {
                'applied_at': 'Date',
                'job_title': 'Poste',
                'company': 'Entreprise',
                'location': 'Lieu',
                'contract_type': 'Type de contrat',
                'url': 'Lien offre',
                'source': 'Source',
                'language': 'Langue',
                'application_type': 'Type de candidature',
                'success': 'Succès',
                'error_message': 'Erreur',
                'cv_path': 'Chemin CV',
                'cover_letter_path': 'Chemin lettre'
            }
            
            df = df[list(columns_mapping.keys())]
            df = df.rename(columns=columns_mapping)
            
            # Formater la date
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Formater le succès
            df['Succès'] = df['Succès'].map({1: 'Oui', 0: 'Non'})
            
            # Exporter avec formatage
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Candidatures', index=False)
                
                # Ajuster la largeur des colonnes
                worksheet = writer.sheets['Candidatures']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            logger.info(f"Excel exported successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None
    
    def generate_report(self) -> str:
        """
        Génère un rapport textuel des statistiques
        
        Returns:
            Rapport sous forme de texte
        """
        stats = self.db.get_statistics()
        
        report = f"""
=== RAPPORT DES CANDIDATURES ===
Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}

STATISTIQUES GLOBALES:
- Total de candidatures: {stats['total']}
- Candidatures réussies: {stats['successful']}
- Candidatures échouées: {stats['failed']}
- Taux de succès: {stats['success_rate']:.1f}%

PAR SOURCE:
"""
        
        for source, count in stats['by_source'].items():
            report += f"- {source}: {count}\n"
        
        report += "\nPAR LANGUE:\n"
        for lang, count in stats['by_language'].items():
            lang_name = "Français" if lang == "fr" else "Anglais" if lang == "en" else lang
            report += f"- {lang_name}: {count}\n"
        
        report += "\n=== FIN DU RAPPORT ===\n"
        
        return report
