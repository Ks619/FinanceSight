import pytest
from unittest.mock import patch, MagicMock

# Import utility modules from each microservice
from service_1 import utils as service1_utils
from service_2 import utils as service2_utils
from service_3 import utils as service3_utils

def test_fetch_news_multiple_feeds_per_service():
    # Define each microservice's module and corresponding fetch function
    services = [
        (service1_utils, "fetch_coindesk_cointelegraph_cryptopotato"),
        (service2_utils, "fetch_bitcoin_decrypt"),
        (service3_utils, "fetch_btc_utoday"),
    ]

    for utils_module, function_name in services:
        # Dynamically patch dependencies based on the module's name
        with patch(f"{utils_module.__name__}.feedparser.parse") as mock_parse, \
             patch(f"{utils_module.__name__}.requests.get") as mock_get, \
             patch(f"{utils_module.__name__}.Article") as mock_article_class:

            # Simulate two RSS entries from two feeds
            entry1 = MagicMock(title="News A", link="http://example.com/a", published="Yesterday")
            entry2 = MagicMock(title="News B", link="http://example.com/b", published="Today")

            # feedparser.parse is called twice – once for each feed
            mock_parse.side_effect = [
                MagicMock(entries=[entry1]),
                MagicMock(entries=[entry2])
            ]

            # Simulate a successful HTTP response for article content
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "<html>mocked</html>"

            # Simulate newspaper.Article parsing behavior
            mock_article = MagicMock()
            mock_article.text = "Simulated content"
            mock_article.set_html.return_value = None
            mock_article.parse.return_value = None
            mock_article_class.return_value = mock_article

            # Call the target function (e.g., fetch_btc_utoday)
            fetch_func = getattr(utils_module, function_name)
            result = fetch_func()

            # Validate returned article list
            assert isinstance(result, list)
            assert len(result) == 2  # Two feeds -> two articles

            # Validate structure and content
            for article in result:
                assert isinstance(article, dict)
                assert "title" in article and isinstance(article["title"], str)
                assert "link" in article and isinstance(article["link"], str)
                assert "content" in article and isinstance(article["content"], str)
                assert "published" in article
                assert "source" in article

            # Validate expected titles
            titles = [article["title"] for article in result]
            assert "News A" in titles
            assert "News B" in titles
