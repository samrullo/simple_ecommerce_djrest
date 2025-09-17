from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets.user.viewsets import (
    CustomerViewSet,
    AddressViewSet,
    RoleViewSet,
    StaffViewSet,
)
from ecommerce.viewsets.user.admin_viewsets import CustomerAdminViewSet
from .viewsets.order.viewsets import OrderViewSet, OrderItemViewSet, PaymentViewSet
from .viewsets.inventory.viewsets import InventoryViewSet,ProductInventoryViewset
from .viewsets.purchase.viewsets import (
    PurchaseViewSet,
LastPurchasePriceViewSet,
    PurchaseCreateAPIView,
    PurchaseUpdateAPIView,
    PurchaseCreateUpdateFromCSVAPIView,
    PurchaseSummaryByDateAPIView,
    PurchaseDetailByDateAPIView,
)
from .viewsets.product.viewsets import (
    CategoryViewSet,
    BrandViewSet,
    TagViewSet,
    ProductViewSet,
    ProductWithImageListView,
    ProductPriceViewSet,
    ProductReviewViewSet,
    WishlistViewSet,
    ProductWithIconImageListView,
    ActiveProductPriceListView,
    ProductMinimalListView
)
from .viewsets.accounting.viewsets import (
    AccountViewSet,
    JournalEntryViewSet,
    JournalEntryLineViewSet,
)
from .viewsets.product.viewsets import (
    ProductCreationAPIView,
    ProductUpdateAPIView,
    ProductCreateUpdateFromCSVAPIView,
)
from ecommerce.viewsets.order.viewsets import OrderCreateAPIView
from ecommerce.viewsets.order.admin_viewsets import AdminOrderViewSet, AdminOrderCreateAPIView
from ecommerce.viewsets.product.viewsets import CurrencyViewSet, FXRateViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"currencies", CurrencyViewSet, basename="currency")
router.register(r"fxrates", FXRateViewSet, basename="fxrate")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"product-prices", ProductPriceViewSet, basename="product-price")
router.register(r"inventories", InventoryViewSet, basename="inventory")
router.register(r"product-total-inventories",ProductInventoryViewset,basename="product-total-inventory")
router.register(r"purchases", PurchaseViewSet, basename="purchase")
router.register(r"last-purchase-prices", LastPurchasePriceViewSet, basename="last-purchase-prices")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items", OrderItemViewSet, basename="order-item")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"addresses", AddressViewSet, basename="address")
router.register(r"product-reviews", ProductReviewViewSet, basename="product-review")
router.register(r"wishlists", WishlistViewSet, basename="wishlist")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"staff", StaffViewSet, basename="staff")
router.register(r"accounts", AccountViewSet)
router.register(r"journal-entries", JournalEntryViewSet)
router.register(r"journal-entry-lines", JournalEntryLineViewSet)
router.register(r"admin-customers", CustomerAdminViewSet, basename="admin-customer")
router.register(r'admin-orders', AdminOrderViewSet, basename='admin-orders')

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/products-with-images/",
        ProductWithImageListView.as_view(),
        name="products-with-images",
    ),
    path("v1/active-product-prices/",ActiveProductPriceListView.as_view(),name="active-product-prices"),
    path("v1/products-with-icon-image/",ProductWithIconImageListView.as_view(),name="products-with-icon-image"),
    path("v1/minimal-products/",ProductMinimalListView.as_view(),name="minimal-products"),
    path("v1/create-product/", ProductCreationAPIView.as_view(), name="create-product"),
    path(
        "v1/update-product/<int:pk>/",
        ProductUpdateAPIView.as_view(),
        name="update-product",
    ),
    path(
        "v1/create-update-products-from-csv/",
        ProductCreateUpdateFromCSVAPIView.as_view(),
        name="create_update_products_from_csv",
    ),
    path(
        "v1/purchases-summary-by-date/",
        PurchaseSummaryByDateAPIView.as_view(),
        name="purchases_summary_by_date",
    ),
    path(
        "v1/purchases-by-date/<str:purchase_date>",
        PurchaseDetailByDateAPIView.as_view(),
        name="purchases_by_date",
    ),

    path(
        "v1/create-purchase/", PurchaseCreateAPIView.as_view(), name="create-purchase"
    ),
    path(
        "v1/update-purchase/<int:pk>/",
        PurchaseUpdateAPIView.as_view(),
        name="update-purchase",
    ),
    path(
        "v1/create-update-purchases-from-csv/",
        PurchaseCreateUpdateFromCSVAPIView.as_view(),
        name="create_update_purchases_from_csv",
    ),
    path("v1/create-order/", OrderCreateAPIView.as_view(), name="create_order"),
    path("v1/admin-create-order/", AdminOrderCreateAPIView.as_view(), name="admin-create-order")

]
