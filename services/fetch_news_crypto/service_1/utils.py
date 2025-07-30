from newspaper import Article
import feedparser
import requests

FEEDS = [
    # "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://cryptopotato.com/feed/",
]

def fetch_article(url):
    try:
        headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/114.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'en-US,en;q=0.9',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        article = Article(url)
        article.set_html(response.text)
        # avoid another downloading of the article
        article.is_downloaded = True
        article.parse()
        return article.text.strip()
    except Exception as e:
        print(f"Failed to fetch: {url} => {e}")
        return ""

def fetch_coindesk_cointelegraph_cryptopotato():
    items = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                content = fetch_article(entry.link)
                items.append({
                    "title": entry.title,
                    "content": content,
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "source": url
                })
        except Exception as e:
            print(f"Error parsing feed {url}: {e}")
    return items
