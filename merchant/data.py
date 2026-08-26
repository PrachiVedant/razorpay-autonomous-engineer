import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "merchant_data"


def load_json(filename):
    path = DATA_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_merchant():
    return load_json("merchant.json")


def get_orders():
    return load_json("orders.json")


def get_payments():
    return load_json("payments.json")


def get_products():
    return load_json("products.json")