"""
Générateur de rapport HTML interactif pour les offres d'emploi avec support des URLs S3
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from utils.models import ApplicationResult
from config import OUTPUT_DIR


class HTMLReporterS3:
    """Génère un rapport HTML interactif avec des liens S3 pour les fichiers"""
    
    def __init__(self):
        logger.info("HTMLReporterS3 initialized")
    
    def generate_report(self, results: List[ApplicationResult], filename: str = None) -> str:
        """
        Génère un rapport HTML interactif avec des liens S3
        
        Args:
            results: Liste des résultats de candidatures
            filename: Nom du fichier (généré automatiquement si None)
            
        Returns:
            Chemin du fichier HTML généré
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"offres_emploi_{timestamp}.html"
        
        output_path = OUTPUT_DIR / filename
        
        logger.info(f"Generating HTML report with S3 links: {output_path}")
        
        # Générer le HTML
        html_content = self._create_html(results)
        
        # Sauvegarder le fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path}")
        return str(output_path)
    
    def _create_html(self, results: List[ApplicationResult]) -> str:
        """Crée le contenu HTML du rapport avec des liens S3"""
        
        # Compter les statistiques
        total = len(results)
        successful = sum(1 for r in results if r.success)
        
        # Générer les lignes du tableau
        table_rows = ""
        for i, result in enumerate(results, 1):
            status_badge = '<span style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px;">✓ Succès</span>' if result.success else '<span style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px;">✗ Erreur</span>'
            
            # Déterminer le drapeau de langue
            lang_flag = "🇫🇷" if result.job_offer.language == "fr" else "🇬🇧"
            
            # Boutons de téléchargement avec URLs S3
            # Les URLs S3 commencent par http:// ou https://
            cv_is_url = result.cv_path and (result.cv_path.startswith('http://') or result.cv_path.startswith('https://'))
            letter_is_url = result.cover_letter_path and (result.cover_letter_path.startswith('http://') or result.cover_letter_path.startswith('https://'))
            
            cv_button = f'<a href="{result.cv_path}" target="_blank" style="background-color: #007bff; color: white; padding: 8px 12px; text-decoration: none; border-radius: 3px; margin-right: 5px; display: inline-block; font-size: 12px; cursor: pointer;">📄 CV</a>' if cv_is_url else '<span style="color: #999; font-size: 12px;">📄 CV</span>'
            
            letter_button = f'<a href="{result.cover_letter_path}" target="_blank" style="background-color: #007bff; color: white; padding: 8px 12px; text-decoration: none; border-radius: 3px; margin-right: 5px; display: inline-block; font-size: 12px; cursor: pointer;">📝 Lettre</a>' if letter_is_url else '<span style="color: #999; font-size: 12px;">📝 Lettre</span>'
            
            apply_button = f'<a href="{result.job_offer.url}" target="_blank" style="background-color: #28a745; color: white; padding: 8px 12px; text-decoration: none; border-radius: 3px; display: inline-block; font-size: 12px;">🔗 Postuler</a>'
            
            table_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{i}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                    <strong>{result.job_offer.title}</strong><br/>
                    <small style="color: #666;">{result.job_offer.company}</small>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{result.job_offer.location}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{result.job_offer.contract_type}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{lang_flag}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{result.job_offer.source}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{status_badge}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">
                    {cv_button}
                    {letter_button}
                    {apply_button}
                </td>
            </tr>
            """
        
        # Créer le HTML complet
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offres d'Emploi - Candidatures Automatisées</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-card .number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            font-size: 14px;
            color: #666;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #ddd;
            font-size: 13px;
            text-transform: uppercase;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .btn {{
            display: inline-block;
            padding: 8px 12px;
            margin-right: 5px;
            border-radius: 3px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.3s ease;
        }}
        
        .btn-primary {{
            background: #007bff;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #0056b3;
        }}
        
        .btn-success {{
            background: #28a745;
            color: white;
        }}
        
        .btn-success:hover {{
            background: #218838;
        }}
        
        .btn-disabled {{
            background: #e9ecef;
            color: #999;
            cursor: not-allowed;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 24px;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
            
            table {{
                font-size: 12px;
            }}
            
            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Offres d'Emploi Qualifiées</h1>
            <p>Candidatures automatisées et personnalisées pour Camille Coupet</p>
            <p style="font-size: 12px; margin-top: 10px;">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{total}</div>
                <div class="label">Offres Trouvées</div>
            </div>
            <div class="stat-card">
                <div class="number">{successful}</div>
                <div class="label">Candidatures Prêtes</div>
            </div>
            <div class="stat-card">
                <div class="number">{total - successful}</div>
                <div class="label">Erreurs</div>
            </div>
        </div>
        
        <div class="content">
            <h2 style="margin-bottom: 20px; color: #333;">📋 Détail des Offres</h2>
            
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 40px;">N°</th>
                            <th style="width: 250px;">Poste & Entreprise</th>
                            <th style="width: 150px;">Lieu</th>
                            <th style="width: 100px;">Contrat</th>
                            <th style="width: 60px;">Langue</th>
                            <th style="width: 100px;">Source</th>
                            <th style="width: 100px;">Statut</th>
                            <th style="width: 250px;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>💡 <strong>Comment utiliser :</strong></p>
            <p>1. 📄 Cliquez sur les boutons "📄 CV" et "📝 Lettre" pour ouvrir/télécharger vos documents optimisés (hébergés sur le cloud)</p>
            <p>2. 🔗 Cliquez sur "🔗 Postuler" pour accéder à l'offre d'emploi</p>
            <p>3. 📤 Soumettez votre candidature directement sur le site de l'offre</p>
            <p style="margin-top: 15px; color: #999;">Agent d'Automatisation de Candidatures • Manus AI</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
