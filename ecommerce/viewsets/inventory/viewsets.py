import logging
from rest_framework import viewsets
from ecommerce.serializers import InventorySerializer
from ecommerce.permissions import IsStaff
from ecommerce.models.inventory.models import Inventory

logger = logging.getLogger(__name__)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsStaff]
