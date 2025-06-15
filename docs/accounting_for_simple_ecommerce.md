# Accounting for simple ecommerce

Below is one approach to designing accounting-related data models for a simple ecommerce business. The goal is to record all financial events (sales, payments, refunds, cost of goods sold, inventory changes, etc.) in a way that supports a standard double-entry accounting system. In a double-entry system, every transaction is recorded in at least two accounts (one debit and one credit), ensuring that the books always balance.

Here’s a sample set of models you might use:

---

## 1. Chart of Accounts

The **Account** model represents a ledger account. Each account belongs to a category (asset, liability, equity, income, or expense), and you might allow for a hierarchical structure if needed.

```python
# models.py
from django.db import models

class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')

    def __str__(self):
        return f"{self.code} - {self.name}"
```

> **Example:**  
> - **Cash/Bank** might be an asset account.  
> - **Sales Revenue** is an income account.  
> - **Cost of Goods Sold (COGS)** is an expense account.  
> - **Accounts Receivable** is an asset account used when sales are made on credit.

---

## 2. Journal Entry and Journal Entry Lines

Each financial transaction is recorded as a **Journal Entry**, which in turn contains one or more **Journal Entry Lines** that record the individual debit and credit amounts.

### Journal Entry

```python
class JournalEntry(models.Model):
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, blank=True)  # Could be an order number, invoice ID, etc.

    def __str__(self):
        return f"Journal Entry {self.id} on {self.date}"
```

### Journal Entry Line

```python
class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, related_name='lines', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.account.name}: Debit {self.debit} / Credit {self.credit}"
```

> **Note:** The sum of debits should always equal the sum of credits in a balanced journal entry.

---

## 3. Integrating Accounting Transactions with Ecommerce Events

For many ecommerce events (for example, a sale or a payment), you would create one or more journal entries. Here are a couple of common examples:

### Sales Transaction

When a sale occurs, you might record two sets of entries:

1. **Revenue Recognition:**

   - **Debit:** Cash or Accounts Receivable (depending on whether payment is immediate or on credit)  
   - **Credit:** Sales Revenue

2. **Cost of Goods Sold (COGS):**

   - **Debit:** Cost of Goods Sold  
   - **Credit:** Inventory

For example:

```python
from decimal import Decimal

def record_sale_journal_entries(order, cash_account, receivable_account, sales_revenue_account, cogs_account, inventory_account):
    # Create a journal entry for the sale revenue
    sale_entry = JournalEntry.objects.create(
        description=f"Sale Order #{order.id}"
    )
    
    # If the payment was received immediately, debit the cash account;
    # otherwise, debit accounts receivable.
    if order.paid_in_full:
        debit_account = cash_account
    else:
        debit_account = receivable_account

    JournalEntryLine.objects.create(
        journal_entry=sale_entry,
        account=debit_account,
        debit=order.total,
        credit=Decimal('0.00'),
        description="Sale Payment"
    )
    JournalEntryLine.objects.create(
        journal_entry=sale_entry,
        account=sales_revenue_account,
        debit=Decimal('0.00'),
        credit=order.total,
        description="Sales Revenue"
    )
    
    # Create a separate journal entry for COGS if you track inventory costs:
    cogs_entry = JournalEntry.objects.create(
        description=f"COGS for Order #{order.id}"
    )
    JournalEntryLine.objects.create(
        journal_entry=cogs_entry,
        account=cogs_account,
        debit=order.cogs_amount,
        credit=Decimal('0.00'),
        description="Cost of Goods Sold"
    )
    JournalEntryLine.objects.create(
        journal_entry=cogs_entry,
        account=inventory_account,
        debit=Decimal('0.00'),
        credit=order.cogs_amount,
        description="Reduction in Inventory"
    )
```

### Payment Received

If a customer pays later (say, on credit), when the payment is received you might record:

- **Debit:** Cash/Bank  
- **Credit:** Accounts Receivable

```python
def record_payment_journal_entry(payment, cash_account, receivable_account):
    journal_entry = JournalEntry.objects.create(
        description=f"Payment for Invoice #{payment.invoice.id}"
    )
    JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        account=cash_account,
        debit=payment.amount,
        credit=Decimal('0.00'),
        description="Cash Received"
    )
    JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        account=receivable_account,
        debit=Decimal('0.00'),
        credit=payment.amount,
        description="Reduction in Receivables"
    )
```

---

## 4. Additional Considerations

- **Refunds and Returns:**  
  For a refund, you might reverse the original journal entry (or record a new one with the opposite effect).

- **Taxes, Shipping, and Discounts:**  
  Depending on the complexity of your ecommerce business, you may need additional accounts (and corresponding journal entries) for sales tax, shipping fees, discounts, and other adjustments.

- **Integration with Other Systems:**  
  If your business scales or integrates with external ERP systems, you might need to refine these models further or adopt established accounting libraries.

- **Auditing:**  
  The use of journal entries provides a clear audit trail. In production, consider using signals or transactions to ensure that your ecommerce event (order creation, payment processing, etc.) and corresponding journal entries are always in sync.

---

## Summary

A simple ecommerce accounting system can be built around these key models:

- **Account:** Represents each ledger account (e.g., Cash, Sales Revenue, COGS).  
- **JournalEntry:** Represents a complete financial transaction (or set of transactions).  
- **JournalEntryLine:** Represents individual debit/credit lines that make up the journal entry.

By mapping your ecommerce events (sales, payments, refunds, etc.) to these accounting records, you can maintain a clear, auditable financial history that aligns with standard accounting practices while keeping your system relatively straightforward.


# Inventory changes
When I increase an inventory of a product directly, it means I bought products, so I need to post purchases transactions and then increment the inventory.
When I decrease an inventory of a product directly, it means some customer bought the product, so I need to post order by an anonymous customer and then decrement the inventory.