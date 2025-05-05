from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from utility.DatabaseConnector import DatabaseConnector, get_db, get_models_from_db
from utility.EvaluationSummarizer import AverageEvaluation, TutorEvaluation, LLMEvaluation, summarize_evaluations, summarize_feedback, average_evaluation
from pydantic import BaseModel, Field
from typing import List
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class IdeaResponse(BaseModel):
    id: int
    description: str

class AddIdeaRequest(BaseModel):
    ideas: List[str]  # List of text inputs

class DeleteIdeaRequest(BaseModel):
    id: int = Field(..., description="The ID of the idea to be deleted")

class SummaryRequest(BaseModel):
    id: int = Field(..., description="The ID of the idea to be summarized")
    model: str = Field(..., description="The model used for evaluation")
    llm_advanced_summary_enabled: bool
    tutor_advanced_summary_enabled: bool


# Model for /load-evaluations response
class EvaluationsResponse(BaseModel):
    llm_evaluations: List[LLMEvaluation]
    tutor_evaluations: List[TutorEvaluation]


class EvaluationSummaryResponse(BaseModel):
    tutor_summary: AverageEvaluation
    llm_summary: AverageEvaluation


router = APIRouter()


@router.get("/get-ideas")
async def get_ideas(db: DatabaseConnector = Depends(get_db)):
    try:
        query = "SELECT id, description FROM project_descriptions"
        ideas = await db.fetch(query)
        return [IdeaResponse(id=idea["id"], description=idea["description"]) for idea in ideas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-ideas")
async def add_ideas(idea_request: AddIdeaRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        query = "INSERT INTO project_descriptions (description) VALUES ($1)"  # Use $1 instead of %s
        for idea in idea_request.ideas:
            await db.execute(query, idea)  # Pass parameters correctly
        return JSONResponse(content={"message": "Ideas added successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-idea")
async def delete_idea(idea_request: DeleteIdeaRequest, db: DatabaseConnector = Depends(get_db)):
    try:
        query = "DELETE FROM project_descriptions WHERE id = $1"
        await db.execute(query, idea_request.id)
        return JSONResponse(content={"message": "Idea deleted successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_evaluations(db: DatabaseConnector, id: int):
    query_llm = "SELECT * FROM llm_evaluations WHERE project_id = $1"
    query_tutor = "SELECT * FROM tutor_evaluations WHERE project_id = $1"
    
    llm_evaluations = await db.fetch(query_llm, id)
    tutor_evaluations = await db.fetch(query_tutor, id)

    logger.debug(f"LLM Results: {llm_evaluations}")
    logger.debug(f"Tutor Results: {tutor_evaluations}")

    return EvaluationsResponse(
        llm_evaluations = [LLMEvaluation(**dict(eval.items())) for eval in llm_evaluations],
        tutor_evaluations = [TutorEvaluation(**dict(eval.items())) for eval in tutor_evaluations]
    )


@router.get("/load-evaluations")
async def load_evaluations(
    id: int = Query(..., description="The ID of the idea to load evaluations for"),
    db: DatabaseConnector = Depends(get_db)
):
    try:
       return await fetch_evaluations(db, id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to load evaluations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize(
    summary_request: SummaryRequest,
    db: DatabaseConnector = Depends(get_db)
):
    try:
        evaluation_response = await fetch_evaluations(db, summary_request.id)

        # Summarize the tutor evaluations
        tutor_evaluations = evaluation_response.tutor_evaluations
        llm_evaluations = evaluation_response.llm_evaluations

        available_models = await get_models_from_db(db)
        if summary_request.model not in available_models:
            raise HTTPException(status_code=400, detail="Invalid model")

        if not tutor_evaluations or not llm_evaluations:
            raise HTTPException(status_code=400, detail="Please make at least one manual evaluation.")

        if not llm_evaluations:
            raise HTTPException(status_code=400, detail="Please generate at least one evaluation with an LLM.")

        logger.info("There are at least 1 of each tutor- and llm-evaluations.")

        # Summarize the tutor evaluations
        logger.info("Summarizing tutor-evaluations.")
        if summary_request.tutor_advanced_summary_enabled:
            logger.info("Using advanced summarization. (Tutor)")
            tutor_summary: AverageEvaluation = await summarize_evaluations(tutor_evaluations)
        else:
            logger.info("Using statistical summarization. (LLM)")
            tutor_summary: AverageEvaluation = average_evaluation(tutor_evaluations)
            tutor_summary.feedback = await summarize_feedback(tutor_summary.feedback)

        # Summarize the LLM evaluations
        logger.info("Summarizing llm-evaluations.")
        if summary_request.llm_advanced_summary_enabled:
            logger.info("Using advanced summarization. (LLM)")
            llm_summary: AverageEvaluation = await summarize_evaluations(llm_evaluations)
            pass
        else:
            logger.info("Using statistical summarization. (LLM)")
            llm_summary: AverageEvaluation = average_evaluation(llm_evaluations)
            llm_summary.feedback = await summarize_feedback(llm_summary.feedback)

        if llm_summary is None or tutor_summary is None:
            return HTTPException(status_code=500, detail="Failed to summarize evaluations")
        
        return EvaluationSummaryResponse(tutor_summary=tutor_summary, llm_summary=llm_summary)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))