from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Brand, Tag, Product, ProductPrice, Inventory, Order, OrderItem,
    Payment, Customer, Address, ProductReview, Wishlist, Role, Staff
)

# ---------------------------
# 1. Core Data Models
# ---------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    # Display nested details for category, brand, and tags (read-only).
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


# ---------------------------
# 2. Customer & Address Models
# ---------------------------

class CustomerSerializer(serializers.ModelSerializer):
    # Represent the related User as a string (e.g., username).
    user = serializers.StringRelatedField()

    class Meta:
        model = Customer
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


# ---------------------------
# 3. Pricing & Inventory Models
# ---------------------------

class ProductPriceSerializer(serializers.ModelSerializer):
    # Display the product details using the nested ProductSerializer.
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductPrice
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'


# ---------------------------
# 4. Order & Payment Models
# ---------------------------

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    # Include the list of order items (read-only).
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    # Nest the order details (read-only).
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


# ---------------------------
# 5. Reviews & Wishlist
# ---------------------------

class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = '__all__'


# ---------------------------
# 6. Admin & Staff Management
# ---------------------------

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    # Represent the related user as a string.
    user = serializers.StringRelatedField()
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = '__all__'
