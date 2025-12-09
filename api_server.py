# api_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os
import tempfile
from job_application_agent.run_daily_with_s3 import DailyJobApplicationRunnerWithS3

app = FastAPI(title="Job Application Agent API")

# Modèle Pydantic pour les données d'offres reçues de N8N
class JobOfferData(BaseModel):
    offers: List[Dict[str, Any]]

@app.post("/run_agent")
def run_agent(data: JobOfferData):
    """
    Endpoint appelé par N8N pour déclencher l'exécution de l'agent.
    """
    
    offers_data = data.offers
    
    if not offers_data:
        raise HTTPException(status_code=400, detail="No 'offers' data found in the request body.")

    # 1. Création d'un fichier temporaire pour les offres
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
        json.dump(offers_data, tmp_file)
        temp_offers_path = tmp_file.name

    # 2. Exécution de l'agent
    try:
        # L'agent est appelé avec le chemin du fichier temporaire
        runner = DailyJobApplicationRunnerWithS3(test_data_path=temp_offers_path)
        success = runner.run()
        
        # 3. Nettoyage du fichier temporaire
        os.remove(temp_offers_path)
        
        if success:
            return {"status": "success", "message": "Agent executed successfully. Report sent via email."}
        else:
            raise HTTPException(status_code=500, detail="Agent execution failed. Check Render logs for details.")
            
    except Exception as e:
        # 4. Nettoyage en cas d'erreur
        if os.path.exists(temp_offers_path):
            os.remove(temp_offers_path)
            
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

