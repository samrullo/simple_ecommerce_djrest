from decimal import Decimal
from typing import Dict, Tuple
from ecommerce.models import FXRate

def convert_amount_from_one_currency_to_another(
    amount: float | Decimal, from_currency_id: int, to_currency_id: int, fx_rates: Dict[Tuple[int, int], float]
):
    """
    Convert price from one currency to another
    :param amount: amount in from_currency_id, that needs converting to to_currency_id
    :param from_currency_id:
    :param to_currency_id:
    :param fx_rates: fx rates mapping tuples of (from_currency_id, to_currency_id) to fx rates
    :return: converted amount in to_currency
    """
    if from_currency_id == to_currency_id:
        return amount
    rate = fx_rates.get((from_currency_id, to_currency_id))
    if not rate:
        raise ValueError(f"No FX rate from {from_currency_id} to {to_currency_id}")
    return amount * rate

def get_fx_rates():
    return {
        (fx.currency_from.id, fx.currency_to.id): fx.rate
        for fx in FXRate.objects.filter(end_date__isnull=True)
    }

def get_fx_rates_with_currency_codes():
    return {
        (fx.currency_from.code, fx.currency_to.code): float(fx.rate)
        for fx in FXRate.objects.filter(end_date__isnull=True)
    }

def convert_amount_from_one_currency_code_to_another(amount: float | Decimal, from_currency_code: str, to_currency_code: str, fx_rates: Dict[Tuple[str, str], float]
                                                     ):
    """
    Convert price from one currency to another
    :param amount: amount in from_currency_code, that needs converting to to_currency_code
    :param from_currency_code:
    :param to_currency_code:
    :param fx_rates: fx rates mapping tuples of (from_currency_id, to_currency_id) to fx rates
    :return: converted amount in to_currency
    """
    if from_currency_code == to_currency_code:
        return amount
    rate = fx_rates.get((from_currency_code, to_currency_code))
    if not rate:
        raise ValueError(f"No FX rate from {from_currency_code} to {to_currency_code}")
    return amount * rate