from django.urls import include, path
from django.views.decorators.cache import cache_control, cache_page
from rest_framework.routers import DefaultRouter

from ecommerce.profit_rate import ActiveProfitRateView, ProfitRateViewSet,CreateUpdateProfitRate
from ecommerce.viewsets.fx_rates_viewsets import (
    ActiveFXRatesListView,
    FxRateAgainstPrimaryCcyListView,
    FXRateCreateUpdateAPIView,
)
from ecommerce.viewsets.order.admin_viewsets import (
    AdminOrderCreateAPIView,
    AdminOrderViewSet,
)
from ecommerce.viewsets.order.viewsets import OrderCreateAPIView
from ecommerce.viewsets.product.viewsets import CurrencyViewSet, FXRateViewSet
from ecommerce.viewsets.user.admin_viewsets import CustomerAdminViewSet
from ecommerce.weight_cost import ActiveWeightCostView, WeightCostViewset,CreateUpdateWeightCost

from .viewsets.accounting.viewsets import (
    AccountViewSet,
    JournalEntryLineViewSet,
    JournalEntryViewSet,
)
from .viewsets.inventory.viewsets import InventoryViewSet, ProductInventoryViewset
from .viewsets.order.viewsets import OrderItemViewSet, OrderViewSet, PaymentViewSet
from .viewsets.product.viewsets import (
    ActiveProductPriceListView,
    BrandViewSet,
    CategoryViewSet,
    ProductCreateUpdateFromCSVAPIView,
    ProductCreationAPIView,
    ProductMinimalListView,
    ProductPriceViewSet,
    ProductReviewViewSet,
    ProductUpdateAPIView,
    ProductViewSet,
    ProductWithIconImageListView,
    ProductWithImageListView,
    TagViewSet,
    WishlistViewSet,
)
from .viewsets.purchase.viewsets import (
    LastPurchasePriceViewSet,
    PurchaseCreateAPIView,
    PurchaseCreateUpdateFromCSVAPIView,
    PurchaseDetailByDateAPIView,
    PurchaseSummaryByDateAPIView,
    PurchaseUpdateAPIView,
    PurchaseViewSet,
)
from .viewsets.user.viewsets import (
    AddressViewSet,
    CustomerViewSet,
    RoleViewSet,
    StaffViewSet,
)

from ecommerce.income_and_spendings.spendings import SpendingNameViewSet,SpendingViewSet
from ecommerce.income_and_spendings.incomes import IncomeNameViewSet,IncomeViewSet
from ecommerce.viewsets.purchase_order_viewsets import AdminPurchaseAndOrderAPIView

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"currencies", CurrencyViewSet, basename="currency")
router.register(r"fxrates", FXRateViewSet, basename="fxrate")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"product-prices", ProductPriceViewSet, basename="product-price")
router.register(r"inventories", InventoryViewSet, basename="inventory")
router.register(
    r"product-total-inventories",
    ProductInventoryViewset,
    basename="product-total-inventory",
)
router.register(r"purchases", PurchaseViewSet, basename="purchase")
router.register(
    r"last-purchase-prices", LastPurchasePriceViewSet, basename="last-purchase-prices"
)
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
router.register(r"admin-orders", AdminOrderViewSet, basename="admin-orders")
router.register(r"weight-costs", WeightCostViewset, basename="weight-cost")
router.register(r"profit-rates", ProfitRateViewSet, basename="profit-rate")
router.register(r"income-names",IncomeNameViewSet,basename="income-name")
router.register(r"incomes",IncomeViewSet,basename="income")
router.register(r"spending-names",SpendingNameViewSet,basename="spending-name")
router.register(r"spendings",SpendingViewSet,basename="spending")

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/products-with-images/",
        ProductWithImageListView.as_view(),
        name="products-with-images",
    ),
    path(
        "v1/active-product-prices/",
        ActiveProductPriceListView.as_view(),
        name="active-product-prices",
    ),
    path(
        "v1/products-with-icon-image/",
        cache_control(no_cache=True)(
            cache_page(60 * 15)(ProductWithIconImageListView.as_view())
        ),
        name="products-with-icon-image",
    ),
    path(
        "v1/minimal-products/",
        ProductMinimalListView.as_view(),
        name="minimal-products",
    ),

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
    path(
        "v1/admin-create-order/",
        AdminOrderCreateAPIView.as_view(),
        name="admin-create-order",
    ),
    path("v1/active-fxrates/", ActiveFXRatesListView.as_view(), name="active-fxrates"),
    path(
        "v1/active-fxrates-against-primary-currency/",
        FxRateAgainstPrimaryCcyListView.as_view(),
        name="active-fxrates-against-primary-currency",
    ),
    path(
        "v1/create-or-update-fxrates/",
        FXRateCreateUpdateAPIView.as_view(),
        name="create-or-update-fxrates",
    ),
    path(
        "v1/active-weight-cost/",
        ActiveWeightCostView.as_view(),
        name="active-weight-cost",
    ),
    path(
        "v1/active-profit-rate/",
        ActiveProfitRateView.as_view(),
        name="active-profit-rate",
    ),
    path("v1/create-or-update-weight-cost/",CreateUpdateWeightCost.as_view(),name="create-or-update-weight-cost"),
    path("v1/create-or-update-profit-rate/",CreateUpdateProfitRate.as_view(),name="create-or-update-profit-rate"),
    path("v1/create-purchase-order/",AdminPurchaseAndOrderAPIView.as_view(),name="create-purchase-order")
]
