from rest_framework import serializers

from ecommerce.models import (
    Category,
    Brand,
    Tag,
    Product,
    ProductImage,
    ProductPrice,
    ProductReview,
    Wishlist,
)
from ecommerce.models.product.models import Currency, FXRate
from ecommerce.serializers.user.serializers import CustomerSerializer
from ecommerce.serializers.inventory.serializers import InventorySerializer


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class FXRateSerializer(serializers.ModelSerializer):
    currency_from = CurrencySerializer(read_only=True)
    currency_to = CurrencySerializer(read_only=True)
    currency_from_id = serializers.PrimaryKeyRelatedField(source="currency_from", queryset=Currency.objects.all(),
                                                          write_only=True)
    currency_to_id = serializers.PrimaryKeyRelatedField(source="currency_to", queryset=Currency.objects.all(),
                                                        write_only=True)

    class Meta:
        model = FXRate
        fields = ['id', 'currency_from', 'currency_to', 'rate', 'start_date', 'end_date', 'source', 'is_active',
                  'currency_from_id', 'currency_to_id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"



class ProductPriceSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = ProductPrice
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    # Display nested details for category, brand, and tags (read-only).
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    price = ProductPriceSerializer(many=True, read_only=True)
    inventory = InventorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

class ProductWithImageSerializer(serializers.ModelSerializer):
    # Display nested details for category, brand, and tags (read-only).
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    icon_images=serializers.SerializerMethodField()
    price = ProductPriceSerializer(many=True, read_only=True)
    inventory = InventorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
    def get_icon_images(self,obj):
        images=obj.images.filter(tag="icon")
        return ProductImageSerializer(images,many=True).data



class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = "__all__"


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = "__all__"
