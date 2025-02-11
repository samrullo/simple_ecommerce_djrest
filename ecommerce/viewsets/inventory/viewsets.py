from rest_framework import viewsets, permissions

from ecommerce.models import Inventory
from ecommerce.serializers import InventorySerializer


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAdminUser]