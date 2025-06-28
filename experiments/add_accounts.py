import os
import logging
import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

logger=logging.getLogger(__name__)
from ecommerce.models.accounting.models import Account

accounts_to_create=[("1200","Inventory","asset"),
                    ("2000","Account Payable","liability"),
                    ("5000","Cost Of Goods Sold","expense"),
                    ("4000","Sales Income","income"),
                    ("1000","Cash","asset")]

for account_code,account_name,account_type in accounts_to_create:
    account=Account.objects.get_or_create(code=account_code,name=account_name,account_type=account_type)
    logger.debug(f"Created account {account}")