import pytest
from unittest.mock import patch, MagicMock
from fetch_crypto.main import get_coins_prices
from fetch_crypto.models.crypto import MyCoins, Coin

"""
Unit Test for the main business logic.
Mocks the external API (CoinGecko) and the storage layer.
Ensures correct computation of value_change and change_pct,
and fallback behavior for invalid symbols.
"""

@patch("fetch_crypto.main.save_investments")
@patch("fetch_crypto.main.requests.get")
def test_get_coins_prices_logic(mock_requests, mock_save):
    # Arrange
    coins = MyCoins(coins=[
        Coin(symbol="bitcoin", buy_price=47000),
        Coin(symbol="invalidcoin", buy_price=1000)
    ])
    
    # Fake response from CoinGecko
    mock_requests.return_value = MagicMock(status_code=200)
    mock_requests.return_value.json.return_value = {
        "bitcoin": {"usd": 66300}
    }

    # Act
    result = get_coins_prices(coins)

    # Assert
    expected = {
        "results": [
            {
                "symbol": "bitcoin", # symbol – The coin's symbol
                "current_price": 66300, # The mocked current price returned from the API
                "buy_price": 47000, # The original buy price (input)
                "value_change": 19300.0, # Difference between current and buy price: 66300 - 47000
                "change_pct": 41.06 # Percentage change: ((66300 - 47000) / 47000) * 100
            },
            {
                "symbol": "invalidcoin",
                "error": "Not found on CoinGecko"
            }
        ]
    }

    assert result == expected
    mock_save.assert_called_once_with(expected["results"])
