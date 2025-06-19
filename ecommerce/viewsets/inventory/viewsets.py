import logging
from rest_framework import viewsets
from ecommerce.serializers import InventorySerializer, PurchaseSerializer
from ecommerce.models.accounting.models import Account, JournalEntry, JournalEntryLine
from ecommerce.permissions import IsStaff
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ecommerce.permissions import IsStaff
from ecommerce.models.inventory.models import Purchase, Inventory, Product
from ecommerce.models.accounting.models import Account, JournalEntryLine
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
from django.utils import timezone


logger = logging.getLogger(__name__)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsStaff]


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all().order_by('-purchase_datetime')
    serializer_class = PurchaseSerializer
    permission_classes = [IsStaff]


class PurchaseCreateAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        try:
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity"))
            price_per_unit = Decimal(request.data.get("price_per_unit"))
            purchase_datetime = request.data.get("purchase_datetime") or timezone.now()

            with transaction.atomic():
                product = Product.objects.get(id=product_id)

                # Create Purchase record
                purchase = Purchase.objects.create(
                    product=product,
                    quantity=quantity,
                    price_per_unit=price_per_unit,
                    purchase_datetime=purchase_datetime,
                )

                # Update inventory (assumes one inventory record per product for now)
                inventory, _ = Inventory.objects.get_or_create(product=product)
                inventory.stock += quantity
                inventory.save()

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

                return Response({"message": "Purchase recorded successfully."}, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class PurchaseUpdateAPIView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, pk):
        try:
            purchase = get_object_or_404(Purchase, pk=pk)

            new_quantity = int(request.data.get("quantity", purchase.quantity))
            new_price_per_unit = Decimal(request.data.get("price_per_unit", purchase.price_per_unit))
            new_datetime = request.data.get("purchase_datetime", purchase.purchase_datetime)

            with transaction.atomic():
                # Inventory adjustment
                inventory = Inventory.objects.filter(product=purchase.product).first()
                if inventory:
                    quantity_diff = new_quantity - purchase.quantity
                    inventory.stock += quantity_diff
                    inventory.save()

                # Update purchase
                purchase.quantity = new_quantity
                purchase.price_per_unit = new_price_per_unit
                purchase.purchase_datetime = new_datetime
                purchase.save()

                # Update related journal entry lines
                total_cost = new_quantity * new_price_per_unit
                inventory_account = Account.objects.get(code="1200")
                accounts_payable = Account.objects.get(code="2000")

                journal_entry = purchase.journalentry_set.first()  # You can link Purchase ↔ JournalEntry for better tracking

                if journal_entry:
                    for line in journal_entry.lines.all():
                        if line.account == inventory_account:
                            line.debit = total_cost
                            line.description = "Inventory adjusted from purchase update"
                            line.save()
                        elif line.account == accounts_payable:
                            line.credit = total_cost
                            line.description = "Accounts Payable adjusted from purchase update"
                            line.save()

                return Response({"message": "Purchase updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)