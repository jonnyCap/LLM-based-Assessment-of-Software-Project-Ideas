import httpx
import os
import logging
import re
import json
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://100.78.4.119:11434")


class OllamaAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            if payload.get("error"):
                return str(payload["error"])
            if payload.get("message"):
                return str(payload["message"])
    except Exception:
        pass

    response_text = response.text.strip()
    if response_text:
        return response_text

    return f"Ollama request failed with status {response.status_code}."


def ensure_ollama_success(response: httpx.Response | None, operation: str) -> dict[str, Any]:
    if response is None:
        raise OllamaAPIError(502, f"Ollama did not respond during {operation}.")

    if response.status_code >= 400:
        error_message = _extract_error_message(response)
        raise OllamaAPIError(response.status_code, f"Ollama {operation} failed: {error_message}")

    try:
        payload = response.json()
    except Exception:
        raise OllamaAPIError(502, f"Ollama {operation} returned an invalid JSON response.")

    if isinstance(payload, dict) and payload.get("error"):
        raise OllamaAPIError(response.status_code or 502, f"Ollama {operation} failed: {payload['error']}")

    if not isinstance(payload, dict):
        raise OllamaAPIError(502, f"Ollama {operation} returned an unexpected response format.")

    return payload

async def generate(prompt: str, model: str = "mistral"):
    try:
        async with httpx.AsyncClient(timeout=14400) as client:
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

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try extracting first {...}
    match = re.search(r"(\{.*?\})", response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

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

    # If the response_text does not end with a closing brace, add it
    if not response_text.endswith("}"):
        response_text += "}"
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
    

async def list_models() -> list[str]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{OLLAMA_API_URL}/api/tags")
        payload = ensure_ollama_success(response, "model listing")

        models = payload.get("models", [])
        if not isinstance(models, list):
            return []

        model_names: list[str] = []
        for model in models:
            if isinstance(model, dict):
                name = model.get("name")
                if isinstance(name, str):
                    model_names.append(name)
            elif isinstance(model, str):
                model_names.append(model)

        return model_names
    except Exception as e:
        logger.warning(f"Failed to load models from Ollama: {e}")
        return []
