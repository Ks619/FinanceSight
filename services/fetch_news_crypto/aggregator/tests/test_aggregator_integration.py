import os
import json
import pytest
import main

@pytest.mark.integration
@pytest.mark.asyncio
async def test_orchestrate_and_save_news_integration():
    """
    Integration test for the full orchestrator.
    - Executes orchestrate_and_save_news without mocking.
    - Verifies that output files are created.
    - Validates the contents of the output.
    """
    news_file = "received_data/crypto_news.json"
    summary_file = "received_data/crypto_news_analysis.txt"

    try:
        result = await main.orchestrate_and_save_news()

        # Validate structure of the result
        assert isinstance(result, dict)
        assert result["count"] > 0
        assert len(result["summary_chunks"]) > 0

        # Check that files were created
        assert os.path.exists(news_file), "crypto_news.json was not created"
        assert os.path.exists(summary_file), "crypto_news_analysis.txt was not created"

        # Validate JSON file content
        with open(news_file, "r", encoding="utf-8") as f:
            news = json.load(f)
            assert isinstance(news, list), "Expected a list of items in crypto_news.json"
            assert len(news) > 0, "News list is empty"

        # Validate summary content
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_text = f.read()
            assert len(summary_text) > 30

    finally:
        # Clean up the created files after the test (if they exist)
        if os.path.exists(news_file):
            os.remove(news_file)
        if os.path.exists(summary_file):
            os.remove(summary_file)
