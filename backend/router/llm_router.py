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

async def get_models_from_db(db: DatabaseConnector):
    # TODO: Load this on startup and cache it
    """Fetch available models from ENUM type in the database."""
    query = "SELECT unnest(enum_range(NULL::model_enum)) AS model_name"
    models = await db.fetch(query)
    return [model["model_name"] for model in models]

@router.get("/models")
async def get_available_models(db: DatabaseConnector = Depends(get_db)):
    return await get_models_from_db(db)

@router.post("/evaluate")
async def evaluate(evaluation_request: EvaluationRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        project_idea = await db.fetch(
            "SELECT id, description FROM project_descriptions WHERE id = $1",
            evaluation_request.id
        )
        if not project_idea:
            raise HTTPException(status_code=404, detail="Project idea not found")

        available_models = await get_models_from_db(db)
        if evaluation_request.model not in available_models:
            raise HTTPException(status_code=400, detail="Invalid model")

        project_id, description = project_idea[0]["id"], project_idea[0]["description"]

        prompt = (
            f"Evaluate the following project idea based on the criteria: \n"
            f"Novelty (1-10), Usefulness (1-10), Market Potential (1-10), \n"
            f"Applicability (1-10), Complexity (1-10), Completeness (1-10), Feedback text.\n"
            f"\nProject Idea: {description}\n"
            f"\nProvide a structured JSON response with these fields."
        )        

        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={"model": evaluation_request.model, "prompt": prompt}
        )
        response_data = response.json()
        
        await db.execute(
            "INSERT INTO llm_evaluations (project_id, model, novelty, usefulness, market_potential, applicability, complexity, completeness, feedback) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
            project_id, evaluation_request.model,
            response_data.get("novelty", 5), response_data.get("usefulness", 5),
            response_data.get("market_potential", 5), response_data.get("applicability", 5),
            response_data.get("complexity", 5), response_data.get("completeness", 5),
            response_data.get("feedback", "No feedback")
        )
        
        return JSONResponse(content={"message": "Evaluation added successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pull")
async def pull_model(model: str, db: DatabaseConnector = Depends(get_db)):
    try:
        # Send request to pull the model
        response = requests.post(f"{OLLAMA_API_URL}/api/pull", json={"model": model})
        response_data = response.json()

        if response.status_code == 200:
            # Check if model already exists in ENUM
            existing_models_query = "SELECT unnest(enum_range(NULL::model_enum)) AS model_name"
            existing_models = await db.fetch(existing_models_query)
            existing_models = {model_row["model_name"] for model_row in existing_models}

            if model not in existing_models:
                # Add new model to ENUM (ALTER TYPE)
                alter_enum_query = f"ALTER TYPE model_enum ADD VALUE '{model}'"
                await db.execute(alter_enum_query)

            return JSONResponse(content={"message": f"Model '{model}' pulled and added to ENUM."}, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Failed to pull model from API")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

