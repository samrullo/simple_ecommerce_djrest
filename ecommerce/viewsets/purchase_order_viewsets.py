import logging
import traceback
from decimal import Decimal
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from sampytools.list_utils import get_intersection

from ecommerce.models import (
    Currency,
    Customer,
    FXRate,
    Inventory,
    Order,
    OrderItem,
    Payment,
    Product,
    ProductPrice,
    Purchase,
)
from ecommerce.permissions import IsStaff
from ecommerce.viewsets.accounting.viewsets import (
    journal_entry_for_income_increase_when_product_sold,
    journal_entry_for_purchase_inventory_increase,
    journal_entry_when_product_is_sold_fifo,
)
from ecommerce.viewsets.order.utils import convert_price

logger = logging.getLogger(__name__)


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
                journal_entry_for_purchase_inventory_increase(product, purchase)

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
                journal_entry_for_income_increase_when_product_sold(order, customer, line_total)
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


from rest_framework import serializers


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class AdminPurchaseAndOrderFromCSVAPIView(APIView):
    """
    Allows admin to bulk create Purchases and Orders from a CSV file.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsStaff]

    def post(self, request):
        try:
            file_obj = request.FILES.get("file")
            if not file_obj:
                return Response(
                    {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
                )

            df = pd.read_csv(file_obj)

            required_cols = [
                "product_name",
                "quantity",
                "purchase_price",
                "selling_price",
            ]
            missing_cols = [c for c in required_cols if c not in df.columns]
            if missing_cols:
                return Response(
                    {"error": f"Missing required columns: {missing_cols}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            created_purchases = 0
            created_orders = 0

            # load active fx rates once
            fx_rates = {
                (fx.currency_from.id, fx.currency_to.id): fx.rate
                for fx in FXRate.objects.filter(end_date__isnull=True)
            }

            for i, row in df.iterrows():
                try:
                    with transaction.atomic():
                        # --- Product ---
                        product_name = str(row["product_name"]).strip()
                        product = Product.objects.filter(name__iexact=product_name).first()
                        if not product:
                            raise ValueError(f"Product not found: {product_name}")

                        # --- Purchase data ---
                        purchase_qty = int(row["quantity"])
                        purchase_price = Decimal(row["purchase_price"])
                        if pd.notna(row.get("purchase_currency")):
                            purchase_currency_code = str(row["purchase_currency"]).strip()
                        else:
                            purchase_currency_code = settings.ACCOUNTING_CURRENCY
                        purchase_currency = Currency.objects.filter(
                            code__iexact=purchase_currency_code
                        ).first()
                        if not purchase_currency:
                            raise ValueError(f"Invalid purchase currency: {purchase_currency_code}")

                        purchase_date = (
                            timezone.datetime.strptime(str(row["purchase_date"]), "%Y-%m-%d")
                            if "purchase_date" in row and pd.notna(row["purchase_date"])
                            else timezone.now()
                        )

                        # --- Create Purchase ---
                        purchase = Purchase.objects.create(
                            product=product,
                            quantity=purchase_qty,
                            price_per_unit=purchase_price,
                            currency=purchase_currency,
                            purchase_datetime=purchase_date,
                        )
                        Inventory.objects.create(product=product, purchase=purchase, stock=purchase_qty)
                        journal_entry_for_purchase_inventory_increase(product, purchase)
                        created_purchases += 1

                        # --- Order (if selling_price present) ---
                        if pd.notna(row.get("selling_price")):
                            # one of customer_id, customer_username, customer_email, customer_name should be present in the header
                            customer_identification_cols = ["customer_id", "customer_username", "customer_email",
                                                            "customer_name"]
                            if get_intersection(customer_identification_cols, df.columns) == 0:
                                raise ValueError(f"One of {customer_identification_cols} should be specified")

                            selling_qty = int(row["selling_quantity"]) if pd.notna(
                                row.get("selling_quantity")) else int(row["quantity"])
                            selling_price = Decimal(row["selling_price"])
                            selling_currency_code = str(row["selling_currency"]).strip() if pd.notna(
                                row.get("selling_currency")) else getattr(settings, "ACCOUNTING_CURRENCY", "JPY")
                            selling_currency = Currency.objects.filter(
                                code__iexact=selling_currency_code
                            ).first()
                            if not selling_currency:
                                raise ValueError(f"Invalid selling currency: {selling_currency_code}")

                            payment_method = (
                                str(row["payment_method"]).strip()
                                if pd.notna(row.get("payment_method"))
                                else "cash_on_delivery"
                            )
                            base_currency_code = (
                                str(row["base_currency"]).strip()
                                if pd.notna(row.get("base_currency"))
                                else getattr(settings, "ACCOUNTING_CURRENCY", "JPY")
                            )
                            base_currency = Currency.objects.filter(
                                code__iexact=base_currency_code
                            ).first()

                            # --- Customer identification ---
                            customer = None
                            if pd.notna(row.get("customer_id")):
                                customer = Customer.objects.filter(id=int(row["customer_id"])).first()
                            elif pd.notna(row.get("customer_username")):
                                customer = Customer.objects.filter(
                                    user__username=str(row["customer_username"]).strip()
                                ).first()
                            elif pd.notna(row.get("customer_email")):
                                customer = Customer.objects.filter(
                                    user__email=str(row["customer_email"]).strip()
                                ).first()
                            elif pd.notna(row.get("customer_name")):
                                name_parts = str(row["customer_name"]).strip().split()
                                if len(name_parts) >= 2:
                                    customer = Customer.objects.filter(
                                        user__first_name=name_parts[-1],
                                        user__last_name=" ".join(name_parts[:-1]),
                                    ).first()
                            if not customer:
                                raise ValueError(
                                    f"No valid customer identifier for product {product_name}"
                                )

                            # --- Update product price if needed ---
                            active_price = ProductPrice.objects.filter(
                                product=product, end_date__isnull=True
                            ).first()
                            if (
                                    not active_price
                                    or active_price.price != selling_price
                                    or active_price.currency_id != selling_currency.id
                            ):
                                if active_price:
                                    active_price.end_date = timezone.now()
                                    active_price.save()
                                ProductPrice.objects.create(
                                    product=product,
                                    price=selling_price,
                                    currency=selling_currency,
                                    begin_date=timezone.now(),
                                )

                            # --- Create order ---
                            order = Order.objects.create(
                                customer=customer,
                                status="pending",
                                total_amount=Decimal("0.00"),
                                currency=base_currency,
                            )

                            converted_price = convert_price(
                                selling_price,
                                selling_currency.id,
                                base_currency.id,
                                fx_rates,
                            )
                            line_total = converted_price * selling_qty

                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                quantity=selling_qty,
                                price=selling_price,
                                currency=selling_currency,
                            )

                            order.total_amount = line_total
                            order.save()

                            Payment.objects.create(
                                order=order,
                                method=payment_method[:20],  # truncate to avoid varchar(20) overflow
                                status="pending",
                                transaction_id=None,
                            )

                            # Accounting entries
                            journal_entry_when_product_is_sold_fifo(product, quantity_sold=selling_qty)
                            journal_entry_for_income_increase_when_product_sold(order, customer, line_total)
                            created_orders += 1

                except Exception as row_err:
                    logger.error(f"Error processing row {i}: {row_err}")
                    return Response({"error":f"Error while processing purchase order for {product} : {row_err}"},status=status.HTTP_400_BAD_REQUEST)

            return Response(
                {
                    "message": f"Processed {created_purchases} purchases and {created_orders} orders.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"CSV bulk upload failed: {e}")
            return Response(
                {"error": str(e), "trace": traceback.format_exc()},
                status=status.HTTP_400_BAD_REQUEST,
            )
