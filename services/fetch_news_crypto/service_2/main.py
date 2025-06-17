from fastapi import FastAPI
from utils import fetch_bitcoin_decrypt

app = FastAPI()

@app.get("/fetch_news")
def fetch_news():
    news = fetch_bitcoin_decrypt()
    return {"count": len(news), "items": news}