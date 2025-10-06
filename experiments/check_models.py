import os

import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

from django.contrib.auth import get_user_model

from ecommerce.models.inventory.models import Inventory
from ecommerce.models.product.models import Product, ProductImage

User=get_user_model()

inventories = Inventory.objects.all()
print(f"inventories : {len(inventories)}")

product = Product.objects.get(pk=2)
pimage = ProductImage.objects.filter(product=product).first()
print(f"product image name : {pimage.image}")
