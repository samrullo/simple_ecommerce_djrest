# ERP data model for simple ecommerce

When designing an ecommerce application that serves both external customers and internal enterprise users (the owner and staff), you’ll want a data model that’s flexible, normalized, and extensible. In this setting, a **relational data model** is typically a great choice because it:

- **Ensures Data Consistency:** Transactions (orders, payments, inventory adjustments) can be managed reliably.
- **Supports Complex Relationships:** It allows you to model relationships between products, categories, orders, users, etc.
- **Facilitates Role-Based Access:** You can extend your user model to differentiate between customers and staff/administrative users.
- **Lays a Foundation for Reporting:** A normalized model can be the source for analytical queries or be fed into a separate reporting/BI layer later on.

Below is an example data model using Django’s ORM. This example covers the basics for both ecommerce transactions and enterprise data management:

---

## Example Data Model

### 1. Extend the User Model

You can extend Django’s built-in user (or use a custom user model) to include roles and additional attributes. In this example, we add a simple flag or even a profile for customers.

```python
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # A simple way to flag different user roles. 
    # In a production system, consider using Django Groups or a more advanced role system.
    is_customer = models.BooleanField(default=True)
    is_staff_member = models.BooleanField(default=False)

    def __str__(self):
        return self.username
```

### 2. Product Catalog

Products typically belong to one or more categories. Here’s an example of a product with its category relationship and basic inventory tracking:

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL
    )  # For a hierarchical category structure

    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField(Category, related_name='products')
    inventory_count = models.IntegerField(default=0)  # Basic inventory tracking

    def __str__(self):
        return self.name
```

### 3. Customer Profiles

Even if you extend the user model, you may want to keep customer-specific data (like addresses) in a separate profile model.

```python
class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
```

### 4. Orders and Order Items

The transactional part of the ecommerce system is handled via orders and their related order items:

```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(
        CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.user.username if self.customer else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of product price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
```

### 5. Payments

Track payment details associated with orders:

```python
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"
```

### 6. Enterprise Data Management Aspects

For the owner and staff, you might want to track additional business-related data such as suppliers, inventory transactions, and even staff actions. For example, a simple supplier model:

```python
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
```

And you might add an **InventoryTransaction** model to track inventory changes:

```python
class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
    ]
    product = models.ForeignKey(Product, related_name='inventory_transactions', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.quantity} for {self.product.name}"
```

---

## Summary of the Recommended Data Model

- **Core Transactional Data:**  
  - **Products & Categories:** To manage your product catalog.
  - **Orders & Order Items:** To capture customer purchases.
  - **Payments:** To track financial transactions.
  - **Inventory:** Both a field in the Product model and an InventoryTransaction model for detailed tracking.

- **User Management:**  
  - **CustomUser & CustomerProfile:** To differentiate between external customers and internal staff/administrators.

- **Enterprise Extensions:**  
  - **Suppliers:** To manage vendor relationships.
  - **Inventory Transactions:** To record all inventory changes.
  - (Additional models such as Reports, Returns, or Employee Activity could be added based on your business needs.)

This relational model provides a solid foundation for both the ecommerce storefront and the back-office enterprise data management system. It ensures that the data is well-organized, consistent, and easily extensible as your business grows and as additional enterprise functionalities (like analytics or complex reporting) are required.

Of course, depending on your exact requirements, you might adjust or extend this model further—for example, by adding more detailed product variants, promotional pricing, or integrating with external ERP systems. However, the above design represents a robust starting point for your project.


# InventoryTransaction and Inventory models
It depends on your design, but in many systems you do maintain a separate **Inventory** model (or field) that represents the current stock level for a product. The **InventoryTransaction** model typically acts as an audit log of all the changes—such as sales, restocks, or manual adjustments. When you record a new transaction, you would update the corresponding Inventory record so that it always reflects the current state.

There are two common approaches:

1. **Recalculate On Demand:**  
   You could compute the current inventory level for a product by summing all related transactions (taking into account whether each transaction adds or subtracts stock). This approach is straightforward but can be inefficient when you have a large number of transactions.

2. **Maintain a Separate Inventory Model:**  
   In this approach, you have an **Inventory** model that stores the current stock quantity for each product. Every time an **InventoryTransaction** is created, you update the related **Inventory** record accordingly. This approach offers faster lookups and can simplify the logic in other parts of your application (like displaying available stock), while still preserving a complete audit trail.

---

## Example Using a Separate Inventory Model

### The Inventory Model

```python
# models.py
from django.db import models

class Inventory(models.Model):
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
```

### The InventoryTransaction Model

Assume you already have an `InventoryTransaction` model like this:

```python
class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
    ]
    product = models.ForeignKey('Product', related_name='inventory_transactions', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()  # For a sale, this might be positive but subtracted logically
    transaction_date = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.quantity} for {self.product.name}"
```

### Updating Inventory When a Transaction Occurs

One way to update the Inventory automatically is to use Django's signals. For example, you can use the `post_save` signal to update the Inventory whenever a new InventoryTransaction is created:

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Inventory, InventoryTransaction

@receiver(post_save, sender=InventoryTransaction)
def update_inventory(sender, instance, created, **kwargs):
    if created:
        # Get or create the Inventory record for the product.
        inventory, _ = Inventory.objects.get_or_create(product=instance.product)

        # Determine the adjustment. The logic here depends on your conventions.
        # For example, for a sale you might want to subtract the quantity.
        if instance.transaction_type == 'sale':
            adjustment = -instance.quantity
        else:
            # For 'restock' and 'adjustment' we assume the quantity field reflects
            # the change to be applied (positive for adding stock, negative for subtracting).
            adjustment = instance.quantity

        # Update the inventory level.
        inventory.quantity += adjustment
        inventory.save()
```

Make sure you import and register your signals (typically in your app’s `apps.py` or `__init__.py`):

```python
# apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'your_app'

    def ready(self):
        import your_app.signals  # noqa
```

---

## Summary

- **When to Update Inventory:**  
  Every time you create a new **InventoryTransaction** (whether it's a sale, restock, or adjustment), you update the corresponding **Inventory** record. This keeps the current stock level up to date.

- **Why Maintain a Separate Inventory Model:**  
  It allows for quick lookups and simplifies business logic in other parts of your system (like displaying product availability), while still keeping a detailed log of all changes through the **InventoryTransaction** model.

- **Implementation Options:**  
  You can update the **Inventory** directly within your business logic (for example, in the view or service layer that creates the transaction) or automate it with signals as shown above.

This design pattern provides a robust approach to inventory management, ensuring that you have both a real-time view of current stock and a complete history of how that stock has changed over time.

