from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utility.DatabaseConnector import DatabaseConnector, get_db
from utility.OllamaConnector import generate, pull, extract_json_from_response
from pydantic import BaseModel
from openai import OpenAI
import asyncio
import logging
import os

router = APIRouter()

API_KEY = os.getenv("API_KEY")
MIN_RATING = 0
MAX_RETRIES = 3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ICLEvaluationRequest(BaseModel):
    id: int
    is_async: bool = False


# TODO: use actual models here instead
EVALUATION_MODELS = ['mistral', "llama2"]

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

    description = project_idea[0]["description"]

    async def evaluate_model(model: str):
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

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await generate(prompt=prompt, model=model)
                if response is None:
                    raise ValueError("No response from model.")

                logger.debug(f"Raw Ollama response for model {model}: {response.text}")
                response_data = response.json()
                raw_response = response_data["response"]

                structured_data = raw_response if isinstance(raw_response, dict) else extract_json_from_response(raw_response)
                return {"model": model, "evaluation": structured_data}

            except Exception as e:
                logger.warning(f"Attempt {attempt} for model {model} failed: {e}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff: 1s, 2s, 4s
                else:
                    logger.error(f"Model {model} failed after {MAX_RETRIES} attempts.")
                    return {"model": model, "error": str(e)}

    # Concurrent or sequential execution
    if evaluation_request.is_async:
        # TODO: Use the actual models instead of 'mistral'
        evaluations = await asyncio.gather(*[evaluate_model('mistral') for model in EVALUATION_MODELS])
    else:
        evaluations = []
        for model in EVALUATION_MODELS:
            # TODO: Remove this next line:
            model = 'mistral'
            result = await evaluate_model(model)
            evaluations.append(result)

    # --- Summarize results ---
    client = OpenAI(api_key=API_KEY, base_url="https://api.hyperbolic.xyz/v1")

    system_prompt = (
            f"You are a helpful assistant that summarizes evaluation scores across different models."
            f"\n**Provide a structured JSON response with exactly these fields, ensuring all keys are in lowercase. The JSON format must be as follows:**\n"
            f"{{\n"
            f'    "novelty": <integer (0-10)>,\n'
            f'    "usefulness": <integer (0-10)>,\n'
            f'    "market_potential": <integer (0-10)>,\n'
            f'    "applicability": <integer (0-10)>,\n'
            f'    "complexity": <integer (0-10)>,\n'
            f'    "completeness": <integer (0-10)>,\n'
            f'    "feedback": "<string with a concise evaluation summary, highlighting strengths, weaknesses, and key recommendations>"\n'
            f"}}\n")

    user_prompt = f"Here are the evaluations:\n{evaluations}\nSummarize them in a helpful way."

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            chat_completion = await client.chat.completions.create(
                model="meta-llama/Meta-Llama-3-70B-Instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=1024,
            )

            text_response = chat_completion.choices[0].message.content.strip()
            structured_data = extract_json_from_response(text_response)

            break
        except Exception as e:
            logger.warning(f"Attempt {attempt} for summarization failed: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 ** (attempt - 1))


    return JSONResponse(content={
        "summary": structured_data,
        "evaluations": evaluations
    })