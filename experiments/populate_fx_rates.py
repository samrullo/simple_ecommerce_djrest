import datetime
import logging
import os

import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

logger = logging.getLogger(__name__)
from ecommerce.models.product.models import Currency, FXRate

currency_codes = ["USD", "JPY", "SOM"]
usd_fx_rates = {"USD": 1.0, "JPY": 150.0, "SOM": 12400.0}

# first delete all fx rates
FXRate.objects.all().delete()

start_date = datetime.date.today()

# populate USD against other currency rates
for currency_code in usd_fx_rates:
    from_currency = Currency.objects.filter(code="USD").first()
    to_currency = Currency.objects.filter(code=currency_code).first()
    fx_rate = FXRate.objects.create(
        currency_from=from_currency,
        currency_to=to_currency,
        rate=usd_fx_rates[currency_code],
        start_date=start_date,
    )
    logger.info(f"Create fx rate : {fx_rate}")

# populate other fx rates
for from_currency_code in ["JPY", "SOM"]:
    for to_currency_code in ["USD", "JPY", "SOM"]:
        if from_currency_code == to_currency_code:
            continue
        usd_to_from_currency_fx_rate = usd_fx_rates[from_currency_code]
        usd_to_to_currency_fx_rate = usd_fx_rates[to_currency_code]
        from_to_fx_rate = (
            1 / usd_to_from_currency_fx_rate
        ) * usd_to_to_currency_fx_rate
        from_currency = Currency.objects.filter(code=from_currency_code).first()
        to_currency = Currency.objects.filter(code=to_currency_code).first()
        created_fx_rate = FXRate.objects.create(
            currency_from=from_currency,
            currency_to=to_currency,
            rate=from_to_fx_rate,
            start_date=start_date,
        )
        logger.info(f"Create fx rate : {created_fx_rate}")
