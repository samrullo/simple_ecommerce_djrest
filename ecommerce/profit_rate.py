import logging
from django.db import models
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import JSONParser
from ecommerce.models.audit_mixin import AuditMixin
from ecommerce.permissions import IsStaff,IsStaffOrReadOnly

logger=logging.getLogger(__name__)

class ProfitRate(AuditMixin):
    profit_rate = models.FloatField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.profit_rate}% from {self.start_date} to {self.end_date or 'ongoing'}"

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["profit_rate"],
                condition=models.Q(end_date__isnull=True),
                name="only_one_active_profit_rate",
            )
        ]


class ProfitRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitRate
        fields = "__all__"


class ProfitRateViewSet(ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    serializer_class = ProfitRateSerializer
    queryset = ProfitRate.objects.all()


class ActiveProfitRateView(APIView):
    def get(self, request):
        active_record = ProfitRate.objects.filter(end_date__isnull=True).first()
        if not active_record:
            return Response(
                {"detail": "No active profit rate found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProfitRateSerializer(active_record)
        return Response(serializer.data)


def create_update_profit_rate(profit_rate: float):
    """End-date the active profit rate (if any) and create a new one."""
    active_record = ProfitRate.objects.filter(end_date__isnull=True).first()
    if active_record:
        active_record.end_date = timezone.now().date()
        active_record.save()

    new_record = ProfitRate.objects.create(
        profit_rate=profit_rate,
        start_date=timezone.now().date()
    )
    return new_record


class CreateUpdateProfitRate(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsStaff]

    def post(self, request):
        # expected: { "profit_rate": 12.5 }
        try:
            logger.debug(f"Incoming data to post profit rate : {request.data}")
            profit_rate = float(request.data.get("profit_rate"))
            new_record = create_update_profit_rate(profit_rate)
            return Response(
                {"message": f"Successfully created new profit rate {new_record.profit_rate}%"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.debug(f"Error while updating profit rate : {e}")
            return Response(
                {"error": f"Error while updating profit rate {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request):
        # same as POST but idempotent for update
        try:
            logger.debug(f"Incoming data to update profit rate : {request.data}")
            profit_rate = float(request.data.get("profit_rate"))
            new_record = create_update_profit_rate(profit_rate)
            return Response(
                {"message": f"Successfully updated profit rate {new_record.profit_rate}%"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.debug(f"Error while updating profit rate : {e}")
            return Response(
                {"error": f"Error while updating profit rate {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )
