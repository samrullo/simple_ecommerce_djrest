from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets.user.viewsets import CustomerViewSet, AddressViewSet, RoleViewSet, StaffViewSet
from .viewsets.order.viewsets import OrderViewSet, OrderItemViewSet, PaymentViewSet
from .viewsets.inventory.viewsets import InventoryViewSet
from .viewsets.product.viewsets import CategoryViewSet, BrandViewSet, TagViewSet, ProductViewSet, ProductPriceViewSet, \
    ProductReviewViewSet, WishlistViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-prices', ProductPriceViewSet, basename='product-price')
router.register(r'inventories', InventoryViewSet, basename='inventory')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'product-reviews', ProductReviewViewSet, basename='product-review')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'staff', StaffViewSet, basename='staff')

urlpatterns = [
    path('v1/ecommerce/', include(router.urls)),
]
