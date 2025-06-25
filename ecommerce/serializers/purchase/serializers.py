from rest_framework import serializers

from ecommerce.models.purchase.models import Purchase


class PurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Purchase
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'price_per_unit',
            'purchase_datetime',
            'created_at',
            'updated_at',
        ]
