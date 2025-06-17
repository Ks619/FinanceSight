import json
from pathlib import Path
import feedparser
from newspaper import Article
import requests

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://cryptopotato.com/feed/",
    "https://news.bitcoin.com/feed/",
    "https://decrypt.co/feed",
    "https://www.newsbtc.com/feed/",
    "https://cryptonews.com/news/feed",
    "https://u.today/rss"
]

def fetch_full_article(url):
    """
    Fetches the full text of a news article from a given URL.

    Args:
        url (str): The URL of the article.

    Returns:
        str: The full text of the article if successfully fetched and parsed, 
                otherwise an empty string.
    """
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/114.0.0.0 Safari/537.36'
            )
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        article = Article(url)
        article.set_html(response.text)
        article.parse()

        return article.text.strip()

    except Exception as e:
        print(f"Failed to fetch full article from {url}: {e}")
        return ""


def fetch_crypto_news():
    """
    Parses multiple RSS feeds, fetches each article's full content, and builds a list of news items.

    Returns:
        list[dict]: A list of dictionaries, each representing a crypto news article
                    with title, content, link, published date, and source URL.
    """
    news_items = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                article_url = entry.get("link", "")
                full_text = ""

                if article_url:
                    full_text = fetch_full_article(article_url)

                news_items.append({
                    "title": entry.get("title", ""),
                    "content": full_text,
                    "link": article_url,
                    "published": entry.get("published", ""),
                    "source": feed_url
                })
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")

    return news_items

def load_crypto_news(filepath="received_data/crypto_news.json"):
    """
    Loads saved crypto news data from a JSON file.

    Args:
        filepath (str): Path to the JSON file. Defaults to 'received_data/crypto_news.json'.

    Returns:
        list[dict]: A list of previously saved news items, or an empty list if file not found.
    """
    path = Path(filepath)

    if not path.exists():
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_crypto_news(coin_list, filepath="received_data/crypto_news.json"):
    """
    Saves the given list of crypto news items to a JSON file.
    If a previous file exists, it will be deleted before writing the new data.

    Args:
        coin_list (list[dict]): A list of dictionaries representing crypto news articles.
        filepath (str): Path where the data should be saved. Defaults to 'received_data/crypto_news.json'.

    Returns:
        None
    """
    path = Path(filepath)
    
    # create directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # delete old file if it exists
    if path.exists():
        path.unlink()

    # save new data
    with open(path, "w", encoding="utf-8") as f:
        json.dump(coin_list, f, indent=4, ensure_ascii=False)

    print(f"Overwritten: {filepath}")