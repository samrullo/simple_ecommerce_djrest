from rest_framework import serializers

from ecommerce.models import (
    Category,
    Brand,
    Tag,
    Product,
    ProductPrice,
    ProductReview,
    Wishlist,
)
from ecommerce.serializers.user.serializers import CustomerSerializer


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


class ProductSerializer(serializers.ModelSerializer):
    # Display nested details for category, brand, and tags (read-only).
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductPriceSerializer(serializers.ModelSerializer):
    # Display the product details using the nested ProductSerializer.
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductPrice
        fields = "__all__"


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
