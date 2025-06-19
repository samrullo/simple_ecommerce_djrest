from rest_framework import serializers
from ecommerce.models import Inventory
from ecommerce.models.inventory.models import Purchase


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"

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