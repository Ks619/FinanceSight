import httpx
import traceback

def split_text_into_chunks(text, max_length=4000):
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

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://llm:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=500
            )

            response.raise_for_status()
            result = response.json()

            return result.get("response", "").strip()
        
        except httpx.HTTPStatusError as e:
            return f"HTTP error: {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Request error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"