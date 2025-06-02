from rest_framework import serializers

from ecommerce.models import Inventory
from ecommerce.serializers.product.serializers import ProductSerializer


class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = "__all__"
