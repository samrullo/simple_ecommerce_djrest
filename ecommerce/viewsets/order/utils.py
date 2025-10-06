from decimal import Decimal
from typing import Dict, Tuple


def convert_price(
    price: float|Decimal, from_code: str, to_code: str, fx_rates: Dict[Tuple[str, str], float]
):
    """
    Convert price from one currency to another
    :param price:
    :param from_code:
    :param to_code:
    :param fx_rates:
    :return:
    """
    if from_code == to_code:
        return price
    rate = fx_rates.get((from_code, to_code))
    if not rate:
        raise ValueError(f"No FX rate from {from_code} to {to_code}")
    return price * rate
