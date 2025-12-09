"""
Module pour gérer l'upload des fichiers générés vers un service de stockage cloud (S3)
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Optional
from loguru import logger


class FileUploader:
    """Gère l'upload des fichiers vers S3 via manus-upload-file"""
    
    def __init__(self):
        logger.info("FileUploader initialized")
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Téléverse un fichier vers S3 et retourne l'URL publique
        
        Args:
            file_path: Chemin du fichier à téléverser
            
        Returns:
            URL publique du fichier, ou None en cas d'erreur
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            logger.info(f"Uploading file: {file_path}")
            
            # Utiliser manus-upload-file pour téléverser le fichier
            result = subprocess.run(
                ['manus-upload-file', str(file_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"Upload failed: {result.stderr}")
                return None
            
            # Extraire l'URL de la réponse
            # La réponse contient "CDN URL: https://..."
            output = result.stdout.strip()
            
            # Chercher l'URL dans la réponse
            url_match = re.search(r'https://files[^"\s]+', output)
            
            if url_match:
                public_url = url_match.group(0)
                logger.info(f"File uploaded successfully: {public_url}")
                return public_url
            else:
                logger.error(f"No URL found in upload response: {output}")
                return None
            
        except subprocess.TimeoutExpired:
            logger.error(f"Upload timeout for file: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None
    
    def upload_multiple_files(self, file_paths: list) -> dict:
        """
        Téléverse plusieurs fichiers et retourne un dictionnaire d'URLs
        
        Args:
            file_paths: Liste des chemins de fichiers à téléverser
            
        Returns:
            Dictionnaire {chemin_original: url_publique}
        """
        urls = {}
        
        for file_path in file_paths:
            public_url = self.upload_file(file_path)
            if public_url:
                urls[file_path] = public_url
            else:
                urls[file_path] = None
        
        return urls
