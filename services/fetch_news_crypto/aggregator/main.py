from fastapi import FastAPI
import httpx
import asyncio
import json
from pathlib import Path
from utils import split_text_into_chunks, analyze_with_ollama
import os
from datetime import datetime, timezone


# List of microservices that provide crypto news
SERVICES = [
    os.getenv("SERVICE_1_URL", "http://service1:8000/fetch_news"),
    os.getenv("SERVICE_2_URL", "http://service2:8000/fetch_news"),
    os.getenv("SERVICE_3_URL", "http://service3:8000/fetch_news")
]

# URL and model name for Ollama LLM service
OLLAMA_URL = os.getenv("OLLAMA_API", "http://ollama:11434") + "/api/generate"
OLLAMA_MODEL = "llama3"

# Semaphore to limit concurrent analysis requests
semaphore = asyncio.Semaphore(1)

app = FastAPI()

def is_published_today(published_str: str) -> bool:
    try:
        # example: "Mon, 28 Jul 2025 20:23:43 +0100"
        published_dt = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %z")
        today = datetime.now(published_dt.tzinfo).date()
        return published_dt.date() == today
    except Exception as e:
        print(f"[!] Failed to parse published date: {published_str} | {e}")
        return False


async def fetch_with_retry(url: str, retries: int = 5, delay: float = 5.0):
    """Try to fetch data from a service with retries on failure."""
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
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

    # Filter today's news only
    today_news = [item for item in all_news if is_published_today(item.get("published", ""))]

    if not today_news:
        print("No news published today.")
        return {"message": "No news published today.", "count": 0}

    # Save the news to a JSON file
    path = Path("received_data")
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "crypto_news.json", "w", encoding="utf-8") as f:
        json.dump(today_news, f, ensure_ascii=False, indent=4)

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

if __name__ == "__main__":
    asyncio.run(orchestrate_and_save_news())
