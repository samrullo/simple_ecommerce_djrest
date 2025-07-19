from rest_framework import serializers

from ecommerce.models.purchase.models import Purchase
from ecommerce.serializers.product.serializers import CurrencySerializer


class PurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price_per_unit",
            "currency",
            "purchase_datetime",
            "created_at",
            "updated_at",
        ]
