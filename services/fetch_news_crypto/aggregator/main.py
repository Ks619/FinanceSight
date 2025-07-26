from fastapi import FastAPI
import httpx
import asyncio
import json
from pathlib import Path
from utils import split_text_into_chunks, analyze_with_ollama
import os

# List of microservices that provide crypto news
SERVICES = [
    os.getenv("SERVICE_1_URL", "http://service1:8000/fetch_news"),
    os.getenv("SERVICE_2_URL", "http://service2:8000/fetch_news"),
    os.getenv("SERVICE_3_URL", "http://service3:8000/fetch_news")
]

# URL and model name for Ollama LLM service
OLLAMA_URL = os.getenv("OLLAMA_API", "http://ollama-llm:11434/api/generate")
OLLAMA_MODEL = "llama3"

# Semaphore to limit concurrent analysis requests
semaphore = asyncio.Semaphore(3)

app = FastAPI()

async def fetch_with_retry(url: str, retries: int = 5, delay: float = 5.0):
    """Try to fetch data from a service with retries on failure."""
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            print(f"[{url}] Attempt {attempt} failed: HTTP {e.response.status_code} - {e}")
        except Exception as e:
            print(f"[{url}] Attempt {attempt} failed: {repr(e)}")
        if attempt < retries:
            await asyncio.sleep(delay)
        else:
            print(f"[{url}] Failed after {retries} attempts.")
            return {"items": []}

async def analyze_limited(chunk: str):
    async with semaphore:
        return await analyze_with_ollama(chunk)

async def orchestrate_and_save_news():
    all_news = []

    # Fetch from services with retry
    fetch_tasks = [fetch_with_retry(url) for url in SERVICES]
    responses = await asyncio.gather(*fetch_tasks)

    for data in responses:
        all_news.extend(data.get("items", []))

    # Save the news to a JSON file
    path = Path("received_data")
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "crypto_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)

    # Analyze news content
    full_text = "\n\n".join([item.get("content", "") for item in all_news if item.get("content")])
    chunks = split_text_into_chunks(full_text)
    analysis_tasks = [analyze_limited(chunk) for chunk in chunks]
    results = await asyncio.gather(*analysis_tasks)

    with open(path / "crypto_news_analysis.txt", "w", encoding="utf-8") as f:
        for i, summary in enumerate(results):
            f.write(f"\n--- Chunk {i+1} ---\n{summary}\n")

    return {
        "message": f"Saved {len(all_news)} news items and analyzed {len(chunks)} chunks",
        "count": len(all_news),
        "summary_chunks": results
    }

@app.get("/get_crypto_news")
async def get_crypto_news():
    return await orchestrate_and_save_news()
