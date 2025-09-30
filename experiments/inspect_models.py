import os

import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

from ecommerce.models.inventory.models import Inventory
from ecommerce.models.purchase.models import Purchase
from ecommerce.models.product.models import Product,Currency

inventories = Inventory.objects.all()
print(f"inventories : {len(inventories)}")

product_id=820
product=Product.objects.get(id=product_id)
purchases=Purchase.objects.filter(product=product).all()
print(f"{product} has {len(purchases)} purchases")