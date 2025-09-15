from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

from ecommerce.models import Inventory, ProductInventory

@receiver([post_save, post_delete], sender=Inventory)
def update_product_inventory(sender, instance, **kwargs):
    total = Inventory.objects.filter(product=instance.product).aggregate(
        total=Sum("stock")
    )["total"] or 0

    ProductInventory.objects.update_or_create(
        product=instance.product,
        defaults={"total_inventory": total}
    )

