import json
from pathlib import Path
import asyncio
import httpx
import os

OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")
semaphore = asyncio.Semaphore(3)
print("Using OLLAMA_API:", OLLAMA_API)


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

    timeout = httpx.Timeout(600.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                f"{OLLAMA_API}/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": True},
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


async def analyze_limited(chunk: str):
    async with semaphore:
        return await analyze_with_ollama(chunk)


async def analyze_existing_news_file():
    path = Path("received_data/crypto_news.json")
    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        all_news = json.load(f)

    full_text = "\n\n".join([item.get("content", "") for item in all_news if item.get("content")])
    if not full_text.strip():
        print("[WARN] No content found in crypto_news.json.")
        return

    chunks = split_text_into_chunks(full_text)
    analysis_tasks = [analyze_limited(chunk) for chunk in chunks]
    results = await asyncio.gather(*analysis_tasks)

    final_analysis = "\n\n".join([f"--- Chunk {i+1} ---\n{res}" for i, res in enumerate(results)])
    output_path = Path("received_data/crypto_news_analysis.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_analysis)

    print(f"[INFO] Analysis saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(analyze_existing_news_file())
