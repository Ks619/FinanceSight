import httpx
import traceback
import os
import json

OLLAMA_API = os.getenv("OLLAMA_API", "http://ollama:11434")

def split_text_into_chunks(text, max_length=2000):
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= max_length:
            current_chunk += paragraph + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


async def analyze_with_ollama(chunk: str):
    prompt = (
        "Analyze the following crypto news and suggest if there are any interesting coins "
        "to consider investing in, based on trends, project potential, and current events:\n\n"
        f"{chunk}"
    )

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=60.0)) as client:
            response = await client.post(
                f"{OLLAMA_API}/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": True}
            )

            response.raise_for_status()
            result = ""
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        result += data.get("response", "")
                    except json.JSONDecodeError as e:
                        result += f"\n[Decode error]: {e}"
            return result.strip()

    except httpx.HTTPStatusError as e:
        return f"HTTP error: {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"Request error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
