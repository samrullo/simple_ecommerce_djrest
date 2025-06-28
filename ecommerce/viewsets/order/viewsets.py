from rest_framework import viewsets, permissions

from ecommerce.models import Order, OrderItem, Payment
from ecommerce.serializers import (
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ecommerce.models.order.models import Order, OrderItem, Payment
from ecommerce.models.product.models import Product, ProductPrice
from ecommerce.models.inventory.models import Inventory
from ecommerce.models.users.models import Customer
from ecommerce.models.accounting.models import Account
from ecommerce.viewsets.accounting.viewsets import journal_entry_when_product_is_sold_fifo
from ecommerce.models.accounting.models import JournalEntry, JournalEntryLine

# TODO : build Order react component that allows user to add products to shopping cart and sends request to create order
class OrderCreateAPIView(APIView):
    def post(self, request):
        try:
            order_items_data = request.data.get("items", [])
            payment_method = request.data.get("payment_method", "cash_on_delivery")
            user = request.user

            if not user.is_authenticated:
                return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            customer = get_object_or_404(Customer, user=user)

            with transaction.atomic():
                order = Order.objects.create(customer=customer, status="pending", total_amount=Decimal("0.00"))
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

                    line_total = active_price.price * quantity
                    total_amount += line_total

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=active_price.price
                    )

                    inventory = Inventory.objects.filter(product=product).first()
                    if not inventory or inventory.stock < quantity:
                        raise ValueError(f"Not enough inventory for product {product.name}")

                    inventory.stock -= quantity
                    inventory.save()

                    journal_lines += journal_entry_when_product_is_sold_fifo(product=product, quantity_sold=quantity)

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

                return Response({"message": "Order created successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
