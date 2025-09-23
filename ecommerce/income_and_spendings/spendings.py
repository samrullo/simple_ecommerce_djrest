from django.db import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from ecommerce.models.audit_mixin import AuditMixin
from ecommerce.models.product.models import Currency
from ecommerce.serializers.product.serializers import CurrencySerializer


class SpendingName(AuditMixin):
    """
    Defines a spending category (e.g., Travel, Office Supplies).
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Spending(AuditMixin):
    """
    Records an actual spending instance.
    """

    spending_name = models.ForeignKey(
        SpendingName, on_delete=models.CASCADE, related_name="spendings"
    )
    adate = models.DateField(default=timezone.now)  # date of spending
    amount = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return (
            f"{self.spending_name.name}: {self.amount} {self.currency} on {self.adate}"
        )


class SpendingNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingName
        fields = "__all__"


class SpendingSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.PrimaryKeyRelatedField(
        source="currency", queryset=Currency.objects.all(), write_only=True
    )

    class Meta:
        model = Spending
        fields = [
            "id",
            "spending_name",
            "adate",
            "amount",
            "currency",
            "currency_id",
            "created_at",
            "modified_at",
            "modified_by",
        ]


class SpendingNameViewSet(ModelViewSet):
    queryset = SpendingName.objects.all()
    serializer_class = SpendingNameSerializer


class SpendingViewSet(ModelViewSet):
    queryset = Spending.objects.all().select_related("spending_name", "currency")
    serializer_class = SpendingSerializer
