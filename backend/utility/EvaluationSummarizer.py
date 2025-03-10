from utility.OllamaConnector import generate
from typing import List, DefaultDict
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Evaluation(BaseModel):
    id: int
    project_id: int
    novelty: int = Field(..., ge=0, le=10)
    usefulness: int = Field(..., ge=0, le=10)
    market_potential: int = Field(..., ge=0, le=10)
    applicability: int = Field(..., ge=0, le=10)
    complexity: int = Field(..., ge=0, le=10)
    completeness: int = Field(..., ge=0, le=10)
    feedback: str

class TutorEvaluation(Evaluation):
    username: str = Field(..., description="The username of the tutor who is evaluating the project")

class LLMEvaluation(Evaluation):
    model: str = Field(..., description="The name of the LLM model used for evaluation")

class AverageEvaluation(BaseModel):
    num_evaluations: int
    novelty: float
    usefulness: float
    market_potential: float
    applicability: float
    complexity: float
    completeness: float
    feedback: str

def average_evaluation(evaluations: List[Evaluation]):
    num_evaluations = len(evaluations)
    aggregated = DefaultDict(int)
    all_feedback = []

    for evaluation in evaluations:
        aggregated["novelty"] += evaluation.novelty
        aggregated["usefulness"] += evaluation.usefulness
        aggregated["market_potential"] += evaluation.market_potential
        aggregated["applicability"] += evaluation.applicability
        aggregated["complexity"] += evaluation.complexity
        aggregated["completeness"] += evaluation.completeness
        all_feedback.append(evaluation.feedback)

    # Create average evaluation entity
    return AverageEvaluation(
        num_evaluations=num_evaluations,
        novelty=aggregated["novelty"] / num_evaluations,
        usefulness=aggregated["usefulness"] / num_evaluations,
        market_potential=aggregated["market_potential"] / num_evaluations,
        applicability=aggregated["applicability"] / num_evaluations,
        complexity=aggregated["complexity"] / num_evaluations,
        completeness=aggregated["completeness"] / num_evaluations,
        feedback=" | ".join(all_feedback)  # Concatenated feedback
    )


async def summarize_feedback(feedback: str):
    prompt = (
        "The following is a collection of feedback comments from multiple evaluations:\n\n"
        f"{feedback}\n\n"
        "Please provide a concise and well-structured summary of this feedback that captures the key points."
    )

    response = await generate(prompt)
    
    if response and response.status_code == 200:
        return response.json().get("response", "Summarization failed.")
    
    return "Summarization failed due to an error."



async def summarize_evaluations(evaluations: List[Evaluation]):
    if not evaluations:
        logger.error("There have not been any evaluations.")
        return None  # Return None if no evaluations exist

    # Construct the structured prompt
    prompt = "Below are multiple evaluations of a project. Each evaluation includes numerical ratings and feedback:\n\n"

    for i, evaluation in enumerate(evaluations, start=1):
        prompt += (
            f"Evaluation {i}:\n"
            f"  - Novelty: {evaluation.novelty}/10\n"
            f"  - Usefulness: {evaluation.usefulness}/10\n"
            f"  - Market Potential: {evaluation.market_potential}/10\n"
            f"  - Applicability: {evaluation.applicability}/10\n"
            f"  - Complexity: {evaluation.complexity}/10\n"
            f"  - Completeness: {evaluation.completeness}/10\n"
            f"  - Feedback: {evaluation.feedback}\n\n"
        )

    prompt += (
        "Based on these evaluations, please provide the following:\n"
        "1. A concise and structured summary of the feedback, identifying key insights and recurring themes.\n"
        "2. A reevaluated assessment of the project, assigning **new** scores (on a scale of 0 to 10), using previous assessments, for:\n"
        "   - Novelty\n"
        "   - Usefulness\n"
        "   - Market Potential\n"
        "   - Applicability\n"
        "   - Complexity\n"
        "   - Completeness\n\n"
        "Please return your response in the following JSON format:\n"
        "{\n"
        '  "novelty": <new_value>,\n'
        '  "usefulness": <new_value>,\n'
        '  "market_potential": <new_value>,\n'
        '  "applicability": <new_value>,\n'
        '  "complexity": <new_value>,\n'
        '  "completeness": <new_value>,\n'
        '  "feedback": "<summarized_feedback>"\n'
        "}"
    )

    # Call the LLM to generate the summary and reevaluation
    response = await generate(prompt)

    if response and response.status_code == 200:
        try:
            response_json = response.json()
            if "response" not in response_json:
                raise ValueError("Missing 'response' key in LLM output.")
    
            llm_response = response_json["response"]  # Extract the response content
            llm_data = json.loads(llm_response)  # Parse the JSON string from LLM
    
            # Ensure all required keys are present, otherwise default to None
            return AverageEvaluation(
                num_evaluations=len(evaluations),
                novelty=llm_data.get("novelty"),
                usefulness=llm_data.get("usefulness"),
                market_potential=llm_data.get("market_potential"),
                applicability=llm_data.get("applicability"),
                complexity=llm_data.get("complexity"),
                completeness=llm_data.get("completeness"),
                feedback=llm_data.get("feedback", "Summarization failed.")
            )

        except json.JSONDecodeError:
            logger.error("LLM response is not a valid JSON object.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    logger.error("Summarization failed due to an error.")
    return None

