from django.db import models
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

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
        constraints = [
            models.UniqueConstraint(
                fields=["cost_per_kg"],
                condition=models.Q(end_date__isnull=True),
                name="only_one_active_weight_cost_global",
            )
        ]


class WeightCostSerializer(serializers.ModelSerializer):
    weight_cost_currency = serializers.SerializerMethodField()

    def get_weight_cost_currency(self, obj):
        return CurrencySerializer(obj.currency).data

    class Meta:
        model = WeightCost
        fields = "__all__"


class WeightCostViewset(ModelViewSet):
    serializer_class = WeightCostSerializer
    queryset = WeightCost.objects.all()


class ActiveWeightCostView(APIView):
    """
    Returns the single active WeightCost (end_date is NULL).
    """

    def get(self, request):
        active_record = WeightCost.objects.filter(end_date__isnull=True).first()
        if not active_record:
            return Response(
                {"detail": "No active weight cost found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = WeightCostSerializer(active_record)
        return Response(serializer.data)
