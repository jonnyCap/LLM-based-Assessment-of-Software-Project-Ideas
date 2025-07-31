from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utility.DatabaseConnector import DatabaseConnector, get_db, store_evaluation
from utility.OllamaConnector import generate, extract_json_from_response
from utility.EvaluationSummarizer import LLMEvaluation
from pydantic import BaseModel
from openai import OpenAI
from datetime import datetime
from typing import List
import asyncio
import logging
import os

router = APIRouter()

API_KEY = os.getenv("API_KEY")
ASYNC_REQUEST = os.getenv("ASYNC_REQUEST", "false").lower() == "true"
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2048))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))

MIN_RATING = 0

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ICLEvaluationRequest(BaseModel):
    id: int

class ICLEvaluationResponse(BaseModel):
    quick_eval: LLMEvaluation
    evaluations: List[LLMEvaluation]


EVALUATION_MODELS = ['mistral', 'mistral:7b-instruct', 'llama3.2:3b-instruct-fp16', 'deepseek-r1:8b',]
SUMMARIZER_MODEL = 'Meta-Llama-3-70B-Instruct'

@router.post("/quick_eval")
async def evaluate(evaluation_request: ICLEvaluationRequest, db: DatabaseConnector = Depends(get_db)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not set")

    project_idea = await db.fetch(
        "SELECT id, description FROM project_descriptions WHERE id = $1",
        evaluation_request.id
    )
    if not project_idea:
        raise HTTPException(status_code=404, detail="Project idea not found")

    project_id, description = project_idea[0]["id"], project_idea[0]["description"]

    async def evaluate_model(model: str):
        logger.debug(f"Evaluating with model: {model}")
        prompt = (
            f"You are an experienced tutor in a software project management higher education course. Your task is to evaluate the project idea (described below), assign a score (0-10) for each of the six dimensions (described below). Provide a short justification for each score, explaining why you chose that value. Remember:  The project idea is a text usually consisting of a few sentences, and it is the starting point in a first-year university-level software project management course. The project idea should be the conceptual basis for a project which can be used to apply different project management methods and tools, such as a business plan, risk management, specifications, work breakdown structure, effort estimation and a minimum viable prototype. \n"
            f"Additionally, provide a short general feedback for the project idea (that will be given to the group)\n"
            f"These are the six dimensions you have to evaluate:\n"
            f"1. Novelty (0-10): 0 = There is nothing new or original in the product idea/proposal (only known solutions and knowledge passed on in a new way). 10 = The product idea/proposal is entirely new and original.\n"
            f"2. Usefulness (0-10): 0 = The product idea/proposal does not fit the needs and wishes of the target group(s), (i.e., the potential customers/users). 10 = The product idea/proposal is entirely aligned with the needs and wishes of the target group(s), (i.e., the potential customers/users).\n"
            f"3. Market Potential (0-10): 0 = The product idea/proposal is unlikely to attract sales and be sufficiently profitable to bring onto the market. 10 = The product idea/proposal will likely attract sales and be sufficiently profitable to bring onto the market.\n"
            f"4. Applicability (0-10): 0 = The project idea/proposal is not suitable for implementation within the software project management course (e.g., it lacks a clear software focus, does not require the development of a software-based solution, or falls outside the course's learning objectives). 10 = The project idea/proposal is highly suitable for the software project management course, clearly requiring the development of a software-based solution and fully aligned with the course's learning objectives and expected deliverables.\n"
            f"5. Complexity (0-10): 0 = The project idea/proposal is either too trivial (offering little challenge for meaningful planning and design) or excessively complex (making it unrealistic to meaningfully address through the course deliverables, such as project plans, documentation, and team coordination tasks). 10 = The project idea/proposal has an appropriate and balanced level of complexity, offering sufficient challenges and depth to engage meaningfully with the course deliverables (including project planning, documentation, and design) without being unmanageable or disproportionately demanding for a second-semester student team.\n"
            f"6. Completeness (0-10): 0 = The project idea/proposal is vague or missing essential details, making it unclear what the project's purpose, scope, or implementation steps would be, and providing little usable foundation for further planning in the course.10 = The project idea/proposal is well-documented and complete, clearly describing its purpose, scope, features, and implementation approach, providing a strong and usable foundation for further project planning activities in the course.\n"
            f"\nProject Idea: {description}\n"
            f"\n**Provide a structured JSON response with exactly these fields, ensuring all keys are in lowercase. Evaluations are only allowed to be be of type Integer, **NOT** Float or Double. Enclose all string values in double quotes and ensure the output can be parsed without errors. Strings have to be The JSON format must be as follows:**\n"
            f"{{\n"
            f'    "novelty": <integer (0-10)>,\n'
            f'    "novelty_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "usefulness": <integer (0-10)>,\n'
            f'    "usefulness_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "market_potential": <integer (0-10)>,\n'
            f'    "market_potential_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "applicability": <integer (0-10)>,\n'
            f'    "applicability_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "complexity": <integer (0-10)>,\n'
            f'    "complexity_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "completeness": <integer (0-10)>,\n'
            f'    "completeness_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "feedback": "<max 1-2 short yet grammatically correct sentences (string with a concise evaluation summary, highlighting strengths, weaknesses, and key recommendations for the group)>"\n'
            f"}}\n"
            f"\nEnsure that the response follows this structure exactly, with numeric values between 0 and 10 and a meaningful feedback string."
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await generate(prompt=prompt, model=model)
                if response is None:
                    raise ValueError("No response from model.")

                logger.debug(f"Raw Ollama response for model {model}: {response.text}")
                response_data = response.json()
                raw_response = response_data["response"]

                structured_data = raw_response if isinstance(raw_response, dict) else extract_json_from_response(raw_response)

                # Append necessary data
                structured_data["id"] = 0
                structured_data["project_id"] = project_id
                structured_data["model"] = model
                structured_data["created_at"] = datetime.now()
                structured_data["advanced_prompt"] = False

                evaluation = LLMEvaluation(**structured_data)
                return evaluation

            except Exception as e:
                logger.warning(f"Attempt {attempt} for model {model} failed: {e}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff: 1s, 2s, 4s
                else:
                    raise HTTPException(status_code=500, detail=f"Failed repeatedly to evalute. Error in model {model}: {str(e)}")

    # Concurrent or sequential execution
    if ASYNC_REQUEST:
        evaluations: List[LLMEvaluation] = await asyncio.gather(*[evaluate_model(model) for model in EVALUATION_MODELS])
    else:
        evaluations: List[LLMEvaluation] = []
        for model in EVALUATION_MODELS:
            result = await evaluate_model(model)
            evaluations.append(result)

    # Log the evaluation array with all its entries
    logger.info(f"Evaluations: {evaluations}")
    # --- Store evaluations in the database ---
    for evaluation in evaluations:
        await store_evaluation(db, project_id, evaluation)

    # --- Summarize results ---
    client = OpenAI(api_key=API_KEY, base_url="https://api.hyperbolic.xyz/v1")

    system_prompt = (
            f"You received mutliple evaluations of a project idea from tutors in a first-year university-level software project management course. For your information: The project idea is a text usually consisting of a few sentences, and it is the starting point in a first-year university-level software project management course. Each evaluation includes numerical ratings, justifications for those ratings and a general feedback. \n\n"
            f"This is the project idea that has to be evaluated:\n"
            f"{description}\n\n"
            f"Your task is to reevalute the project idea, by summarizing the received evaluations (listed below).\n"
            f"Your summarized evaluation should be based on the following criteria:\n"
            f"1. Novelty (0-10): 0 = There is nothing new or original in the product idea/proposal (only known solutions and knowledge passed on in a new way). 10 = The product idea/proposal is entirely new and original.\n"
            f"2. Usefulness (0-10): 0 = The product idea/proposal does not fit the needs and wishes of the target group(s), (i.e., the potential customers/users). 10 = The product idea/proposal is entirely aligned with the needs and wishes of the target group(s), (i.e., the potential customers/users).\n"
            f"3. Market Potential (0-10): 0 = The product idea/proposal is unlikely to attract sales and be sufficiently profitable to bring onto the market. 10 = The product idea/proposal will likely attract sales and be sufficiently profitable to bring onto the market.\n"
            f"4. Applicability (0-10): 0 = The project idea/proposal is not suitable for implementation within the software project management course (e.g., it lacks a clear software focus, does not require the development of a software-based solution, or falls outside the course's learning objectives). 10 = The project idea/proposal is highly suitable for the software project management course, clearly requiring the development of a software-based solution and fully aligned with the course's learning objectives and expected deliverables.\n"
            f"5. Complexity (0-10): 0 = The project idea/proposal is either too trivial (offering little challenge for meaningful planning and design) or excessively complex (making it unrealistic to meaningfully address through the course deliverables, such as project plans, documentation, and team coordination tasks). 10 = The project idea/proposal has an appropriate and balanced level of complexity, offering sufficient challenges and depth to engage meaningfully with the course deliverables (including project planning, documentation, and design) without being unmanageable or disproportionately demanding for a second-semester student team.\n"
            f"6. Completeness (0-10): 0 = The project idea/proposal is vague or missing essential details, making it unclear what the project's purpose, scope, or implementation steps would be, and providing little usable foundation for further planning in the course.10 = The project idea/proposal is well-documented and complete, clearly describing its purpose, scope, features, and implementation approach, providing a strong and usable foundation for further project planning activities in the course.\n"
            f"\n**Provide a structured JSON response with exactly these fields, ensuring all keys are in lowercase. Evaluations are only allowed to be be of type Integer, **NOT** Float or Double. The JSON format must be as follows:**\n"
            f"{{\n"
            f'    "novelty": <integer (0-10)>,\n'
            f'    "novelty_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "usefulness": <integer (0-10)>,\n'
            f'    "usefulness_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "market_potential": <integer (0-10)>,\n'
            f'    "market_potential_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "applicability": <integer (0-10)>,\n'
            f'    "applicability_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "complexity": <integer (0-10)>,\n'
            f'    "complexity_justification": <max 1 short yet grammatically correct sentence with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "completeness": <integer (0-10)>,\n'
            f'    "completeness_justification": <max 1 short yet grammatically correct sentenc with 6-12 words (string with concise justification for usefulness evaluation)>,\n'
            f'    "feedback": "<max 1-2 short yet grammatically correct sentences (string with a concise evaluation summary, highlighting strengths, weaknesses, and key recommendations)>"\n'
            f"}}\n")

    user_prompt = f"Here are the evaluations:\n{evaluations}\n"

    evaluation = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            chat_completion = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3-70B-Instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )

            text_response = chat_completion.choices[0].message.content.strip()
            structured_data = extract_json_from_response(text_response)

            # Append necessary data
            structured_data["id"] = 0
            structured_data["project_id"] = project_id
            structured_data["model"] = SUMMARIZER_MODEL
            structured_data["created_at"] = datetime.now()
            structured_data["advanced_prompt"] = False

            evaluation = LLMEvaluation(**structured_data)

            # Store the summarized evaluation in the database
            await store_evaluation(db, project_id, evaluation)

            break
        except Exception as e:
            logger.warning(f"Attempt {attempt} for summarization failed: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 ** (attempt - 1))
            else :
                raise HTTPException(status_code=500, detail=f"Failed repeatedly to summarize. Error: {str(e)}")

    if evaluation is None:
        raise HTTPException(status_code=500, detail="Failed to summarize the evaluations.")

    return ICLEvaluationResponse(quick_eval=evaluation, evaluations=evaluations)