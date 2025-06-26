from django.db import models

from ecommerce.models.product.models import Product
from ecommerce.models.purchase.models import Purchase

class Inventory(models.Model):
    """
    Tracks inventory by purchase batch to enable FIFO-based COGS calculations.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="inventory_records")
    stock = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.name} - {self.stock} pcs from {self.purchase.purchase_datetime.strftime('%Y-%m-%d')}"