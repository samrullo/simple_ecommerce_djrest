from django.db import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from ecommerce.models.audit_mixin import AuditMixin
from ecommerce.models.product.models import Currency
from ecommerce.serializers.product.serializers import CurrencySerializer


class IncomeName(AuditMixin):
    """
    Defines an income category (e.g., Sales, Investment, Rental).
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Income(AuditMixin):
    """
    Records an actual income instance.
    """

    income_name = models.ForeignKey(
        IncomeName, on_delete=models.CASCADE, related_name="incomes"
    )
    adate = models.DateField(default=timezone.now)  # date of income
    amount = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.income_name.name}: {self.amount} {self.currency} on {self.adate}"


class IncomeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeName
        fields = "__all__"


class IncomeSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.PrimaryKeyRelatedField(
        source="currency", queryset=Currency.objects.all(), write_only=True
    )

    class Meta:
        model = Income
        fields = [
            "id",
            "income_name",
            "adate",
            "amount",
            "currency",
            "currency_id",
            "created_at",
            "modified_at",
            "modified_by",
        ]


class IncomeNameViewSet(ModelViewSet):
    queryset = IncomeName.objects.all()
    serializer_class = IncomeNameSerializer


class IncomeViewSet(ModelViewSet):
    queryset = Income.objects.all().select_related("income_name", "currency")
    serializer_class = IncomeSerializer