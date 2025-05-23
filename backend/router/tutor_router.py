from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utility.DatabaseConnector import DatabaseConnector, get_db
from pydantic import BaseModel, Field

class TutorEvaluationRequest(BaseModel):
    project_id: int = Field(..., description="The ID of the project being evaluated")
    username: str = Field(..., description="The username of the tutor who is evaluating the project")
    novelty: int = Field(..., ge=0, le=10)
    usefulness: int = Field(..., ge=0, le=10)
    market_potential: int = Field(..., ge=0, le=10)
    applicability: int = Field(..., ge=0, le=10)
    complexity: int = Field(..., ge=0, le=10)
    completeness: int = Field(..., ge=0, le=10)
    feedback: str = Field(..., description="Feedback for the project")

router = APIRouter()

@router.post("/evaluate")
async def evaluate_tutor(evaluation_request: TutorEvaluationRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        await db.execute(
            "INSERT INTO tutor_evaluations (project_id, username, novelty, usefulness, market_potential, applicability, complexity, completeness, feedback) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
            evaluation_request.project_id, evaluation_request.username, evaluation_request.novelty, evaluation_request.usefulness, evaluation_request.market_potential,
            evaluation_request.applicability, evaluation_request.complexity, evaluation_request.completeness, evaluation_request.feedback
        )
        
        return JSONResponse(content={"message": "Tutor evaluation added successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
