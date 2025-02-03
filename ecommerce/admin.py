from django.contrib import admin
from .models import (
    Category, Brand, Tag, Product, ProductPrice, Inventory, Order, OrderItem,
    Payment, Customer, Address, ProductReview, Wishlist, Role, Staff
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'brand', 'inventory_stock', 'is_active']
    search_fields = ['name', 'sku']
    list_filter = ['is_active', 'category', 'brand']

    def inventory_stock(self, obj):
        # Try to fetch an Inventory record for this product
        inventory = Inventory.objects.filter(product=obj).first()
        if inventory:
            return inventory.stock
        return "N/A"  # Return N/A if no inventory record is found

    inventory_stock.short_description = 'Stock'


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'discount_price', 'currency']
    search_fields = ['product__name']

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'stock']
    search_fields = ['product__name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'total_amount', 'created_at']
    search_fields = ['customer__user__username', 'id']
    list_filter = ['status', 'created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['order__id', 'product__name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'method', 'status', 'transaction_id', 'created_at']
    search_fields = ['order__id', 'transaction_id']
    list_filter = ['method', 'status']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']
    search_fields = ['user__username', 'phone']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'street', 'city', 'state', 'zip_code', 'country', 'is_default']
    search_fields = ['customer__user__username', 'street', 'city', 'state']
    list_filter = ['is_default', 'country']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'created_at']
    search_fields = ['product__name', 'customer__user__username']
    list_filter = ['rating', 'created_at']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'added_at']
    search_fields = ['customer__user__username', 'product__name']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    search_fields = ['user__username', 'role__name']
