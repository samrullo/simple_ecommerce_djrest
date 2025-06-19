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


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)  # Purchase cost
    purchase_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs at {self.price_per_unit}"