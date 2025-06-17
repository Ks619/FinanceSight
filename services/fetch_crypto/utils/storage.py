import json
from pathlib import Path


def load_investments(filepath="received_data/my_coins.json"):
    """
    Loads previously saved cryptocurrency investment data from a JSON file.
    If the file does not exist, an empty list is returned instead.

    Args:
        filepath (str, optional): Path to the JSON file containing investment data.
                                  Defaults to 'received_data/my_coins.json'.

    Returns:
        list: A list of investment records if the file exists and is valid JSON.
              Returns an empty list if the file does not exist.
    """
    path = Path(filepath)

    if not path.exists():
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_investments(coin_list, filepath="received_data/my_coins.json"):
    """
    Saves a list of cryptocurrency investment records to a JSON file.
    If a previous file exists, it is deleted and replaced with the new content.

    Args:
        coin_list (list): A list of dictionaries, each representing a coin investment.
                          Example:
                          [
                              {
                                  "symbol": "bitcoin",
                                  "buy_price": 47000,
                                  "current_price": 66000,
                                  "value_change": 19000,
                                  "change_pct": 40.43
                              },
                              ...
                          ]
        filepath (str, optional): The path to the JSON file to save the data into.
                                  Defaults to 'received_data/my_coins.json'.
    """
    path = Path(filepath)
    
    # create directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # delete old file if it exists
    if path.exists():
        path.unlink()

    # save new data
    with open(path, "w", encoding="utf-8") as f:
        json.dump(coin_list, f, indent=4, ensure_ascii=False)
    
    print(f"Overwritten: {filepath}")