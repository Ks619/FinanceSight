from pydantic import BaseModel

class Coin(BaseModel):
    symbol: str
    buy_price: float

class MyCoins(BaseModel):
    coins: list[Coin]
