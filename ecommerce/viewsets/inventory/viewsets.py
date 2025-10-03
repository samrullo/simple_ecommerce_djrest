import logging

from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from ecommerce.models.inventory.models import Inventory, ProductInventory
from ecommerce.permissions import IsStaff
from ecommerce.serializers import InventorySerializer, ProductInventorySerializer

logger = logging.getLogger(__name__)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsStaff]


class ProductInventoryViewset(viewsets.ModelViewSet):
    serializer_class = ProductInventorySerializer

    def get_queryset(self):
        queryset = ProductInventory.objects.all()
        product_id=self.request.query_params.get("product_id")
        if product_id:
            queryset=queryset.filter(product=product_id)
        return queryset
