# Product prices in different currencies
My products will have their prices recorded in ProductPrice table.
Their prices can be denominated in different currencies.
So I will need to convert their prices into a common base currency that customer chooses.
In Product page, I can introduce Base Currency dropdown that will have accounting currency selected by default.
I will pull list of currencies from Currency viewset.
I will also pull fxrates that will have structure like below

```json
{
        "id": 1,
        "currency_from": {
            "id": 1,
            "code": "USD",
            "name": "US Dollars",
            "symbol": null,
            "decimal_places": 2,
            "is_active": true
        },
        "currency_to": {
            "id": 2,
            "code": "JPY",
            "name": "Japanese Yen",
            "symbol": null,
            "decimal_places": 2,
            "is_active": true
        },
        "rate": "145.000000",
        "start_date": "2025-06-27",
        "end_date": null,
        "source": null,
        "is_active": true
    },
```
I will pull active fx rates by querying records where end_date is null
In my react component I will simplify fx rate object to have structure as following

```json
{
  "currency_from": "USD",
  "currency_to": "JPY",
  "rate": 145.00
}
```
I will introduce a column named `price_in_base_currency` that I will calculate product prices in base currency.
Perhaps, I should make currency drop down an App Context variable, but not too sure about it.

When saving order total sum, I will most probably save it in the base currency that customer chose.
But when making journal entries, I will have to convert total sum into accounting currency.

Anyways for now I introduced currency field both for Order and OrderItem tables

```python
class Order(models.Model):
    """
    Stores customer orders.
    """

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        # Assuming Customer model has a related 'user' with a username
        return f"Order {self.id} - {self.customer.user.username}"


class OrderItem(models.Model):
    """
    Links products with orders.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"OrderItem {self.product.name} - {self.quantity} pcs at price {self.price} {self.currency}"


```

# Shopping cart total sum in base currency
When customer adds products to shopping cart, the app should calculate sums per product in base currency 
and calculate total sum in base currency.
Then customer will proceed to actually place the order by choosing payment method.
Then backend order create apiview will create order and corresponding order items using following viewset

```python
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

```