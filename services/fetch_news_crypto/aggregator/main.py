from fastapi import FastAPI
import httpx
import asyncio
import json
from pathlib import Path

SERVICES = [
    "http://service1:8000/fetch_news",
    "http://service2:8000/fetch_news",
    "http://service3:8000/fetch_news"
]

app = FastAPI()

@app.get("/get_crypto_news")
async def get_crypto_news():
    all_news = []
    timeout = httpx.Timeout(300)  

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

    # Save to file
    path = Path("received_data")
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "crypto_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)

    return {"message": f"Saved {len(all_news)} news items", "count": len(all_news)}