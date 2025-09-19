from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.core.cache import cache

from ecommerce.models import Inventory, ProductInventory,Product

@receiver([post_save, post_delete], sender=Inventory)
def update_product_inventory(sender, instance, **kwargs):
    total = Inventory.objects.filter(product=instance.product).aggregate(
        total=Sum("stock")
    )["total"] or 0

    ProductInventory.objects.update_or_create(
        product=instance.product,
        defaults={"total_inventory": total}
    )

@receiver([post_save,post_delete],sender=Product)
def clear_all_cache_post_product_save(sender,**kwargs):
    cache.clear()