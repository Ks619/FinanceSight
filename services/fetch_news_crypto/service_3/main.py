from fastapi import FastAPI
from utils import fetch_btc_utoday

app = FastAPI()

@app.get("/fetch_news")
def fetch_news():
    news = fetch_btc_utoday()
    return {"count": len(news), "items": news}