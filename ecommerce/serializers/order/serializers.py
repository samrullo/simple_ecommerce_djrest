from rest_framework import serializers

from ecommerce.models import OrderItem, Order, Payment
from ecommerce.serializers.product.serializers import ProductSerializer
from ecommerce.serializers.user.serializers import CustomerSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    # Include the list of order items (read-only).
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    # Nest the order details (read-only).
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
