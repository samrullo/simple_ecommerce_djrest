from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from decimal import Decimal
from django.shortcuts import get_object_or_404
from ecommerce.models.product.models import Currency, FXRate
from ecommerce.models.order.models import Order, OrderItem, Payment
from ecommerce.models.product.models import Product, ProductPrice
from ecommerce.models.users.models import Customer
from ecommerce.models.accounting.models import Account, JournalEntry, JournalEntryLine
from ecommerce.viewsets.accounting.viewsets import journal_entry_when_product_is_sold_fifo
from ecommerce.viewsets.order.utils import convert_price
from ecommerce.serializers import OrderWithItemsSerializer


class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    Allows admin to view, list, and retrieve orders across all customers.
    """
    queryset = Order.objects.select_related(
        "customer__user", "currency"
    ).prefetch_related("items__product", "customer__addresses", "payment")
    serializer_class = OrderWithItemsSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["get"], url_path="with-items")
    def retrieve_with_items(self, request, pk=None):
        """
        Retrieve full order with items for a given order ID.
        """
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderWithItemsSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminOrderCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            customer_id = request.data.get("customer_id")
            order_items_data = request.data.get("items", [])
            payment_method = request.data.get("payment_method", "cash_on_delivery")

            customer = get_object_or_404(Customer, id=customer_id)
            base_currency_code = request.data.get("base_currency")
            base_currency = get_object_or_404(Currency, code=base_currency_code)
            fx_rates = {
                (fx.currency_from.code, fx.currency_to.code): fx.rate
                for fx in FXRate.objects.filter(end_date__isnull=True)
            }

            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    status="pending",
                    total_amount=Decimal("0.00"),
                    currency=base_currency,
                )
                total_amount = Decimal("0.00")
                journal_lines = []

                for item_data in order_items_data:
                    product_id = item_data.get("product_id")
                    quantity = int(item_data.get("quantity", 0))
                    if quantity <= 0:
                        raise ValueError("Quantity must be positive.")

                    product = get_object_or_404(Product, id=product_id)
                    active_price = ProductPrice.objects.filter(
                        product=product, end_date__isnull=True
                    ).first()

                    if not active_price:
                        raise ValueError(f"No active price for product {product.name}")

                    converted_price = convert_price(
                        active_price.price,
                        active_price.currency.code,
                        base_currency.code,
                        fx_rates,
                    )
                    line_total = converted_price * quantity
                    total_amount += line_total

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=active_price.price,
                        currency=active_price.currency,
                    )

                    cost = journal_entry_when_product_is_sold_fifo(
                        product=product, quantity_sold=quantity
                    )

                order.total_amount = total_amount
                order.save()

                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    status="pending",
                    transaction_id=None,
                )

                income_account = Account.objects.get(code="4000")
                cash_account = Account.objects.get(code="1000")

                journal_entry = JournalEntry.objects.create(
                    description=f"Income from admin-submitted order {order.id}"
                )

                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=cash_account,
                    debit=total_amount,
                    credit=Decimal("0.00"),
                    description="Cash or receivable from admin order",
                )
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=income_account,
                    debit=Decimal("0.00"),
                    credit=total_amount,
                    description="Sales income from admin order",
                )

                for line in journal_lines:
                    line.journal_entry = journal_entry
                    line.save()

                return Response(
                    {"message": "Order created by admin.", "order_id": order.id},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
