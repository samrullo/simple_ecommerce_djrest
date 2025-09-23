from django.db import models
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from ecommerce.models.audit_mixin import AuditMixin


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
