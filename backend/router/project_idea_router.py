from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utility.DatabaseConnector import DatabaseConnector, get_db
from pydantic import BaseModel, Field
from typing import List

# Model for /add-ideas endpoint
class AddIdeaRequest(BaseModel):
    ideas: List[str]  # List of text inputs

# Model for /delete-ideas endpoint
class DeleteIdeaRequest(BaseModel):
    id: int = Field(..., description="The ID of the idea to be deleted")

class LoadIdeaEvaluationRequest(BaseModel):
    id: int = Field(..., description="The ID of the idea which evaluations are to be loaded")

# Model for evaluations (shared by both LLM and Tutor evaluations)
class Evaluation(BaseModel):
    id: int
    project_id: int
    novelty: int = Field(..., ge=1, le=10)
    usefulness: int = Field(..., ge=1, le=10)
    market_potential: int = Field(..., ge=1, le=10)
    applicability: int = Field(..., ge=1, le=10)
    complexity: int = Field(..., ge=1, le=10)
    completeness: int = Field(..., ge=1, le=10)
    feedback: str

# Model for /load-evaluations response
class EvaluationsResponse(BaseModel):
    llm_evaluations: List[Evaluation]
    tutor_evaluations: List[Evaluation]


router = APIRouter()

@router.post("/add-ideas")
def add_ideas(idea_request: AddIdeaRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        query = "INSERT INTO project_description (description) VALUES (%s)"
        for idea in idea_request.ideas:
            db.execute(query, idea)
        return JSONResponse(content={"message": "Ideas added successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-ideas")
def delete_idea(idea_request: DeleteIdeaRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        query = "DELETE FROM project_description WHERE id = %s"
        db.execute(query, idea_request.id)
        return JSONResponse(content={"message": "Idea deleted successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/load-evaluations")
def load_evaluations(idea_request: LoadIdeaEvaluationRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        query_llm = "SELECT * FROM llm_evaluations WHERE project_id = %s"
        query_tutor = "SELECT * FROM tutor_evaluations WHERE project_id = %s"
        
        llm_evaluations = db.fetch(query_llm, idea_request.id)
        tutor_evaluations = db.fetch(query_tutor, idea_request.id)
        
        return EvaluationsResponse(
            llm_evaluations=[Evaluation(**dict(eval)) for eval in llm_evaluations],
            tutor_evaluations=[Evaluation(**dict(eval)) for eval in tutor_evaluations]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


