from django.db import models

from ecommerce.models.product.models import Product


class Inventory(models.Model):
    """
    Tracks product availability.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.stock} in stock"