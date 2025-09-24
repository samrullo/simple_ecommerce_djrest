import logging
from django.db import models
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import JSONParser
from ecommerce.permissions import IsStaff
from ecommerce.models.audit_mixin import AuditMixin
from ecommerce.models.product.models import Currency
from ecommerce.serializers.product.serializers import CurrencySerializer

logger = logging.getLogger(__name__)


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


def get_active_weight_cost() -> WeightCost | None:
    return WeightCost.objects.filter(end_date__isnull=True).first()


class ActiveWeightCostView(APIView):
    """
    Returns the single active WeightCost (end_date is NULL).
    """

    def get(self, request):
        active_record = get_active_weight_cost()
        if not active_record:
            return Response(
                {"detail": "No active weight cost found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = WeightCostSerializer(active_record)
        return Response(serializer.data)


def create_update_weight_cost(cost_per_kg: float, currency_id: int):
    active_record = get_active_weight_cost()
    if active_record:
        active_record.end_date = timezone.now().date()
        active_record.save()
    weight_cost_currency = Currency.objects.get(id=currency_id)
    new_record = WeightCost.objects.create(cost_per_kg=cost_per_kg,
                                           currency=weight_cost_currency,
                                           start_date=timezone.now().date())
    return new_record


class CreateUpdateWeightCost(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsStaff]

    def post(self, request):
        # we expect request.data to be dictionary with keys cost_per_kg with float value
        # and currency_id with integer value representing the currency
        try:
            logger.debug(f"Incoming data to post weight cost : {request.data}")
            cost_per_kg = float(request.data.get("cost_per_kg"))
            currency_id = int(request.data.get("currency_id"))
            new_record = create_update_weight_cost(cost_per_kg, currency_id)
            return Response({"message": f"Successfully created new weight cost {new_record}"})
        except Exception as e:
            logger.debug(f"Error while updating weight cost : {e}")
            return Response({"error": f"Error while updating weight cost {e}"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # we expect request.data to be dictionary with keys cost_per_kg with float value
        # and currency_id with integer value representing the currency
        try:
            logger.debug(f"Incoming data to post weight cost : {request.data}")
            cost_per_kg = float(request.data.get("cost_per_kg"))
            currency_id = int(request.data.get("currency_id"))
            new_record = create_update_weight_cost(cost_per_kg, currency_id)
            return Response({"message": f"Successfully created new weight cost {new_record}"})
        except Exception as e:
            logger.debug(f"Error while updating weight cost : {e}")
            return Response({"error": f"Error while updating weight cost {e}"}, status=status.HTTP_400_BAD_REQUEST)
