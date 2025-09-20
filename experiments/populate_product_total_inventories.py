import os
import logging
import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

logger = logging.getLogger(__name__)
from ecommerce.models.product.models import Product
from ecommerce.models.inventory.models import Inventory,ProductInventory

inventories=Inventory.objects.all()
products=Product.objects.all()

for product in products:
    product_inventories=Inventory.objects.filter(product=product).all()
    # if len(product_inventories)>1:
    #     logging.info(f"{product.name[:10]} has {len(product_inventories)} inventory records")
    total_inventory=sum([product_inventory.stock for product_inventory in product_inventories])
    prod_total_inventory,created=ProductInventory.objects.update_or_create(product=product,defaults={"total_inventory":total_inventory})
    logging.info(f"Updated or created {created} product inventory {prod_total_inventory}")