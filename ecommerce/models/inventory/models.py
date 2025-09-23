from django.db import models

from ecommerce.models.product.models import Product
from ecommerce.models.purchase.models import Purchase


class Inventory(models.Model):
    """
    Tracks inventory by purchase batch to enable FIFO-based COGS calculations.
    """

    product = models.ForeignKey(
        Product, related_name="inventory", on_delete=models.CASCADE
    )
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="inventory_records"
    )
    stock = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.name} - {self.stock} pcs from {self.purchase.purchase_datetime.strftime('%Y-%m-%d')}"


class ProductInventory(models.Model):
    """
    Stores total inventory of each product. This will be used to efficiently fetch product inventories
    """

    product = models.ForeignKey(
        Product, related_name="total_inventory", on_delete=models.CASCADE
    )
    total_inventory = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} total inventory : {self.total_inventory}"
