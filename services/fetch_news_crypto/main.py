from fastapi import FastAPI
from utils.storage import save_crypto_news,fetch_crypto_news


app = FastAPI(
    title="Crypto News Fetcher",
    description="Fetches the latest crypto-related news from multiple RSS sources and saves it to a single JSON file.",
    version="1.0"
)


@app.get("/get_crypto_news")
def get_crypto_news():
    """
    Endpoint to fetch crypto news and save it as a JSON file.

    - Fetches news using RSS feeds
    - Saves to 'received_data/latest_news.json'
    - Overwrites the file each time with fresh content

    Returns:
        dict: Summary of the result including file path and news count
    """
    # fetch news from multiple crypto RSS feeds
    news = fetch_crypto_news()

    # save the news data to file (overwrites previous file)
    save_crypto_news(news)

    return {
        "message": f"{len(news)} news items fetched and saved.",
        "count": len(news)
    }
