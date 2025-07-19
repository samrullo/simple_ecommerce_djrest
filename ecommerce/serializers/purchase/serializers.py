from rest_framework import serializers

from ecommerce.models.purchase.models import Purchase
from ecommerce.models.product.models import ProductImage
from ecommerce.serializers.product.serializers import CurrencySerializer


class PurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    currency = CurrencySerializer(read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price_per_unit",
            "currency",
            "purchase_datetime",
            "created_at",
            "updated_at",
        ]

    def get_product_image(self, obj):
        icon_image = ProductImage.objects.filter(product=obj.product, tag="icon").first()
        request = self.context.get("request")
        if icon_image and icon_image.image:
            image_url = icon_image.image.url
            if request:
                return request.build_absolute_uri(image_url)
            return image_url
        return None