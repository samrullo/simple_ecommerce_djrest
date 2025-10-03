from rest_framework import serializers

from ecommerce.models.product.models import Product, ProductImage
from ecommerce.models.purchase.models import Purchase
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
        icon_image = ProductImage.objects.filter(
            product=obj.product, tag="icon"
        ).first()
        request = self.context.get("request")
        if icon_image and icon_image.image:
            image_url = icon_image.image.url
            if request:
                return request.build_absolute_uri(image_url)
            return image_url
        return None


class LastPurchasePriceSerializer(serializers.ModelSerializer):
    last_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    last_currency = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "last_price", "last_currency"]

    def get_last_currency(self, obj):
        from ecommerce.models import Currency

        if obj.last_currency_id:
            currency = Currency.objects.get(id=obj.last_currency_id)
            return {"id":currency.id,"code": currency.code, "name": currency.name}
        return None
