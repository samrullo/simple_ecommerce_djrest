from django.db import models

from ecommerce.models.product.models import Product, Currency


class Order(models.Model):
    """
    Stores customer orders.
    """

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        # Assuming Customer model has a related 'user' with a username
        return f"Order {self.id} - {self.customer.user.username}"


class OrderItem(models.Model):
    """
    Links products with orders.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"OrderItem {self.product.name} - {self.quantity} pcs at price {self.price} {self.currency}"


class Payment(models.Model):
    """
    Handles payment transactions.
    """

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("paypal", "PayPal"),
        ("cash_on_delivery", "Cash on Delivery"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, default="pending")
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.method}"
