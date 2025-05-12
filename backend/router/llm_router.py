from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from router.icl2025_router import EVALUATION_MODELS, SUMMARIZER_MODEL
from utility.DatabaseConnector import DatabaseConnector, get_db, get_models_from_db
from utility.OllamaConnector import generate, pull, extract_json_from_response
from pydantic import BaseModel
import logging
import json

MIN_RATING = 0

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class EvaluationRequest(BaseModel):
    id: int
    model: str
    advanced_prompt: bool

router = APIRouter()


@router.get("/models")
async def get_available_models(db: DatabaseConnector = Depends(get_db)):
    models = await get_models_from_db(db)
    # Merge EVALUATION_MODELS and models into a single list
    merged_models = EVALUATION_MODELS + models + [SUMMARIZER_MODEL]
    return merged_models


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

        if evaluation_request.advanced_prompt:
            logger.info("Using advanced evaluation prompt.")

            criteria = {
                "novelty": "Assess how new and original this idea is. Have similar ideas been proposed or implemented before?",
                "usefulness": "Evaluate whether this project has a real-world application. Does it solve a tangible problem or provide value?",
                "market_potential": "Analyze the market viability of this project. How would it perform in the market considering competition and demand?",
                "applicability": "Determine if this project is feasible and fits within the context of a Software Project Management course. Can it realistically be executed?",
                "complexity": "Assess whether the project provides the right level of complexity for a Software Project Management course. Is it too simple or too complicated?",
                "completeness": "Evaluate how well the project has been described. Does it account for necessary details, edge cases, and potential challenges?"
            }
            evaluation_results = {}
            
            for criterion, description_text in criteria.items():
                prompt = (
                    f"Critically evaluate the following project idea based on '{criterion.replace('_', ' ')}'.\n"
                    f"{description_text}\n"
                    f"Rate it on a scale from 0-10 and provide a brief justification.\n"
                    f"\nProject Idea: {description}\n"
                    f"\n**Your response must be a structured JSON object with exactly two fields: '{criterion}' (integer 0-10) and 'justification' (string).**\n"
                    f"Ensure the response follows this exact JSON format:\n"
                    f"{{\n"
                    f'    "{criterion}": <integer (0-10)>,\n'
                    f'    "justification": "<A brief justification for the given score>"\n'
                    f"}}\n"
                    f"\nReturn only this JSON object and nothing else."
                )

                response = await generate(prompt=prompt, model=evaluation_request.model)
                if response is None:
                    raise HTTPException(status_code=500, detail=f"Failed to evaluate {criterion}.")
                
                try:
                    raw_response = response.json()
                    logger.debug(f"Raw Ollama response for {criterion}: {raw_response}")

                    structured_data = extract_json_from_response(raw_response.get("response", "{}"))

                    if criterion not in structured_data:
                        raise ValueError(f"Missing '{criterion}' key in LLM output.")

                    evaluation_results[criterion] = {
                        "score": int(structured_data.get(criterion, MIN_RATING)),
                        "justification": structured_data.get("justification", "No justification provided")
                    }
                except Exception as e:
                    logger.error(f"Failed to parse JSON for {criterion}: {e}")
                    raise HTTPException(status_code=500, detail=f"Invalid JSON format for {criterion}.")


                prompt_feedback = (
                    f"Provide a single concise feedback summary for the following project idea, considering all aspects: {', '.join(criteria.keys())}.\n"
                    f"\nProject Idea: {description}\n"
                    f"\n**Your response must be a structured JSON object with exactly one field named 'feedback'.**\n"
                    f"Ensure the response follows this exact JSON format:\n"
                    f"{{\n"
                    f'    "feedback": "<A short summary of strengths, weaknesses, and key recommendations>"\n'
                    f"}}\n"
                    f"\nReturn only this JSON object and nothing else."
                )

            
            response_feedback = await generate(prompt=prompt_feedback, model=evaluation_request.model)
            if response_feedback is None:
                raise HTTPException(status_code=500, detail="Failed to generate feedback.")

            try:
                logger.debug(f"Raw Ollama response for feedback: {response_feedback.json()}")
                structured_feedback = extract_json_from_response(response_feedback.json().get("response", "{}"))
                feedback = structured_feedback.get("feedback", "No feedback provided")
            except Exception as e:
                logger.error(f"Failed to parse JSON for feedback: {e}")
                raise HTTPException(status_code=500, detail="Invalid JSON format for feedback.")

        
            novelty = evaluation_results["novelty"]["score"]
            usefulness = evaluation_results["usefulness"]["score"]
            market_potential = evaluation_results["market_potential"]["score"]
            applicability = evaluation_results["applicability"]["score"]
            complexity = evaluation_results["complexity"]["score"]
            completeness = evaluation_results["completeness"]["score"]
        else:
            logger.info("Using basic evaluation prompt.")
            prompt = (
                f"Critically evaluate the following project idea based on the criteria: \n"
                f"1. Novelty (0-10): Assess how new and original this idea is. Have similar ideas been proposed or implemented before?\n"
                f"2. Usefulness (0-10): Evaluate whether this project has a real-world application. Does it solve a tangible problem or provide value?\n"
                f"3. Market Potential (0-10): Analyze the market viability of this project. How would it perform in the market considering competition and demand?\n"
                f"4. Applicability (0-10): Determine if this project is feasible and fits within the context of a Software Project Management course. Can it realistically be executed?\n"
                f"5. Complexity (0-10): Assess whether the project provides the right level of complexity for a Software Project Management course. Is it too simple or too complicated?\n"
                f"6. Completeness (0-10): Evaluate how well the project has been described. Does it account for necessary details, edge cases, and potential challenges?\n"
                f"\nProject Idea: {description}\n"
                f"\n**Provide a structured JSON response with exactly these fields, ensuring all keys are in lowercase. The JSON format must be as follows:**\n"
                f"{{\n"
                f'    "novelty": <integer (0-10)>,\n'
                f'    "usefulness": <integer (0-10)>,\n'
                f'    "market_potential": <integer (0-10)>,\n'
                f'    "applicability": <integer (0-10)>,\n'
                f'    "complexity": <integer (0-10)>,\n'
                f'    "completeness": <integer (0-10)>,\n'
                f'    "feedback": "<string with a concise evaluation summary, highlighting strengths, weaknesses, and key recommendations>"\n'
                f"}}\n"
                f"\nEnsure that the response follows this structure exactly, with numeric values between 0 and 10 and a meaningful feedback string."
            )

            response = await generate(prompt=prompt, model=evaluation_request.model)
            if response is None:
                return HTTPException(status_code=500, detail="An error occurred while interacting with LLMs.")

            logger.debug(f"Raw Ollama response: {response.text}")
            response_data = response.json()

            try:
                raw_response = response_data["response"]
    
                if isinstance(raw_response, dict):
                    structured_data = raw_response
                else:
                    structured_data = extract_json_from_response(raw_response)

            except Exception as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                raise HTTPException(status_code=500, detail="Invalid JSON format in Ollama response.")
    
            novelty = int(structured_data.get("novelty", MIN_RATING))
            usefulness = int(structured_data.get("usefulness", MIN_RATING))
            market_potential = int(structured_data.get("market_potential", MIN_RATING))
            applicability = int(structured_data.get("applicability", MIN_RATING))
            complexity = int(structured_data.get("complexity", MIN_RATING))
            completeness = int(structured_data.get("completeness", MIN_RATING))
            feedback = structured_data.get("feedback", "No feedback")

        await db.execute(
            "INSERT INTO llm_evaluations (project_id, model, novelty, usefulness, market_potential, applicability, complexity, completeness, feedback, advanced_prompt) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            project_id, evaluation_request.model,
            novelty, usefulness, market_potential, applicability, complexity, completeness, feedback, evaluation_request.advanced_prompt
        )
        
        return JSONResponse(content={"message": "Evaluation added successfully"}, status_code=200)
    except Exception as e:
        logger.error(f"Failed to evaluate project idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/pull")
async def pull_model(model: str, db: DatabaseConnector = Depends(get_db)):
    try:
        # Send request to pull the model
        response = await pull(model)
        if response is None:
            return HTTPException(status_code=500, detail="An error occured while pulling the model.")

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

