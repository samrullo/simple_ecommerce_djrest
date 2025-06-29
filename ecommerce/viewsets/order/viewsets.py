from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal
from django.shortcuts import get_object_or_404
from ecommerce.models.product.models import Currency, FXRate
from ecommerce.serializers import (
    OrderSerializer,
    OrderItemSerializer,
    OrderWithItemsSerializer,
    PaymentSerializer,
)
from ecommerce.models.order.models import Order, OrderItem, Payment
from ecommerce.models.product.models import Product, ProductPrice
from ecommerce.models.users.models import Customer
from ecommerce.models.accounting.models import Account
from ecommerce.viewsets.accounting.viewsets import journal_entry_when_product_is_sold_fifo
from ecommerce.models.accounting.models import JournalEntry, JournalEntryLine


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(customer__user=user)

    @action(detail=True, methods=["get"], url_path="with-items")
    def retrieve_with_items(self, request, pk=None):
        user = request.user
        order = get_object_or_404(Order, pk=pk)

        if not user.is_staff and not user.is_superuser and order.customer.user != user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderWithItemsSerializer(order)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]




def convert_price(price, from_code, to_code, fx_rates: dict):
    if from_code == to_code:
        return price
    rate = fx_rates.get((from_code, to_code))
    if not rate:
        raise ValueError(f"No FX rate from {from_code} to {to_code}")
    return price * rate


class OrderCreateAPIView(APIView):
    def post(self, request):
        try:
            order_items_data = request.data.get("items", [])
            payment_method = request.data.get("payment_method", "cash_on_delivery")
            user = request.user

            if not user.is_authenticated:
                return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            customer = get_object_or_404(Customer, user=user)
            base_currency_code = request.data.get("base_currency")  # e.g., "JPY"
            base_currency = get_object_or_404(Currency, code=base_currency_code)
            fx_rates = {
                (fx.currency_from.code, fx.currency_to.code): fx.rate
                for fx in FXRate.objects.filter(end_date__isnull=True)
            }

            with transaction.atomic():
                order = Order.objects.create(customer=customer, status="pending", total_amount=Decimal("0.00"),currency=base_currency)
                total_amount = Decimal("0.00")
                journal_lines = []

                for item_data in order_items_data:
                    product_id = item_data.get("product_id")
                    quantity = int(item_data.get("quantity", 0))
                    if quantity <= 0:
                        raise ValueError("Quantity must be positive.")

                    product = get_object_or_404(Product, id=product_id)
                    active_price = ProductPrice.objects.filter(product=product, end_date__isnull=True).first()

                    if not active_price:
                        raise ValueError(f"No active price found for product {product.name}")

                    converted_price = convert_price(active_price.price, active_price.currency.code, base_currency.code,
                                                    fx_rates)
                    line_total = converted_price * quantity
                    total_amount += line_total

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=active_price.price,
                        currency=active_price.currency
                    )

                    cost = journal_entry_when_product_is_sold_fifo(product=product, quantity_sold=quantity)
                    # Optionally accumulate cost if needed

                # Save total amount on order
                order.total_amount = total_amount
                order.save()

                # Create payment record
                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    status="pending",
                    transaction_id=None,
                )

                # Add income journal entry
                income_account = Account.objects.get(code="4000")  # Sales income
                cash_account = Account.objects.get(code="1000")  # Cash or receivable

                journal_entry = JournalEntry.objects.create(
                    description=f"Income from order {order.id}"
                )

                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=cash_account,
                    debit=total_amount,
                    credit=Decimal("0.00"),
                    description="Cash or receivable from sale"
                )
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=income_account,
                    debit=Decimal("0.00"),
                    credit=total_amount,
                    description="Sales income"
                )

                # Save journal lines from inventory changes
                for line in journal_lines:
                    line.journal_entry = journal_entry
                    line.save()

                return Response({"message": "Order created successfully.", "order_id": order.id},
                                status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
