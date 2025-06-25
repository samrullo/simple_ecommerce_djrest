from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.models import Product, Inventory, Account, JournalEntry, JournalEntryLine
from ecommerce.models.purchase.models import Purchase
from ecommerce.permissions import IsStaff
from ecommerce.serializers.purchase.serializers import PurchaseSerializer


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
                # Calculate the delta
                old_total = purchase.quantity * purchase.price_per_unit
                new_total = new_quantity * new_price_per_unit
                delta = new_total - old_total
                quantity_diff = new_quantity - purchase.quantity

                # Update inventory
                inventory = Inventory.objects.filter(product=purchase.product).first()
                if inventory:
                    inventory.stock += quantity_diff
                    inventory.save()

                # Update purchase
                purchase.quantity = new_quantity
                purchase.price_per_unit = new_price_per_unit
                purchase.purchase_datetime = new_datetime
                purchase.save()

                # Create new journal entry to reflect the adjustment
                inventory_account = Account.objects.get(code="1200")      # Inventory
                accounts_payable = Account.objects.get(code="2000")       # Accounts Payable

                journal_entry = JournalEntry.objects.create(
                    description=f"Adjustment for purchase update #{purchase.id}"
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

                return Response({"message": "Purchase updated and adjustment journal entry recorded."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)