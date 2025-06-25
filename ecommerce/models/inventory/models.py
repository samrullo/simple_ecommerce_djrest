from django.db import models

from ecommerce.models.product.models import Product


class Inventory(models.Model):
    """
    Tracks product availability.
    """

    product = models.ForeignKey(Product,related_name="inventory", on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.name} - {self.stock} in stock"
