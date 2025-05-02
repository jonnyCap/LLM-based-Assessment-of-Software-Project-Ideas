import httpx
import os
import logging
import re
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:8000")

async def generate(prompt: str, model: str = "mistral"):
    try:
        async with httpx.AsyncClient(timeout=7200) as client:
            response = await client.post(
                f"{OLLAMA_API_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
        return response
    except Exception:
        return None

def extract_json_from_response(response_text: str) -> dict:
    """
    Attempts to extract and parse a JSON object from a string, handling common LLM response formats.
    """

    response_text = response_text.strip()

    try:
        # Try to parse the entire response as JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Replace triple quotes with normal quotes (common LLM issue)
    response_text = re.sub(r'"""(.*?)"""', lambda m: json.dumps(m.group(1)), response_text, flags=re.DOTALL)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Normalize smart quotes once — early
    response_text = response_text.replace("“", '"').replace("”", '"')

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown code block ```json ... ```
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if code_block_match:
        try:
            inner = re.sub(r'"""(.*?)"""', lambda m: json.dumps(m.group(1)), code_block_match.group(1), flags=re.DOTALL)
            return json.loads(inner)
        except json.JSONDecodeError:
            pass

    # Fallback: extract the first {...} block
    brace_match = re.search(r"(\{.*?\})", response_text, re.DOTALL)
    if brace_match:
        try:
            inner = re.sub(r'"""(.*?)"""', lambda m: json.dumps(m.group(1)), brace_match.group(1), flags=re.DOTALL)
            return json.loads(inner)
        except json.JSONDecodeError:
            pass

    # If all else fails
    raise ValueError("Failed to extract valid JSON from response.")


async def pull(model: str):
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            return await client.post(f"{OLLAMA_API_URL}/api/pull", json={"model": model})
    except Exception:
        return None
    
