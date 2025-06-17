from models.crypto import MyCoins,Coin
from utils.storage import save_investments
from fastapi import FastAPI
import requests

app = FastAPI()

# endpoint
@app.post("/crypto/get_coins_prices")

def get_coins_prices(data: MyCoins):
    """
    Processes a portfolio of cryptocurrency investments, fetches real-time prices 
    from the CoinGecko API, calculates performance metrics, and saves results.

    Args:
        data (MyCoins): An object containing a list of coins, 
                        each with a 'symbol' (e.g., "bitcoin") and a 'buy_price' (float).

    Returns:
        dict: A dictionary with a single key "results", mapping to a list of result dictionaries.
              Each result contains:
                - symbol (str): The coin's symbol.
                - current_price (float): Current price in USD from CoinGecko.
                - buy_price (float): The user's recorded purchase price.
                - value_change (float): Difference between current and buy price.
                - change_pct (float): Percentage change from buy price.
              If a symbol is not found, an error message is returned instead.

    Example return:
        {
            "results": [
                {
                    "symbol": "bitcoin",
                    "current_price": 66300.0,
                    "buy_price": 47000.0,
                    "value_change": 19300.0,
                    "change_pct": 41.06
                },
                {
                    "symbol": "nonexistent",
                    "error": "Not found on CoinGecko"
                }
            ]
        }
    """
    # extract symbols from request
    symbols = [coin.symbol for coin in data.coins]
    symbols_str = ",".join(symbols)

    # fetch prices from CoinGecko
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbols_str}&vs_currencies=usd"
    response = requests.get(url)
    received_data = response.json()

    results = []

    for coin in data.coins:
        if coin.symbol not in received_data:
            results.append({
                "symbol": coin.symbol,
                "error": "Not found on CoinGecko"
            })
            continue

        current_price = received_data[coin.symbol]["usd"]
        value_change = current_price - coin.buy_price
        change_pct = ((current_price - coin.buy_price) / coin.buy_price) * 100

        results.append({
            "symbol": coin.symbol,
            "current_price": current_price,
            "buy_price": coin.buy_price,
            "value_change": round(value_change, 2),
            "change_pct": round(change_pct, 2)
        })

    
    save_investments(results)

    return {"results": results}


if __name__ == "__main__":
    
    my_coins = MyCoins(
        coins=[
            Coin(symbol="bitcoin", buy_price=47000),
            Coin(symbol="ethereum", buy_price=3100),
            Coin(symbol="cardano", buy_price=0.2)
        ]
    )

    results = get_coins_prices(my_coins)

    print("Saved results:", results)
