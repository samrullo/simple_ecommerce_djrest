import logging
from django.conf import settings
from decimal import Decimal

from django.utils import timezone
from rest_framework import permissions, viewsets

from ecommerce.models import (
    Account,
    Inventory,
    JournalEntry,
    JournalEntryLine,
    Product,
    ProductPrice,
)
from ecommerce.models.accounting.models import Account, JournalEntry, JournalEntryLine
from ecommerce.models.purchase.models import Purchase
from ecommerce.serializers.accounting.serializers import (
    AccountSerializer,
    JournalEntryLineSerializer,
    JournalEntrySerializer,
)

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAdminUser]


class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAdminUser]


class JournalEntryLineViewSet(viewsets.ModelViewSet):
    queryset = JournalEntryLine.objects.all()
    serializer_class = JournalEntryLineSerializer
    permission_classes = [permissions.IsAdminUser]


def journal_entries_for_direct_inventory_changes(
    product: Product,
    new_quantity: int,
    inventory_account_code: str = "1200",
    accounts_payable_account_code: str = "2000",
) -> list[Inventory]:
    """
    Adjusts inventory using new model and creates journal entries for direct inventory change.
    This function assumes a virtual purchase for direct admin inventory edits.
    :param product:
    :param new_quantity:
    :param inventory_account_code:
    :param accounts_payable_account_code:
    :return: list of Inventory objects created or adjusted
    """
    previous_quantity = sum(
        inv.stock for inv in Inventory.objects.filter(product=product)
    )
    quantity_diff = new_quantity - previous_quantity
    logger.debug(
        f"Will make changes to {product} inventory with quantity_diff {quantity_diff}, previous_quantity : {previous_quantity}, new_quantity : {new_quantity}"
    )

    if quantity_diff == 0:
        return []  # No change, nothing to do

    # Get active price
    price_obj = ProductPrice.objects.filter(
        product=product, end_date__isnull=True
    ).first()
    unit_price = price_obj.price if price_obj else Decimal("0")
    delta_value = unit_price * abs(quantity_diff)

    inventory_account = Account.objects.get(code=inventory_account_code)
    accounts_payable = Account.objects.get(code=accounts_payable_account_code)

    journal_entry = JournalEntry.objects.create(
        description=f"Direct inventory adjustment for {product.name}"
    )

    if quantity_diff > 0:
        # Create a virtual purchase
        pseudo_purchase = Purchase.objects.create(
            product=product,
            quantity=quantity_diff,
            price_per_unit=unit_price,
            currency=price_obj.currency if price_obj else settings.ACCOUNTING_CURRENCY,
            purchase_datetime=timezone.now(),
        )
        inventory_record = Inventory.objects.create(
            product=product,
            purchase=pseudo_purchase,
            stock=quantity_diff,
            location="DirectAdmin",  # You can customize or parameterize this
        )

        # Debit inventory, credit A/P
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=inventory_account,
            debit=delta_value,
            credit=0,
            description=f"Inventory added for {product.name} at a price of {product.price}",
        )
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=accounts_payable,
            debit=0,
            credit=delta_value,
            description=f"Accounts Payable for inventory increase {product.name} at a price of {product.price}",
        )
        logger.debug(f"Increased inventory of {product} by {quantity_diff}")
        return [inventory_record]

    else:
        # FIFO removal for stock decrease
        inventory_records = Inventory.objects.filter(
            product=product, stock__gt=0
        ).order_by("purchase__purchase_datetime")
        remaining_qty = abs(quantity_diff)
        removed_batches = []

        for inv_idx, inv in enumerate(inventory_records):
            if remaining_qty == 0:
                break
            logger.debug(
                f"Reducing inventory of {product} by remaining_qty {remaining_qty} by procesing inventory record {inv_idx}"
            )
            reduce_qty = min(inv.stock, remaining_qty)
            logger.debug(
                f"Actual reduce_qty for this inventory {inv_idx} will be {reduce_qty}"
            )
            cost = inv.purchase.price_per_unit * reduce_qty
            delta_value += cost

            inv.stock -= reduce_qty
            inv.save()
            remaining_qty -= reduce_qty
            removed_batches.append(inv)

            # Record journal lines per batch if needed
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=inventory_account,
                debit=0,
                credit=cost,
                description=f"Inventory decrease from batch ({inv.purchase})",
            )
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=accounts_payable,
                debit=cost,
                credit=0,
                description=f"Reversal from Accounts Payable as part of inventory descrease from batch {inv.purchase}",
            )

        if remaining_qty > 0:
            raise ValueError(
                f"Not enough inventory to reduce {abs(quantity_diff)} units of {product.name}"
            )

        return removed_batches


def journal_entry_when_product_is_sold_fifo(product: Product, quantity_sold: int):
    """
    Reduces inventory using FIFO logic and creates COGS journal entries.
    """

    inventory_batches = (
        Inventory.objects.filter(product=product, stock__gt=0)
        .select_related("purchase")
        .order_by("purchase__purchase_datetime")
    )

    inventory_account = Account.objects.get(code="1200")  # Inventory
    cogs_account = Account.objects.get(code="5000")  # Cost of Goods Sold

    remaining_qty = quantity_sold
    total_cost = Decimal("0")

    journal_entry = JournalEntry.objects.create(
        description=f"FIFO COGS for sale of {quantity_sold} x {product.name} at {product.price}"
    )

    for inventory in inventory_batches:
        if remaining_qty == 0:
            break

        take_qty = min(remaining_qty, inventory.stock)
        cost = inventory.purchase.price_per_unit * take_qty
        total_cost += cost

        # Reduce stock
        inventory.stock -= take_qty
        inventory.save()

        # Create journal lines per batch if needed
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=cogs_account,
            debit=cost,
            credit=0,
            description=f"COGS ({take_qty} units from purchase {inventory.purchase} at {inventory.purchase.price_per_unit})",
        )
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=inventory_account,
            debit=0,
            credit=cost,
            description=f"Inventory reduction (FIFO) as part of selling {take_qty} units of {inventory.purchase}",
        )

        remaining_qty -= take_qty

    if remaining_qty > 0:
        raise ValueError(f"Not enough inventory to fulfill order for {product.name}")

    return total_cost  # useful if you want to save this to the Order record
