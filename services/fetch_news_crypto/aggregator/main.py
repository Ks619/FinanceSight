from fastapi import FastAPI
import httpx
import asyncio
import json
from pathlib import Path
from utils import split_text_into_chunks, analyze_with_ollama

# List of microservices that provide crypto news
SERVICES = [
    "http://service1:8000/fetch_news",
    "http://service2:8000/fetch_news",
    "http://service3:8000/fetch_news"
]

# URL and model name for Ollama LLM service
OLLAMA_URL = "http://ollama-llm:11434/api/generate"
OLLAMA_MODEL = "llama3"

# Semaphore to limit concurrent analysis requests
semaphore = asyncio.Semaphore(3)

app = FastAPI()

async def wait_for_service(url: str, retries: int = 10):
    """
    Waits for a service to become available by pinging it.

    Args:
        url (str): The service URL to check.
        retries (int): Number of retry attempts (default is 10).
    """
    for _ in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return
        except Exception:
            pass
        await asyncio.sleep(2)

async def analyze_limited(chunk: str):
    """
    Analyze a single chunk of text using the LLM with concurrency limit.

    Args:
        chunk (str): A chunk of text to analyze.

    Returns:
        str: The summary or analysis result from the LLM.
    """
    async with semaphore:
        return await analyze_with_ollama(chunk)

async def orchestrate_and_save_news():
    """
    Orchestrates the entire news retrieval and analysis process:
    - Waits for all services to be available
    - Fetches news from each service
    - Saves raw news to JSON
    - Extracts content and splits it into chunks
    - Analyzes each chunk using the LLM
    - Saves summarized results to a text file

    Returns:
        dict: Summary of the process including counts and summaries.
    """
    all_news = []
    timeout = httpx.Timeout(10000)

    # Wait for each service to become ready
    for url in SERVICES:
        await wait_for_service(url)

    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [client.get(url) for url in SERVICES]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                print("Error calling service:", repr(response))
                continue
            try:
                data = response.json()
                all_news.extend(data.get("items", []))
            except Exception as e:
                print("Error parsing response:", e)

    # Save raw news data to a file
    path = Path("received_data")
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "crypto_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)

    # Extract full article content
    full_text = "\n\n".join([item.get("content", "") for item in all_news if item.get("content")])

    # Split the content into chunks
    chunks = split_text_into_chunks(full_text)

    # Analyze each chunk with the LLM
    analysis_tasks = [analyze_limited(chunk) for chunk in chunks]
    results = await asyncio.gather(*analysis_tasks)

    # Save the analyzed summaries to a file
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
    """
    HTTP endpoint to trigger the crypto news retrieval and analysis.

    Returns:
        dict: Output from orchestrate_and_save_news().
    """
    return await orchestrate_and_save_news()
