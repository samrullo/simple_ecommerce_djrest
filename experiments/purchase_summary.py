import os
import pandas as pd
import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from ecommerce.models import Purchase

purchases = Purchase.objects.all()
data = [
    {

        "quantity": purchase.quantity,
        "price_per_unit": float(purchase.price_per_unit),
        "currency": purchase.currency.code if purchase.currency else None,
        "purchase_date": purchase.purchase_datetime.date(),


    }
    for purchase in purchases
]

# Convert to DataFrame
from ecommerce.viewsets.utils import get_fx_rates_with_currency_codes, convert_amount_from_one_currency_code_to_another

fx_rates = get_fx_rates_with_currency_codes()
purchasedf = pd.DataFrame(data)
purchasedf["currency"]=purchasedf["currency"].fillna(settings.ACCOUNTING_CURRENCY)
purchasedf["amount"] = purchasedf["quantity"] * purchasedf["price_per_unit"]
purchasedf["amount_in_accounting_currency"] = purchasedf.apply(
    lambda row: convert_amount_from_one_currency_code_to_another(row["amount"], row["currency"],
                                                                 settings.ACCOUNTING_CURRENCY, fx_rates), axis=1)

purchase_sum_df = purchasedf.groupby("purchase_date")[["amount", "amount_in_accounting_currency"]].agg(
    {"amount": "count", "amount_in_accounting_currency": "sum"}).reset_index()
print(purchase_sum_df.head().to_string())