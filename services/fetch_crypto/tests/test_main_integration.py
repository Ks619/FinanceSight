import pytest
from fastapi.testclient import TestClient
from fetch_crypto.main import app

"""
Integration Test for the FastAPI endpoint /crypto/get_coins_prices.
This test sends a real HTTP POST request to the application, using real CoinGecko data.

It verifies:
- The endpoint returns status code 200
- Each coin is processed and included in the response
- Correct fields exist for valid coins
- An appropriate error is returned for an invalid coin
"""

client = TestClient(app)

def test_integration_get_prices():
    # Arrange: Input with two valid coins and one invalid
    coins = {
        "coins": [
            {"symbol": "bitcoin", "buy_price": 47000},
            {"symbol": "ethereum", "buy_price": 3000},
            {"symbol": "nonexistentcoin", "buy_price": 1}
        ]
    }

    # Act: Make the POST request to the FastAPI endpoint
    response = client.post("/crypto/get_coins_prices", json=coins)

    # Assert: Basic response structure
    assert response.status_code == 200
    data = response.json()
    results = data.get("results", [])

    # Assert: All coins are present in the result
    assert len(results) == 3

    # Extract each coin from the results
    bitcoin = next((r for r in results if r["symbol"] == "bitcoin"), None)
    ethereum = next((r for r in results if r["symbol"] == "ethereum"), None)
    invalid = next((r for r in results if r["symbol"] == "nonexistentcoin"), None)

    # Assert: All expected coins are found in the result
    assert bitcoin is not None
    assert ethereum is not None
    assert invalid is not None

    # Assert: Valid coins contain all required fields and types
    for coin in [bitcoin, ethereum]:
        assert "current_price" in coin
        assert "buy_price" in coin
        assert "value_change" in coin
        assert "change_pct" in coin
        assert isinstance(coin["value_change"], float)
        assert isinstance(coin["change_pct"], float)

    # Assert: Invalid coin returns proper error message
    assert invalid.get("error") == "Not found on CoinGecko"
