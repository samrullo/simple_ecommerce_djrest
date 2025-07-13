# Splitting Purchase model to Purchase and PurchaseItem models

We will change current ```Purchase``` model that represents single purchase of single item,
into ```Purchase``` and ```PurchaseItem``` models.
```Purchase``` will now represent collection of purchase items made on a certain date.
Purchase will have date field that is unique.

This change will require changes to many other parts of my code base.

# Change journal entry
Within ```journal_entries_for_direct_inventory_changes``` function there is a part where I create a pseudo purchase and associate inventory object with it.

```python
    if quantity_diff > 0:
        # Create a virtual purchase
        pseudo_purchase = Purchase.objects.create(
            product=product,
            quantity=quantity_diff,
            price_per_unit=unit_price,
            purchase_datetime=timezone.now(),
        )

```

I will need to change above code to following logic.
Find a ```Purchase``` with the current date ```purchase_date==timezone.now().date()``` and then create new ```PurchaseItem``` under that purchase and 
associate inventory with the newly created purchase item.

# Create serializers
We will have to change current Purchase serializer to match the new Purchase object.
And in addition create new PurchaseItemSerializer

# Viewsets
