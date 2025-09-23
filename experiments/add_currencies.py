import logging
import os

import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

logger = logging.getLogger(__name__)
from ecommerce.models.product.models import Currency, FXRate

currencies_to_create = [
    ("USD", "US Dollars"),
    ("JPY", "Japanese Yen"),
    ("SOM", "Uzbek Som"),
]

for currency_code, currency_name in currencies_to_create:
    currency = Currency.objects.create(code=currency_code, name=currency_name)
    logger.debug(f"Create currency {currency}")

usd_currency = Currency.objects.filter(code="USD").first()
jpy_currency = Currency.objects.filter(code="JPY").first()
som_currency = Currency.objects.filter(code="SOM").first()
import datetime

start_date = datetime.date.today()
usd_jpy_fxrate = FXRate.objects.create(
    currency_from=usd_currency,
    currency_to=jpy_currency,
    rate=145.00,
    start_date=start_date,
)
logger.debug(f"Created fx rate {usd_jpy_fxrate}")
usd_som_fxrate = FXRate.objects.create(
    currency_from=usd_currency,
    currency_to=som_currency,
    rate=12581.00,
    start_date=start_date,
)
logger.debug(f"Created fx rate {usd_som_fxrate}")
