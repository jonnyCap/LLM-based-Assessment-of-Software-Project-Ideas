from fastapi import APIRouter, HTTPException, Depends
from utility.DatabaseConnector import DatabaseConnector, get_db
import os
import requests

router = APIRouter()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:8000")

# If you want to extend this list, add them either in docker compose or use the pull endpoint dyncamically
MODELS = ["mistral"]

@router.get("/models")
def get_available_models():
    return MODELS

@router.post("/generate")
async def generate_response(prompt: str, db: DatabaseConnector = Depends(get_db)):
    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/generate", json={"model": "mistral", "prompt": prompt})
        
        # TODO: Store request
        db.fetch("SELECT * from requests", prompt)
        # TODO: Store response
        db.execute("INSERT INTO responses (prompt, response) VALUES ($1, $2)", prompt, response.json()["response"])
        
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pull")
def pull_model(model: str):
    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/pull", json={"model": model})
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))