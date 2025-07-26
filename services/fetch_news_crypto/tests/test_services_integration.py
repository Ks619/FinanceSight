import pytest

# Import the actual fetch functions from each microservice
from service_1.utils import fetch_coindesk_cointelegraph_cryptopotato
from service_2.utils import fetch_bitcoin_decrypt
from service_3.utils import fetch_btc_utoday

@pytest.mark.integration
@pytest.mark.parametrize("fetch_function", [
    fetch_coindesk_cointelegraph_cryptopotato,
    fetch_bitcoin_decrypt,
    fetch_btc_utoday,
])
def test_fetch_news_integration(fetch_function):
    # Call the function directly – performs real HTTP and RSS parsing
    articles = fetch_function()

    # Validate the result is a list (can be empty if no articles available)
    assert isinstance(articles, list)
    assert len(articles) >= 0

    for article in articles:
        # Ensure each article is a dict with required fields
        assert isinstance(article, dict)
        assert "title" in article and isinstance(article["title"], str)
        assert "link" in article and isinstance(article["link"], str)
        assert "content" in article and isinstance(article["content"], str)
        assert "published" in article
        assert "source" in article
