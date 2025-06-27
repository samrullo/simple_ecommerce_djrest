from django.db import models
from django.utils import timezone
from ecommerce.models.users.models import Customer

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # e.g., 'USD', 'JPY'
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=5, blank=True, null=True)
    decimal_places = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.name})"


class FXRate(models.Model):
    currency_from = models.ForeignKey(Currency, related_name='fx_from', on_delete=models.CASCADE)
    currency_to = models.ForeignKey(Currency, related_name='fx_to', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=20, decimal_places=6)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("currency_from", "currency_to", "start_date")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.currency_from.code}/{self.currency_to.code} @ {self.rate} ({self.start_date} - {self.end_date})"


class Category(models.Model):
    """
    Helps organize products into different categories.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Brand(models.Model):
    """
    To associate products with different brands.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Used to label products (e.g., "new", "bestseller", "discount").
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Stores information about products available for sale.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)  # Stock Keeping Unit
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductPrice(models.Model):
    """
    Handles time-based pricing for a product.
    """

    product = models.ForeignKey(Product, related_name="price", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.ForeignKey(Currency,on_delete=models.SET_NULL,null=True)

    begin_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-begin_date"]  # latest first
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(end_date__isnull=True),
                name="only_one_active_price_per_product"
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.price} {self.currency} ({self.begin_date} to {self.end_date or 'ongoing'})"


class ProductReview(models.Model):
    """
    Allows customers to leave reviews.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.user.username} on {self.product.name}"


class Wishlist(models.Model):
    """
    Stores products that customers wish to buy later.
    """

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.product.name}"
