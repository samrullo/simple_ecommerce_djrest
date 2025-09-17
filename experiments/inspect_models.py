import os
import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

from ecommerce.models.inventory.models import Inventory
from ecommerce.models.product.models import Product,ProductImage,Currency
from ecommerce.models.purchase.models import Purchase

inventories = Inventory.objects.all()
print(f"inventories : {len(inventories)}")
