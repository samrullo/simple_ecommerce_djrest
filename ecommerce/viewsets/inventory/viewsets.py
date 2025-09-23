import logging

from rest_framework import viewsets

from ecommerce.models.inventory.models import Inventory, ProductInventory
from ecommerce.permissions import IsStaff
from ecommerce.serializers import InventorySerializer, ProductInventorySerializer

logger = logging.getLogger(__name__)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsStaff]


class ProductInventoryViewset(viewsets.ModelViewSet):
    queryset = ProductInventory.objects.all()
    serializer_class = ProductInventorySerializer
