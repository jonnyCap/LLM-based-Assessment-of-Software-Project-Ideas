from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utility.DatabaseConnector import DatabaseConnector, get_db
from pydantic import BaseModel
import os
import requests

class EvaluationRequest(BaseModel):
    id: str
    model: str

router = APIRouter()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:8000")

# If you want to extend this list, add them either in docker compose or use the pull endpoint dyncamically
MODELS = ["mistral"]

@router.get("/models")
def get_available_models():
    return MODELS

@router.post("/evaluate")
async def evaluate(evaluation_request: EvaluationRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        project_idea = await db.fetch("SELECT id, description FROM project_description WHERE id = $1", evaluation_request.id)
        if not project_idea:
            raise HTTPException(status_code=404, detail="Project idea not found")
        
        if evaluation_request.model not in MODELS:
            raise HTTPException(status_code=400, detail="Invalid model")

        project_id, description = project_idea[0]["id"], project_idea[0]["description"]

        # TODO: Give more context here
        prompt = (
            f"Evaluate the following project idea based on the criteria: \n"
            f"Novelty (1-10), Usefulness (1-10), Market Potential (1-10), \n"
            f"Applicability (1-10), Complexity (1-10), Completeness (1-10), Feedback text.\n"
            f"\nProject Idea: {description}\n"
            f"\nProvide a structured JSON response with these fields."
        )        

        response: dict = requests.post(f"{OLLAMA_API_URL}/api/generate", json={"model": evaluation_request.model, "prompt": prompt})
        response_data = response.json()
        
        await db.execute(
            "INSERT INTO llm_evaluations (project_id, novelty, usefulness, market_potential, applicability, complexity, completeness, feedback) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            project_id, response_data.get("novelty", 5), response_data.get("usefulness", 5), response_data.get("market_potential", 5),
            response_data.get("applicability", 5), response_data.get("complexity", 5), response_data.get("completeness", 5), response_data.get("feedback", "No feedback")
        )
        
        return JSONResponse(content={"message": "Evaluation added successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pull")
def pull_model(model: str):
    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/pull", json={"model": model})
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))