import logging
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import JSONParser
from ecommerce.permissions import IsStaff
from ecommerce.models import (
    Product, Purchase, Inventory, Order, OrderItem,
    ProductPrice, Currency, Customer, Payment,
    FXRate, Account, JournalEntry, JournalEntryLine
)
from ecommerce.viewsets.order.utils import convert_price
from ecommerce.viewsets.accounting.viewsets import (
    journal_entry_when_product_is_sold_fifo,
)

logger=logging.getLogger(__name__)


class AdminPurchaseAndOrderAPIView(APIView):
    """
    Admin creates purchase and order simultaneously via JSON payload.
    Accepts currency IDs instead of codes.
    """
    permission_classes = [IsStaff]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            data = request.data
            logger.debug(f"Incoming data for AdminPurchaseAndOrderAPIView : {data}")

            # --- Purchase inputs ---
            product_id = data.get("product_id")
            purchase_qty = int(data.get("purchase_quantity"))
            purchase_price = Decimal(data.get("purchase_price_per_unit"))
            purchase_currency_id = data.get("purchase_currency_id")
            purchase_currency = get_object_or_404(Currency, id=purchase_currency_id)
            purchase_datetime = data.get("purchase_datetime") or timezone.now()

            # --- Order inputs ---
            customer_id = data.get("customer_id")
            sold_qty = int(data.get("sold_quantity"))
            sold_price = Decimal(data.get("sold_price_per_unit"))
            sold_currency_id = data.get("sold_currency_id")
            sold_currency = get_object_or_404(Currency, id=sold_currency_id)
            payment_method = data.get("payment_method", "cash_on_delivery")
            base_currency_id = data.get("base_currency_id")
            base_currency = get_object_or_404(Currency, id=base_currency_id)

            product = get_object_or_404(Product, id=product_id)
            customer = get_object_or_404(Customer, id=customer_id)

            # active FX rates keyed by (from_id, to_id)
            fx_rates = {
                (fx.currency_from.id, fx.currency_to.id): fx.rate
                for fx in FXRate.objects.filter(end_date__isnull=True)
            }

            with transaction.atomic():
                # --- Create Purchase ---
                purchase = Purchase.objects.create(
                    product=product,
                    quantity=purchase_qty,
                    price_per_unit=purchase_price,
                    currency=purchase_currency,
                    purchase_datetime=purchase_datetime,
                )

                Inventory.objects.create(
                    product=product,
                    purchase=purchase,
                    stock=purchase_qty
                )

                inventory_account = Account.objects.get(code="1200")
                accounts_payable = Account.objects.get(code="2000")
                total_purchase_cost = purchase_price * purchase_qty

                je_purchase = JournalEntry.objects.create(
                    description=f"Purchase of {purchase_qty} {product.name}"
                )
                JournalEntryLine.objects.create(
                    journal_entry=je_purchase,
                    account=inventory_account,
                    debit=total_purchase_cost,
                    credit=0,
                    description="Inventory increase from purchase",
                )
                JournalEntryLine.objects.create(
                    journal_entry=je_purchase,
                    account=accounts_payable,
                    debit=0,
                    credit=total_purchase_cost,
                    description="Accounts Payable for purchase",
                )

                # --- Update Product Price if needed ---
                active_price = ProductPrice.objects.filter(
                    product=product, end_date__isnull=True
                ).first()

                if not active_price or active_price.price != sold_price or active_price.currency_id != sold_currency.id:
                    if active_price:
                        active_price.end_date = timezone.now()
                        active_price.save()
                    ProductPrice.objects.create(
                        product=product,
                        price=sold_price,
                        currency=sold_currency,
                        begin_date=timezone.now()
                    )

                # --- Create Order ---
                order = Order.objects.create(
                    customer=customer,
                    status="pending",
                    total_amount=Decimal("0.00"),
                    currency=base_currency,
                )

                converted_price = convert_price(
                    sold_price, sold_currency.id, base_currency.id, fx_rates
                )
                line_total = converted_price * sold_qty

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=sold_qty,
                    price=sold_price,
                    currency=sold_currency,
                )

                order.total_amount = line_total
                order.save()

                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    status="pending",
                    transaction_id=None,
                )

                # Reduce inventory / record COGS
                cost = journal_entry_when_product_is_sold_fifo(
                    product=product, quantity_sold=sold_qty
                )

                income_account = Account.objects.get(code="4000")
                cash_account = Account.objects.get(code="1000")

                je_order = JournalEntry.objects.create(
                    description=f"Admin order {order.id} for customer {customer.id}"
                )
                JournalEntryLine.objects.create(
                    journal_entry=je_order,
                    account=cash_account,
                    debit=line_total,
                    credit=0,
                    description="Cash/Receivable from customer",
                )
                JournalEntryLine.objects.create(
                    journal_entry=je_order,
                    account=income_account,
                    debit=0,
                    credit=line_total,
                    description="Sales income",
                )

                return Response(
                    {
                        "message": "Purchase and order created successfully.",
                        "purchase_id": purchase.id,
                        "order_id": order.id,
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            logger.debug(f"Error while creating purchase and order : {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
