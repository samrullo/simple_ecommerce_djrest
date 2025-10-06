from django.db import models

from ecommerce.models.product.models import Currency, Product


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Purchase cost
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    purchase_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units at {self.price_per_unit}"
