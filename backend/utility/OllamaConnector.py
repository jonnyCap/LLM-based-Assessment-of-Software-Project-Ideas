import httpx
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:8000")

async def generate(prompt: str, model: str = "mistral"):
    try:
        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(
                f"{OLLAMA_API_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
        return response
    except Exception:
        return None


async def pull(model: str):
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            return await client.post(f"{OLLAMA_API_URL}/api/pull", json={"model": model})
    except Exception:
        return None
    
