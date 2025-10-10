import datetime
import traceback
from decimal import Decimal
from django.utils.dateparse import parse_date
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.models import (
    Account,
    Inventory,
    JournalEntry,
    JournalEntryLine,
    Product,
    Purchase,
)
from ecommerce.models.product.models import Currency
from ecommerce.permissions import IsStaff
from ecommerce.serializers.purchase.serializers import (
    LastPurchasePriceSerializer,
    PurchaseSerializer,
)


class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsStaff]

    def get_queryset(self):
        queryset = Purchase.objects.all().order_by("-purchase_datetime")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                queryset = queryset.filter(purchase_datetime__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                queryset = queryset.filter(purchase_datetime__date__lte=end_date)

        return queryset


class LastPurchasePriceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LastPurchasePriceSerializer

    def get_queryset(self):
        latest_purchase = Purchase.objects.filter(product=OuterRef("pk")).order_by(
            "-purchase_datetime"
        )

        return Product.objects.annotate(
            last_price=Subquery(latest_purchase.values("price_per_unit")[:1]),
            last_currency_id=Subquery(latest_purchase.values("currency")[:1]),
        )


class PurchaseCreateAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        try:
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity"))
            price_per_unit = Decimal(request.data.get("price_per_unit"))
            currency_code = request.data.get("currency")
            currency = Currency.objects.filter(code=currency_code).first()
            purchase_datetime = request.data.get("purchase_datetime") or timezone.now()

            with transaction.atomic():
                product = Product.objects.get(id=product_id)

                # Create Purchase record
                purchase = Purchase.objects.create(
                    product=product,
                    quantity=quantity,
                    price_per_unit=price_per_unit,
                    currency=currency,
                    purchase_datetime=purchase_datetime,
                )

                # Update inventory (assumes one inventory record per product for now)
                Inventory.objects.create(
                    product=product, purchase=purchase, stock=quantity
                )

                # Journal entries
                inventory_account = Account.objects.get(code="1200")
                accounts_payable = Account.objects.get(code="2000")
                total_cost = price_per_unit * quantity

                journal_entry = JournalEntry.objects.create(
                    description=f"Purchase of {quantity} units of {product.name}"
                )

                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=inventory_account,
                    debit=total_cost,
                    credit=0,
                    description="Inventory increase from purchase",
                )
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=accounts_payable,
                    debit=0,
                    credit=total_cost,
                    description="Accounts Payable for purchase",
                )

                return Response(
                    {"message": "Purchase recorded successfully."},
                    status=status.HTTP_201_CREATED,
                )

        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseUpdateAPIView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, pk):
        try:
            purchase = get_object_or_404(Purchase, pk=pk)

            new_quantity = int(request.data.get("quantity", purchase.quantity))
            new_price_per_unit = Decimal(
                request.data.get("price_per_unit", purchase.price_per_unit)
            )
            currency_code = request.data.get("currency")
            currency = Currency.objects.filter(code=currency_code).first()
            new_datetime = request.data.get(
                "purchase_datetime", purchase.purchase_datetime
            )

            with transaction.atomic():
                # Calculate the delta
                old_total = purchase.quantity * purchase.price_per_unit
                new_total = new_quantity * new_price_per_unit
                delta = new_total - old_total
                quantity_diff = new_quantity - purchase.quantity

                # Update inventory
                inventory = Inventory.objects.filter(
                    product=purchase.product, purchase=purchase
                ).first()
                if inventory:
                    inventory.stock += quantity_diff
                    inventory.save()

                # Update purchase
                purchase.quantity = new_quantity
                purchase.price_per_unit = new_price_per_unit
                purchase.currency = currency
                purchase.purchase_datetime = new_datetime
                purchase.save()

                # Create new journal entry to reflect the adjustment
                inventory_account = Account.objects.get(code="1200")  # Inventory
                accounts_payable = Account.objects.get(code="2000")  # Accounts Payable

                journal_entry = JournalEntry.objects.create(
                    description=f"Adjustment for purchase update #{purchase.id} {purchase}"
                )

                if delta != 0:
                    if delta > 0:
                        # Cost increased → debit inventory, credit payable
                        JournalEntryLine.objects.create(
                            journal_entry=journal_entry,
                            account=inventory_account,
                            debit=delta,
                            credit=0,
                            description="Inventory increase from purchase update",
                        )
                        JournalEntryLine.objects.create(
                            journal_entry=journal_entry,
                            account=accounts_payable,
                            debit=0,
                            credit=delta,
                            description="Accounts payable increase from purchase update",
                        )
                    else:
                        # Cost decreased → credit inventory, debit payable
                        JournalEntryLine.objects.create(
                            journal_entry=journal_entry,
                            account=inventory_account,
                            debit=0,
                            credit=abs(delta),
                            description="Inventory decrease from purchase update",
                        )
                        JournalEntryLine.objects.create(
                            journal_entry=journal_entry,
                            account=accounts_payable,
                            debit=abs(delta),
                            credit=0,
                            description="Accounts payable decrease from purchase update",
                        )

                return Response(
                    {
                        "message": "Purchase updated and adjustment journal entry recorded."
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseCreateUpdateFromCSVAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsStaff]

    def post(self, request):
        try:
            file_obj = request.FILES.get("file")
            if not file_obj:
                return Response(
                    {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
                )

            df = pd.read_csv(file_obj)
            required_cols = ["product_name", "quantity", "price_per_unit"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return Response(
                    {"error": f"Missing columns: {missing_cols}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for i, row in df.iterrows():
                with transaction.atomic():
                    product_name = row["product_name"]
                    quantity = int(row["quantity"])
                    price_per_unit = Decimal(row["price_per_unit"])
                    currency_code = row.get("currency")
                    currency_code = (
                        currency_code
                        if pd.notna(currency_code)
                        else settings.ACCOUNTING_CURRENCY
                    )
                    currency = Currency.objects.filter(code=currency_code).first()
                    purchase_date = row.get("purchase_date")
                    purchase_datetime = (
                        timezone.datetime.strptime(purchase_date, "%Y-%m-%d")
                        if pd.notna(purchase_date)
                        else timezone.now()
                    )

                    product = Product.objects.filter(name__iexact=product_name).first()
                    if not product:
                        raise ValueError(f"Product not found: {product_name}")

                    purchase = Purchase.objects.create(
                        product=product,
                        quantity=quantity,
                        price_per_unit=price_per_unit,
                        currency=currency,
                        purchase_datetime=purchase_datetime,
                    )

                    Inventory.objects.create(
                        product=product, purchase=purchase, stock=quantity
                    )

                    inventory_account = Account.objects.get(code="1200")
                    accounts_payable = Account.objects.get(code="2000")
                    total_cost = price_per_unit * quantity

                    journal_entry = JournalEntry.objects.create(
                        description=f"Bulk purchase of {quantity} {product.name}"
                    )

                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=inventory_account,
                        debit=total_cost,
                        credit=0,
                        description="Inventory increase from CSV purchase",
                    )
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=accounts_payable,
                        debit=0,
                        credit=total_cost,
                        description="Accounts Payable for CSV purchase",
                    )

            return Response(
                {"message": f"Successfully processed {len(df)} purchases."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            traceback_str = traceback.format_exc()
            return Response(
                {"error": str(e), "trace": traceback_str},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PurchaseSummaryByDateAPIView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        summary = (
            Purchase.objects.annotate(purchase_date_only=TruncDate("purchase_datetime"))
            .values("purchase_date_only")
            .annotate(num_purchases=Count("id"))
            .order_by("-purchase_date_only")
        )
        return Response(
            [
                {
                    "purchase_date": item["purchase_date_only"],
                    "num_purchases": item["num_purchases"],
                }
                for item in summary
            ]
        )


class PurchaseDetailByDateAPIView(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsStaff]

    def get_queryset(self):
        date_str = self.kwargs.get("purchase_date")
        if not date_str:
            return Purchase.objects.none()

        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Purchase.objects.none()

        return Purchase.objects.filter(purchase_datetime__date=date_obj).order_by(
            "purchase_datetime"
        )
