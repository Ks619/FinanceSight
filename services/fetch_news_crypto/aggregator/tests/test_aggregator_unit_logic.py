import pytest  
from unittest.mock import AsyncMock, patch  
import main  
from datetime import datetime

# Test the function that splits large text into smaller chunks
def test_split_text_into_chunks():
    # Prepare a long test string by repeating multiple lines
    text = "Line 1.\nLine 2.\nLine 3.\n" * 100

    # Call the function with a maximum chunk size of 1000 characters
    chunks = main.split_text_into_chunks(text, max_length=1000)

    # Assert the returned result is a list
    assert isinstance(chunks, list)

    # Assert that all elements in the list are strings
    assert all(isinstance(chunk, str) for chunk in chunks)

    # Ensure the total length of all chunks is at least 90% of the original text
    assert sum(len(c) for c in chunks) >= len(text) * 0.9


# Test the analyze_limited function using a mocked LLM call
@pytest.mark.asyncio  # Mark the function as an asynchronous test
async def test_analyze_limited_mocked_llm():
    test_chunk = "Bitcoin is rising due to ETF news."  # A sample news text chunk

    # Patch the analyze_with_ollama function with an async mock
    with patch("main.analyze_with_ollama", new_callable=AsyncMock) as mock_analyze:
        # Set the mocked LLM response
        mock_analyze.return_value = "LLM says: consider BTC and ETH."

        # Call the function being tested
        result = await main.analyze_limited(test_chunk)

        # Assert the LLM was called once with the correct argument
        mock_analyze.assert_awaited_once_with(test_chunk)

        # Check that the returned string includes the expected prefix
        assert "LLM says:" in result


# Full test of the orchestrate_and_save_news function with mocked services and LLM
@pytest.mark.asyncio
async def test_orchestrate_with_mocked_services_and_llm(tmp_path):
    # Define a fake response that simulates the result from one news service
    today_str = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")  # example: "Mon, 29 Jul 2025 17:40:00 +0000"
    fake_response = {
        "count": 2,
        "items": [
            {
                "title": "Bitcoin",
                "content": "BTC is up",
                "link": "...",
                "published": "today",
                "source": "url"
            },
            {
                "title": "Ethereum",
                "content": "ETH is strong",
                "link": "...",
                "published": today_str,
                "source": "url"
            }
        ]
    }

    # Patch the external dependencies used inside orchestrate_and_save_news
    with patch("main.fetch_with_retry", new_callable=AsyncMock) as mock_fetch, \
         patch("main.analyze_with_ollama", new_callable=AsyncMock) as mock_llm, \
         patch("main.Path", return_value=tmp_path):

        # Simulate that each fetch returns the fake response
        mock_fetch.return_value = fake_response

        # Simulate that the LLM returns a summary string
        mock_llm.return_value = "LLM Summary"

        # Call the function being tested
        result = await main.orchestrate_and_save_news()

        # Begin validating the structure and content of the result

        # Result must be a dictionary
        assert isinstance(result, dict)

        # It should contain expected keys
        assert "count" in result
        assert "message" in result
        assert "summary_chunks" in result

        # Check values are of the correct type and match expectations
        assert result["count"] == 6  # 2 items * 3 services = 6
        assert isinstance(result["message"], str)
        assert isinstance(result["summary_chunks"], list)
        assert len(result["summary_chunks"]) == 1
        assert result["summary_chunks"][0] == "LLM Summary"
