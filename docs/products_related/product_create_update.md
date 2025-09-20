# Product create or update

## How product price created or updated
I use below function to close existing active price by setting end date to today
and creating new record with start date today and end date null

```python
def add_or_update_product_price(
    product: Product, price: str | int | float, currency_code: str
):
    """
    Close current active price and create a new active price record.
    """
    try:
        currency_obj = Currency.objects.filter(code=currency_code).first()
        new_price = Decimal(price)
        today = timezone.now().date()

        # Find the current active price
        active_price = ProductPrice.objects.filter(
            product=product, end_date__isnull=True
        ).first()

        if active_price:
            # Close the old active price
            active_price.end_date = today
            active_price.save()

        # Create new active price
        ProductPrice.objects.create(
            product=product,
            price=new_price,
            currency=currency_obj,
            begin_date=today,
            end_date=None,
        )

    except Exception as e:
        logger.debug(f"Price update error: {e}")

```