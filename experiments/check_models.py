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

product_id=815
product = Product.objects.get(pk=product_id)
product_prices=product.price.all()
product_images=product.images.all()
pimage = product.images.first()
print(f"Product {product} has {len(product_prices)} prices and {len(product_images)} images")
print(f"product image name : {pimage.image}")
