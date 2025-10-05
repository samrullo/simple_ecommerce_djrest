from django.contrib import admin

from ecommerce.models.product.models import Currency, FXRate
from ecommerce.weight_cost import WeightCost

from .models import (
    Account,
    Address,
    Brand,
    Category,
    Customer,
    Inventory,
    JournalEntry,
    JournalEntryLine,
    Order,
    OrderItem,
    Payment,
    Product,
    ProductImage,
    ProductPrice,
ProductWeight,
    ProductReview,
    Role,
    Staff,
    Tag,
    Wishlist,
)
from ecommerce.profit_rate import ProfitRate
from ecommerce.income_and_spendings.spendings import SpendingName,Spending
from ecommerce.income_and_spendings.incomes import IncomeName,Income

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "brand", "inventory_stock", "is_active"]
    search_fields = ["name", "sku"]
    list_filter = ["is_active", "category", "brand"]

    def inventory_stock(self, obj):
        # Try to fetch an Inventory record for this product
        inventory = Inventory.objects.filter(product=obj).first()
        if inventory:
            return inventory.stock
        return "N/A"  # Return N/A if no inventory record is found

    inventory_stock.short_description = "Stock"


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ["product", "price", "discount_price", "currency"]
    search_fields = ["product__name"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    search_fields = ["product__name"]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["product", "stock"]
    search_fields = ["product__name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "total_amount", "created_at"]
    search_fields = ["customer__user__username", "id"]
    list_filter = ["status", "created_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price"]
    search_fields = ["order__id", "product__name"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "method", "status", "transaction_id", "created_at"]
    search_fields = ["order__id", "transaction_id"]
    list_filter = ["method", "status"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone"]
    search_fields = ["user__username", "phone"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "street",
        "city",
        "state",
        "zip_code",
        "country",
        "is_default",
    ]
    search_fields = ["customer__user__username", "street", "city", "state"]
    list_filter = ["is_default", "country"]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "customer", "rating", "created_at"]
    search_fields = ["product__name", "customer__user__username"]
    list_filter = ["rating", "created_at"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["customer", "product", "added_at"]
    search_fields = ["customer__user__username", "product__name"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["user", "role"]
    search_fields = ["user__username", "role__name"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "parent")
    list_filter = ("account_type",)
    search_fields = ("code", "name")


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 1


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "description", "reference", "is_balanced")
    inlines = [JournalEntryLineInline]
    search_fields = ("description", "reference")
    readonly_fields = ("is_balanced",)


@admin.register(JournalEntryLine)
class JournalEntryLineAdmin(admin.ModelAdmin):
    list_display = ("journal_entry", "account", "debit", "credit", "description")
    list_filter = ("account",)
    search_fields = ("description",)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "decimal_places")
    search_fields = ("code", "name")


@admin.register(FXRate)
class FXRateAdmin(admin.ModelAdmin):
    list_display = ("currency_from", "currency_to", "rate", "start_date", "end_date")
    list_filter = ("currency_from", "currency_to", "start_date")
    search_fields = ("currency_from__code", "currency_to__code")


@admin.register(WeightCost)
class WeightCostAdmin(admin.ModelAdmin):
    pass

@admin.register(ProfitRate)
class ProfitRateAdmin(admin.ModelAdmin):
    pass

@admin.register(SpendingName)
class SpendingNameAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "modified_at", "modified_by")
    readonly_fields = ("created_at", "modified_at", "modified_by")

@admin.register(Spending)
class SpendingAdmin(admin.ModelAdmin):
    pass

@admin.register(IncomeName)
class IncomeNameAdmin(admin.ModelAdmin):
    pass

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    pass

@admin.register(ProductWeight)
class ProductWeightAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "modified_at", "modified_by")