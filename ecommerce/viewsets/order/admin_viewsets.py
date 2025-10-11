from decimal import Decimal
from django.conf import settings
from django.utils.dateparse import parse_date
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.models.accounting.models import Account, JournalEntry, JournalEntryLine
from ecommerce.models.order.models import Order, OrderItem, Payment
from ecommerce.models.product.models import Currency, FXRate, Product, ProductPrice
from ecommerce.models.users.models import Customer
from ecommerce.permissions import IsStaff
from ecommerce.serializers import OrderWithItemsSerializer
from ecommerce.viewsets.accounting.viewsets import (
    journal_entry_when_product_is_sold_fifo,
)
from ecommerce.viewsets.order.utils import convert_price


class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    Allows admin to view, list, and retrieve orders across all customers.
    """

    serializer_class = OrderWithItemsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = (
            Order.objects.select_related("customer__user", "currency")
            .prefetch_related("items__product", "customer__addresses", "payment")
            .order_by("-created_at")
        )

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset

    @action(detail=True, methods=["get"], url_path="with-items")
    def retrieve_with_items(self, request, pk=None):
        """
        Retrieve full order with items for a given order ID.
        """
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderWithItemsSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderTotalInAccountingCurrencyView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, *args, **kwargs):
        start_date = parse_date(request.query_params.get("start_date"))
        end_date = parse_date(request.query_params.get("end_date"))

        orders = Order.objects.select_related("currency").all()

        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)

        # Build FX rate map to accounting currency
        fx_rates = FXRate.objects.filter(
            end_date__isnull=True,
            currency_to__code=settings.ACCOUNTING_CURRENCY
        ).select_related("currency_from", "currency_to")

        fx_map = {
            (fx.currency_from.code, fx.currency_to.code): Decimal(fx.rate)
            for fx in fx_rates
        }

        total_amount = Decimal("0.00")
        for order in orders:
            from_code = order.currency.code if order.currency else None
            to_code = settings.ACCOUNTING_CURRENCY
            rate = fx_map.get((from_code, to_code), Decimal("1.0") if from_code == to_code else None)

            if rate is None:
                continue  # Skip orders without a valid FX rate
            total_amount += order.total_amount * rate

        return Response({
            "amount": round(total_amount, 2),
            "currency": settings.ACCOUNTING_CURRENCY,
        })

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
