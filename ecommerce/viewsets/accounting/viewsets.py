from rest_framework import viewsets, permissions
from ecommerce.models.accounting.models import Account, JournalEntry, JournalEntryLine
from ecommerce.serializers.accounting.serializers import (
    AccountSerializer,
    JournalEntrySerializer,
    JournalEntryLineSerializer,
)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAdminUser]


class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAdminUser]


class JournalEntryLineViewSet(viewsets.ModelViewSet):
    queryset = JournalEntryLine.objects.all()
    serializer_class = JournalEntryLineSerializer
    permission_classes = [permissions.IsAdminUser]
