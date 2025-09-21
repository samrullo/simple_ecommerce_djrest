from django.db import models
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from django.utils import timezone
from ecommerce.models.audit_mixin import AuditMixin
from ecommerce.models.product.models import Currency
from ecommerce.serializers.product.serializers import CurrencySerializer


class WeightCost(AuditMixin):
    cost_per_kg = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.cost_per_kg} {self.currency} per kg from {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ["-start_date"]
        constraints = [models.UniqueConstraint(fields=["cost_per_kg"],
                                               condition=models.Q(end_date__isnull=True),
                                               name="only_one_active_weight_cost")]


class WeightCostSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer

    class Meta:
        model = WeightCost
        fields = "__all__"

class WeightCostViewset(ModelViewSet):
    serializer_class = WeightCostSerializer
    queryset = WeightCost.objects.all()
