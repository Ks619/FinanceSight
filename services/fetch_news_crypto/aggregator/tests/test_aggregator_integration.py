import os
import json
import pytest
import main
from unittest.mock import patch

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

    # Patch split_text_into_chunks to return only the first 2 chunks
    original_splitter = main.split_text_into_chunks

    def limited_chunker(text: str, max_length: int = 2000):
        chunks = original_splitter(text, max_length)
        return chunks[:2]

    with patch("main.split_text_into_chunks", side_effect=limited_chunker):
        result = await main.orchestrate_and_save_news()

        # Validate result structure
        assert isinstance(result, dict)
        assert result["count"] > 0
        assert len(result["summary_chunks"]) > 0
        assert len(result["summary_chunks"]) <= 2

        # Files must be created
        assert os.path.exists(news_file), "crypto_news.json was not created"
        assert os.path.exists(summary_file), "crypto_news_analysis.txt was not created"

        # Validate news file
        with open(news_file, "r", encoding="utf-8") as f:
            news = json.load(f)
            assert isinstance(news, list)
            assert len(news) > 0

        # Validate summary
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_text = f.read()
            assert len(summary_text) > 30
