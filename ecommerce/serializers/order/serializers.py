from rest_framework import serializers
from ecommerce.models import OrderItem, Order, Payment
from ecommerce.serializers.product.serializers import (
    CurrencySerializer,
)
from ecommerce.serializers.user.serializers import CustomerSerializer,CustomerWithUserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.SerializerMethodField()
    currency = CurrencySerializer()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price",
            "currency",
        ]

    def get_product_image(self, obj):
        icon_image = obj.product.images.filter(tag="icon").first()
        if icon_image and icon_image.image and hasattr(icon_image.image, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(icon_image.image.url)
            return icon_image.image.url
        return None


class OrderWithItemsSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerWithUserSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    # Include the list of order items (read-only).
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    # Nest the order details (read-only).
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
